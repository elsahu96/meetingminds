"""SurrealDB vector store integration for LangChain.

This module provides a VectorStore implementation backed by SurrealDB,
using SurrealDB's native HNSW (Hierarchical Navigable Small World) vector
index and KNN operator for approximate nearest-neighbour search.

It mirrors the interface conventions of ``langchain_mongodb.MongoDBAtlasVectorSearch``
and complies with the LangChain open-source integration guide at
https://docs.langchain.com/oss/python/contributing/integrations-langchain

Typical usage::

    from surrealdb import Surreal
    from langchain_openai import OpenAIEmbeddings
    from langchain_surrealdb.vectorstores import SurrealDBVectorStore

    async with Surreal("ws://localhost:8000/rpc") as db:
        await db.signin({"username": "root", "password": "root"})
        await db.use("langchain", "langchain")

        store = await SurrealDBVectorStore.afrom_texts(
            texts=["Hello world", "Goodbye world"],
            embedding=OpenAIEmbeddings(),
            db=db,
        )
        results = await store.asimilarity_search("Hello", k=2)
"""

from __future__ import annotations

import asyncio
import json
import logging
import uuid
from typing import (
    Any,
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Tuple,
    Type,
)

import numpy as np
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Distance metric literals understood by SurrealDB's KNN / HNSW operator.
# Brute-force search accepts: COSINE, EUCLIDEAN, MANHATTAN, MINKOWSKI.
# HNSW index additionally supports: EUCLIDEAN (default), COSINE.
# ---------------------------------------------------------------------------
_DISTANCE_METRICS = frozenset(
    {"COSINE", "EUCLIDEAN", "MANHATTAN", "MINKOWSKI", "CHEBYSHEV", "HAMMING"}
)

# SurrealQL EF (effort) default for HNSW queries.
_DEFAULT_EF = 150
# Default number of results returned by similarity search.
_DEFAULT_K = 4


class SurrealDBVectorStore(VectorStore):
    """VectorStore backed by `SurrealDB`_.

    This class stores document text, embeddings, and arbitrary metadata inside
    a SurrealDB table and exposes vector-similarity search through SurrealDB's
    native KNN operator (``<|K,EF|>`` / ``<|K,METRIC|>``).  When an HNSW index
    is defined on the embedding field the KNN operator exploits it automatically
    for sub-linear query time; otherwise SurrealDB falls back to a brute-force
    scan.

    .. _SurrealDB: https://surrealdb.com

    Args:
        db: An **authenticated** and **namespace/database-selected**
            ``surrealdb.Surreal`` (async) connection.  The caller is
            responsible for opening and closing the connection.
        embedding: Embedding model used to embed query strings.
        table_name: SurrealDB table that stores documents.  Created
            automatically if it does not exist.  Defaults to
            ``"langchain_documents"``.
        text_field: Table field that stores the raw document text.
            Defaults to ``"text"``.
        embedding_field: Table field that stores the embedding vector.
            Defaults to ``"embedding"``.
        metadata_field: Table field that stores document metadata as a
            JSON object.  Defaults to ``"metadata"``.
        index_name: Name of the HNSW vector index to create (or expect).
            Defaults to ``"langchain_hnsw_idx"``.  Pass ``None`` to skip
            index creation entirely (brute-force mode).
        vector_dimension: Dimensionality of the embedding vectors.  When
            ``None`` (default) the dimension is inferred from the first
            ``embed_documents`` call and the index is created lazily.
        distance_metric: Distance function used for both index definition
            and KNN queries.  One of ``"COSINE"`` (default),
            ``"EUCLIDEAN"``, ``"MANHATTAN"``.
        ef: HNSW query-time effort parameter (number of candidates
            examined).  Higher values improve recall at the cost of
            latency.  Defaults to ``150``.
        hnsw_m: HNSW graph connectivity parameter *M*.  Defaults to the
            SurrealDB default of ``12``.
        hnsw_efc: HNSW index build-time candidate list size *efc*.
            Defaults to the SurrealDB default of ``150``.
        relevance_score_fn: Score normalization strategy.  ``"cosine"``
            (default) maps raw cosine *distance* to a [0, 1] similarity;
            ``"euclidean"`` applies ``1 / (1 + distance)``; ``"raw"``
            returns the raw distance unchanged.

    Example::

        from surrealdb import Surreal
        from langchain_openai import OpenAIEmbeddings
        from langchain_surrealdb.vectorstores import SurrealDBVectorStore

        async with Surreal("ws://localhost:8000/rpc") as db:
            await db.signin({"username": "root", "password": "root"})
            await db.use("myns", "mydb")

            store = SurrealDBVectorStore(
                db=db,
                embedding=OpenAIEmbeddings(),
                table_name="docs",
                distance_metric="COSINE",
            )
            ids = await store.aadd_texts(["Hello world", "Foo bar"])
            results = await store.asimilarity_search("Hello", k=1)
    """

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def __init__(
        self,
        db: Any,  # surrealdb.Surreal – typed as Any to avoid hard dep at import
        embedding: Embeddings,
        *,
        table_name: str = "langchain_documents",
        text_field: str = "text",
        embedding_field: str = "embedding",
        metadata_field: str = "metadata",
        index_name: Optional[str] = "langchain_hnsw_idx",
        vector_dimension: Optional[int] = None,
        distance_metric: str = "COSINE",
        ef: int = _DEFAULT_EF,
        hnsw_m: int = 12,
        hnsw_efc: int = 150,
        relevance_score_fn: str = "cosine",
    ) -> None:
        distance_metric = distance_metric.upper()
        if distance_metric not in _DISTANCE_METRICS:
            raise ValueError(
                f"distance_metric must be one of {_DISTANCE_METRICS}, "
                f"got {distance_metric!r}"
            )
        if relevance_score_fn not in {"cosine", "euclidean", "raw"}:
            raise ValueError(
                "relevance_score_fn must be 'cosine', 'euclidean', or 'raw'"
            )

        self._db = db
        self._embedding = embedding
        self._table = table_name
        self._text_field = text_field
        self._embedding_field = embedding_field
        self._metadata_field = metadata_field
        self._index_name = index_name
        self._vector_dimension = vector_dimension
        self._distance_metric = distance_metric
        self._ef = ef
        self._hnsw_m = hnsw_m
        self._hnsw_efc = hnsw_efc
        self._relevance_score_fn = relevance_score_fn
        self._index_created = False

    # ------------------------------------------------------------------
    # LangChain VectorStore required property
    # ------------------------------------------------------------------

    @property
    def embeddings(self) -> Embeddings:
        """Embedding model used by this store."""
        return self._embedding

    # ------------------------------------------------------------------
    # Schema helpers
    # ------------------------------------------------------------------

    async def _ensure_schema(self, dimension: int) -> None:
        """Create the SurrealDB table schema and HNSW index if needed.

        This is idempotent; SurrealDB's ``DEFINE … IF NOT EXISTS`` prevents
        duplicate definitions.  The first call that discovers the vector
        dimension triggers index creation; subsequent calls are no-ops.
        """
        if self._index_created:
            return

        ddl = f"""
            DEFINE TABLE IF NOT EXISTS {self._table} SCHEMALESS PERMISSIONS NONE;
            DEFINE FIELD IF NOT EXISTS {self._text_field}
                ON {self._table} TYPE string;
            DEFINE FIELD IF NOT EXISTS {self._embedding_field}
                ON {self._table} TYPE array<float>;
            DEFINE FIELD IF NOT EXISTS {self._metadata_field}
                ON {self._table} FLEXIBLE TYPE object;
        """
        await self._db.query(ddl)

        if self._index_name is not None:
            index_ddl = (
                f"DEFINE INDEX IF NOT EXISTS {self._index_name} "
                f"ON {self._table} "
                f"FIELDS {self._embedding_field} "
                f"HNSW DIMENSION {dimension} "
                f"DIST {self._distance_metric} "
                f"M {self._hnsw_m} "
                f"EFC {self._hnsw_efc};"
            )
            await self._db.query(index_ddl)
            logger.info(
                "HNSW index %r on table %r (dim=%d, dist=%s) ensured.",
                self._index_name,
                self._table,
                dimension,
                self._distance_metric,
            )

        self._index_created = True
        self._vector_dimension = dimension

    # ------------------------------------------------------------------
    # Score normalisation
    # ------------------------------------------------------------------

    def _normalise_score(self, raw_distance: float) -> float:
        """Convert a raw KNN distance to a relevance score in [0, 1]."""
        if self._relevance_score_fn == "cosine":
            # SurrealDB's COSINE distance is in [0, 2].
            # Convert to cosine *similarity* ∈ [-1, 1], then shift to [0, 1].
            return 1.0 - (raw_distance / 2.0)
        elif self._relevance_score_fn == "euclidean":
            return 1.0 / (1.0 + raw_distance)
        else:  # "raw"
            return raw_distance

    # ------------------------------------------------------------------
    # Core write path
    # ------------------------------------------------------------------

    async def aadd_texts(
        self,
        texts: Iterable[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        *,
        ids: Optional[List[str]] = None,
        batch_size: int = 128,
        **kwargs: Any,
    ) -> List[str]:
        """Embed *texts* and insert them into SurrealDB.

        Args:
            texts: Iterable of raw text strings to store.
            metadatas: Optional list of metadata dicts (one per text).
            ids: Optional list of string IDs.  Random UUIDs are generated
                when not supplied.
            batch_size: Number of records inserted per SurrealQL query to
                avoid hitting payload limits.  Defaults to 128.

        Returns:
            List of record IDs (strings) in the same order as *texts*.
        """
        text_list: List[str] = list(texts)
        if not text_list:
            return []

        metadatas = metadatas or [{} for _ in text_list]
        if len(metadatas) != len(text_list):
            raise ValueError(
                f"len(metadatas)={len(metadatas)} != len(texts)={len(text_list)}"
            )

        ids = ids or [str(uuid.uuid4()) for _ in text_list]
        if len(ids) != len(text_list):
            raise ValueError(
                f"len(ids)={len(ids)} != len(texts)={len(text_list)}"
            )

        # Embed all texts in one call (most embedding models batch internally).
        vectors: List[List[float]] = await asyncio.get_event_loop().run_in_executor(
            None, self._embedding.embed_documents, text_list
        )

        dimension = len(vectors[0])
        await self._ensure_schema(dimension)

        # Batch inserts to respect potential payload limits.
        all_ids: List[str] = []
        for start in range(0, len(text_list), batch_size):
            batch_texts = text_list[start : start + batch_size]
            batch_vecs = vectors[start : start + batch_size]
            batch_meta = metadatas[start : start + batch_size]
            batch_ids = ids[start : start + batch_size]

            rows = [
                {
                    "id": f"{self._table}:{rid}",
                    self._text_field: txt,
                    self._embedding_field: vec,
                    self._metadata_field: meta,
                }
                for rid, txt, vec, meta in zip(
                    batch_ids, batch_texts, batch_vecs, batch_meta
                )
            ]

            await self._db.query(
                f"INSERT INTO {self._table} $data;",
                {"data": rows},
            )
            all_ids.extend(batch_ids)

        logger.debug("Inserted %d documents into %r.", len(all_ids), self._table)
        return all_ids

    def add_texts(
        self,
        texts: Iterable[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> List[str]:
        """Synchronous wrapper around :meth:`aadd_texts`.

        Prefer :meth:`aadd_texts` in async contexts.
        """
        return asyncio.get_event_loop().run_until_complete(
            self.aadd_texts(texts, metadatas, **kwargs)
        )

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    async def adelete(
        self,
        ids: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Optional[bool]:
        """Delete documents by their IDs.

        Args:
            ids: List of record IDs (without the table prefix) to delete.

        Returns:
            ``True`` on success, ``False`` on failure.
        """
        if not ids:
            return True
        try:
            for rid in ids:
                record_id = (
                    rid if rid.startswith(f"{self._table}:") else f"{self._table}:{rid}"
                )
                await self._db.delete(record_id)
            return True
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to delete records %s: %s", ids, exc)
            return False

    def delete(
        self,
        ids: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Optional[bool]:
        """Synchronous wrapper around :meth:`adelete`."""
        return asyncio.get_event_loop().run_until_complete(self.adelete(ids, **kwargs))

    # ------------------------------------------------------------------
    # Core read path – similarity search by vector
    # ------------------------------------------------------------------

    async def asimilarity_search_by_vector_with_relevance_scores(
        self,
        embedding: List[float],
        k: int = _DEFAULT_K,
        *,
        filter: Optional[Dict[str, Any]] = None,
        ef: Optional[int] = None,
        use_hnsw: bool = True,
        **kwargs: Any,
    ) -> List[Tuple[Document, float]]:
        """Return *(Document, relevance_score)* pairs for a query vector.

        Args:
            embedding: Pre-computed query vector.
            k: Number of nearest neighbours to return.
            filter: Optional dictionary of metadata equality filters
                applied **before** the KNN search.  Example::

                    {"source": "wiki", "year": 2024}

            ef: HNSW query effort override for this single call.  Falls
                back to the instance-level ``ef`` when ``None``.
            use_hnsw: When ``True`` (default) uses the HNSW index via the
                ``<|K,EF|>`` operator.  When ``False`` uses the brute-force
                ``<|K,METRIC|>`` variant (useful for exact search or before
                the index is built).

        Returns:
            List of *(Document, relevance_score)* tuples ordered by
            descending relevance.
        """
        await self._ensure_schema(len(embedding))

        ef_value = ef if ef is not None else self._ef

        # ------ Build WHERE clause ----------------------------------------
        where_parts: List[str] = []

        # Metadata filters – each key/value pair becomes an equality predicate
        # on the FLEXIBLE metadata object field.
        if filter:
            for key, value in filter.items():
                # Serialise value to SurrealQL literal.
                if isinstance(value, str):
                    escaped = value.replace("'", "\\'")
                    where_parts.append(
                        f"{self._metadata_field}.{key} = '{escaped}'"
                    )
                elif isinstance(value, bool):
                    where_parts.append(
                        f"{self._metadata_field}.{key} = "
                        f"{'true' if value else 'false'}"
                    )
                elif isinstance(value, (int, float)):
                    where_parts.append(
                        f"{self._metadata_field}.{key} = {value}"
                    )
                else:
                    # Fallback: use JSON encoding for complex types
                    where_parts.append(
                        f"{self._metadata_field}.{key} = {json.dumps(value)}"
                    )

        # KNN operator – always applied last in WHERE.
        if use_hnsw and self._index_name:
            knn_expr = (
                f"{self._embedding_field} <|{k},{ef_value}|> $query_vec"
            )
        else:
            knn_expr = (
                f"{self._embedding_field} <|{k},{self._distance_metric}|> $query_vec"
            )

        where_parts.append(knn_expr)
        where_clause = " AND ".join(where_parts)

        # ------ Build SELECT ----------------------------------------------
        #
        # ``vector::distance::knn()`` re-uses the distance already computed
        # by the KNN operator – avoids a second distance computation.
        surql = (
            f"SELECT id, {self._text_field}, {self._metadata_field}, "
            f"vector::distance::knn() AS _distance "
            f"FROM {self._table} "
            f"WHERE {where_clause} "
            f"ORDER BY _distance ASC "
            f"LIMIT {k};"
        )

        result = await self._db.query(surql, {"query_vec": embedding})

        # result is typically a list of response objects; normalise to list[dict]
        rows = self._extract_rows(result)

        docs_and_scores: List[Tuple[Document, float]] = []
        for row in rows:
            text = row.get(self._text_field, "")
            metadata = row.get(self._metadata_field) or {}
            raw_id = row.get("id", "")
            # Strip table prefix from the record ID for user convenience.
            doc_id = str(raw_id).replace(f"{self._table}:", "", 1)
            metadata["_id"] = doc_id
            distance = float(row.get("_distance") or 0.0)
            score = self._normalise_score(distance)
            docs_and_scores.append(
                (Document(page_content=text, metadata=metadata), score)
            )

        return docs_and_scores

    # ------------------------------------------------------------------
    # Convenience search methods (mirror LangChain VectorStore API)
    # ------------------------------------------------------------------

    async def asimilarity_search_with_relevance_scores(
        self,
        query: str,
        k: int = _DEFAULT_K,
        **kwargs: Any,
    ) -> List[Tuple[Document, float]]:
        """Return *(Document, score)* pairs for a text *query*.

        The query is embedded via ``self.embeddings`` before searching.
        """
        query_vec = await asyncio.get_event_loop().run_in_executor(
            None, self._embedding.embed_query, query
        )
        return await self.asimilarity_search_by_vector_with_relevance_scores(
            query_vec, k=k, **kwargs
        )

    async def asimilarity_search_with_score(
        self,
        query: str,
        k: int = _DEFAULT_K,
        **kwargs: Any,
    ) -> List[Tuple[Document, float]]:
        """Alias of :meth:`asimilarity_search_with_relevance_scores`."""
        return await self.asimilarity_search_with_relevance_scores(
            query, k=k, **kwargs
        )

    async def asimilarity_search(
        self,
        query: str,
        k: int = _DEFAULT_K,
        **kwargs: Any,
    ) -> List[Document]:
        """Return the *k* most similar documents for a text *query*."""
        pairs = await self.asimilarity_search_with_relevance_scores(
            query, k=k, **kwargs
        )
        return [doc for doc, _ in pairs]

    async def asimilarity_search_by_vector(
        self,
        embedding: List[float],
        k: int = _DEFAULT_K,
        **kwargs: Any,
    ) -> List[Document]:
        """Return the *k* most similar documents for a raw embedding vector."""
        pairs = await self.asimilarity_search_by_vector_with_relevance_scores(
            embedding, k=k, **kwargs
        )
        return [doc for doc, _ in pairs]

    # ---- Synchronous wrappers -------------------------------------------

    def similarity_search_with_relevance_scores(
        self,
        query: str,
        k: int = _DEFAULT_K,
        **kwargs: Any,
    ) -> List[Tuple[Document, float]]:
        """Synchronous :meth:`asimilarity_search_with_relevance_scores`."""
        return asyncio.get_event_loop().run_until_complete(
            self.asimilarity_search_with_relevance_scores(query, k=k, **kwargs)
        )

    def similarity_search_with_score(
        self,
        query: str,
        k: int = _DEFAULT_K,
        **kwargs: Any,
    ) -> List[Tuple[Document, float]]:
        """Synchronous :meth:`asimilarity_search_with_score`."""
        return asyncio.get_event_loop().run_until_complete(
            self.asimilarity_search_with_score(query, k=k, **kwargs)
        )

    def similarity_search(
        self,
        query: str,
        k: int = _DEFAULT_K,
        **kwargs: Any,
    ) -> List[Document]:
        """Synchronous :meth:`asimilarity_search`."""
        return asyncio.get_event_loop().run_until_complete(
            self.asimilarity_search(query, k=k, **kwargs)
        )

    def similarity_search_by_vector(
        self,
        embedding: List[float],
        k: int = _DEFAULT_K,
        **kwargs: Any,
    ) -> List[Document]:
        """Synchronous :meth:`asimilarity_search_by_vector`."""
        return asyncio.get_event_loop().run_until_complete(
            self.asimilarity_search_by_vector(embedding, k=k, **kwargs)
        )

    # ------------------------------------------------------------------
    # Maximal Marginal Relevance (MMR)
    # ------------------------------------------------------------------

    async def amax_marginal_relevance_search(
        self,
        query: str,
        k: int = _DEFAULT_K,
        fetch_k: int = 20,
        lambda_mult: float = 0.5,
        **kwargs: Any,
    ) -> List[Document]:
        """Return docs selected by Maximal Marginal Relevance.

        MMR optimises for *relevance to the query* while maximising
        *diversity* among the returned documents.

        Args:
            query: Text query.
            k: Number of final documents to return.
            fetch_k: Number of candidate documents to retrieve before MMR
                re-ranking.  Should be larger than *k*.
            lambda_mult: Trade-off parameter ∈ [0, 1].  1 → minimum
                diversity (pure similarity); 0 → maximum diversity.

        Returns:
            List of selected :class:`~langchain_core.documents.Document`
            objects.
        """
        query_vec = await asyncio.get_event_loop().run_in_executor(
            None, self._embedding.embed_query, query
        )
        return await self.amax_marginal_relevance_search_by_vector(
            query_vec,
            k=k,
            fetch_k=fetch_k,
            lambda_mult=lambda_mult,
            **kwargs,
        )

    async def amax_marginal_relevance_search_by_vector(
        self,
        embedding: List[float],
        k: int = _DEFAULT_K,
        fetch_k: int = 20,
        lambda_mult: float = 0.5,
        **kwargs: Any,
    ) -> List[Document]:
        """MMR search given a pre-computed query vector."""
        # 1. Fetch a larger candidate set.
        pairs = await self.asimilarity_search_by_vector_with_relevance_scores(
            embedding, k=fetch_k, **kwargs
        )
        if not pairs:
            return []

        candidate_docs = [doc for doc, _ in pairs]

        # 2. Retrieve stored embeddings for the candidates so we can compute
        #    pairwise cosine similarities client-side.
        candidate_embeddings = await asyncio.get_event_loop().run_in_executor(
            None,
            self._embedding.embed_documents,
            [doc.page_content for doc in candidate_docs],
        )

        # 3. Run MMR selection.
        selected_indices = self._maximal_marginal_relevance(
            np.array(embedding, dtype=np.float32),
            np.array(candidate_embeddings, dtype=np.float32),
            k=k,
            lambda_mult=lambda_mult,
        )
        return [candidate_docs[i] for i in selected_indices]

    def max_marginal_relevance_search(
        self,
        query: str,
        k: int = _DEFAULT_K,
        fetch_k: int = 20,
        lambda_mult: float = 0.5,
        **kwargs: Any,
    ) -> List[Document]:
        """Synchronous :meth:`amax_marginal_relevance_search`."""
        return asyncio.get_event_loop().run_until_complete(
            self.amax_marginal_relevance_search(
                query, k=k, fetch_k=fetch_k, lambda_mult=lambda_mult, **kwargs
            )
        )

    def max_marginal_relevance_search_by_vector(
        self,
        embedding: List[float],
        k: int = _DEFAULT_K,
        fetch_k: int = 20,
        lambda_mult: float = 0.5,
        **kwargs: Any,
    ) -> List[Document]:
        """Synchronous :meth:`amax_marginal_relevance_search_by_vector`."""
        return asyncio.get_event_loop().run_until_complete(
            self.amax_marginal_relevance_search_by_vector(
                embedding, k=k, fetch_k=fetch_k, lambda_mult=lambda_mult, **kwargs
            )
        )

    # ------------------------------------------------------------------
    # Class-method constructors (LangChain convention)
    # ------------------------------------------------------------------

    @classmethod
    async def afrom_texts(
        cls: Type["SurrealDBVectorStore"],
        texts: List[str],
        embedding: Embeddings,
        metadatas: Optional[List[Dict[str, Any]]] = None,
        *,
        db: Any,
        ids: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> "SurrealDBVectorStore":
        """Create a :class:`SurrealDBVectorStore` from raw texts.

        Convenience constructor that creates the store, embeds the texts,
        and inserts them in a single call.

        Args:
            texts: Raw text strings.
            embedding: Embedding model.
            metadatas: Optional metadata dicts (one per text).
            db: Authenticated ``surrealdb.Surreal`` connection.
            ids: Optional explicit record IDs.
            **kwargs: Forwarded verbatim to :class:`SurrealDBVectorStore`.

        Returns:
            A new :class:`SurrealDBVectorStore` populated with *texts*.
        """
        store = cls(db=db, embedding=embedding, **kwargs)
        await store.aadd_texts(texts, metadatas=metadatas, ids=ids)
        return store

    @classmethod
    def from_texts(
        cls: Type["SurrealDBVectorStore"],
        texts: List[str],
        embedding: Embeddings,
        metadatas: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> "SurrealDBVectorStore":
        """Synchronous :meth:`afrom_texts`.

        Note: ``db`` must be supplied as a keyword argument.
        """
        return asyncio.get_event_loop().run_until_complete(
            cls.afrom_texts(texts, embedding, metadatas=metadatas, **kwargs)
        )

    @classmethod
    async def afrom_documents(
        cls: Type["SurrealDBVectorStore"],
        documents: List[Document],
        embedding: Embeddings,
        *,
        db: Any,
        ids: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> "SurrealDBVectorStore":
        """Create a :class:`SurrealDBVectorStore` from :class:`Document` objects.

        Args:
            documents: List of LangChain :class:`~langchain_core.documents.Document`.
            embedding: Embedding model.
            db: Authenticated ``surrealdb.Surreal`` connection.
            ids: Optional explicit record IDs.
            **kwargs: Forwarded verbatim to :class:`SurrealDBVectorStore`.

        Returns:
            A new :class:`SurrealDBVectorStore` populated with *documents*.
        """
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        return await cls.afrom_texts(
            texts, embedding, metadatas=metadatas, db=db, ids=ids, **kwargs
        )

    @classmethod
    def from_documents(
        cls: Type["SurrealDBVectorStore"],
        documents: List[Document],
        embedding: Embeddings,
        **kwargs: Any,
    ) -> "SurrealDBVectorStore":
        """Synchronous :meth:`afrom_documents`.

        Note: ``db`` must be supplied as a keyword argument.
        """
        return asyncio.get_event_loop().run_until_complete(
            cls.afrom_documents(documents, embedding, **kwargs)
        )

    # ------------------------------------------------------------------
    # Document retrieval by ID
    # ------------------------------------------------------------------

    async def aget_by_ids(self, ids: List[str]) -> List[Document]:
        """Fetch documents by their record IDs.

        Args:
            ids: List of record IDs (with or without table prefix).

        Returns:
            List of :class:`Document` objects in the same order as *ids*.
            Missing records are silently omitted.
        """
        docs: List[Document] = []
        for rid in ids:
            full_id = (
                rid if rid.startswith(f"{self._table}:") else f"{self._table}:{rid}"
            )
            result = await self._db.select(full_id)
            if result:
                row = result if isinstance(result, dict) else result[0]
                text = row.get(self._text_field, "")
                metadata = row.get(self._metadata_field) or {}
                metadata["_id"] = rid
                docs.append(Document(page_content=text, metadata=metadata))
        return docs

    def get_by_ids(self, ids: List[str]) -> List[Document]:
        """Synchronous :meth:`aget_by_ids`."""
        return asyncio.get_event_loop().run_until_complete(self.aget_by_ids(ids))

    # ------------------------------------------------------------------
    # Index management helpers
    # ------------------------------------------------------------------

    async def acreate_index(self) -> None:
        """(Re-)create the HNSW vector index.

        Useful after bulk ingestion when the index may have been deferred.
        Raises :exc:`RuntimeError` if the vector dimension is not yet known.
        """
        if self._vector_dimension is None:
            raise RuntimeError(
                "Cannot create the index before the vector dimension is known. "
                "Insert at least one document first."
            )
        if self._index_name is None:
            raise RuntimeError(
                "No index_name configured.  Pass index_name=<str> to enable "
                "HNSW index management."
            )
        index_ddl = (
            f"DEFINE INDEX {self._index_name} "
            f"ON {self._table} "
            f"FIELDS {self._embedding_field} "
            f"HNSW DIMENSION {self._vector_dimension} "
            f"DIST {self._distance_metric} "
            f"M {self._hnsw_m} "
            f"EFC {self._hnsw_efc} "
            f"OVERWRITE;"
        )
        await self._db.query(index_ddl)
        logger.info(
            "HNSW index %r (re)created on table %r.",
            self._index_name,
            self._table,
        )

    async def adrop_index(self) -> None:
        """Drop the HNSW vector index (does not remove data)."""
        if self._index_name is None:
            return
        await self._db.query(
            f"REMOVE INDEX IF EXISTS {self._index_name} ON {self._table};"
        )
        self._index_created = False
        logger.info("HNSW index %r dropped.", self._index_name)

    async def adrop_table(self) -> None:
        """Drop the entire table (irreversible – deletes all documents)."""
        await self._db.query(f"REMOVE TABLE IF EXISTS {self._table};")
        self._index_created = False
        logger.warning("Table %r dropped.", self._table)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_rows(query_result: Any) -> List[Dict[str, Any]]:
        """Normalise the heterogeneous return values of ``db.query()``.

        ``surrealdb-py`` can return a list of response dicts, a list of
        result dicts, or (in older SDK versions) a flat list of record
        dicts.  This method handles all three cases.
        """
        if not query_result:
            return []
        # Unwrap a single-statement response list: [{result: [...], ...}]
        if isinstance(query_result, list):
            first = query_result[0]
            if isinstance(first, dict) and "result" in first:
                return first["result"] or []
            # Already a flat list of record dicts.
            return query_result
        return []

    @staticmethod
    def _maximal_marginal_relevance(
        query_embedding: np.ndarray,
        candidate_embeddings: np.ndarray,
        k: int,
        lambda_mult: float,
    ) -> List[int]:
        """Greedy MMR selection returning *k* indices into *candidate_embeddings*.

        Args:
            query_embedding: 1-D query vector of shape ``(D,)``.
            candidate_embeddings: 2-D matrix of shape ``(N, D)``.
            k: Number of documents to select.
            lambda_mult: Relevance/diversity trade-off ∈ [0, 1].

        Returns:
            Ordered list of *k* integer indices.
        """

        def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> np.ndarray:
            a_norm = np.linalg.norm(a)
            b_norms = np.linalg.norm(b, axis=1, keepdims=True)
            b_norms = np.where(b_norms == 0, 1e-9, b_norms)
            return (b @ a) / (a_norm * b_norms.flatten() + 1e-9)

        n = len(candidate_embeddings)
        k = min(k, n)

        sim_to_query = _cosine_similarity(query_embedding, candidate_embeddings)

        selected: List[int] = []
        remaining = list(range(n))

        for _ in range(k):
            if not remaining:
                break
            if not selected:
                # Pick the most similar doc first.
                idx = int(np.argmax(sim_to_query[remaining]))
                selected.append(remaining[idx])
                remaining.pop(idx)
                continue

            # For each remaining candidate compute max similarity to already
            # selected set.
            selected_embeddings = candidate_embeddings[selected]
            redundancy = np.max(
                np.stack(
                    [
                        _cosine_similarity(candidate_embeddings[i], selected_embeddings)
                        for i in remaining
                    ]
                ),
                axis=1,
            )

            mmr_scores = (
                lambda_mult * sim_to_query[remaining]
                - (1 - lambda_mult) * redundancy
            )
            best = int(np.argmax(mmr_scores))
            selected.append(remaining[best])
            remaining.pop(best)

        return selected

    # ------------------------------------------------------------------
    # Dunder helpers
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"SurrealDBVectorStore("
            f"table={self._table!r}, "
            f"distance={self._distance_metric}, "
            f"index={self._index_name!r}"
            f")"
        )