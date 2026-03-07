"""
Named SurrealQL query strings.

TODO: test and refine each query against a live SurrealDB instance.
"""

QUERY_OVERDUE_COMMITMENTS = """
-- Find all actions where status='pending' and deadline < now()
-- Return person name, action description, deadline, originating meeting title
SELECT
    person.name    AS person,
    action.description AS action,
    committed.deadline AS deadline,
    meeting.title  AS meeting_origin,
    duration::days(time::now() - committed.deadline) AS days_overdue
FROM committed
WHERE status = 'pending'
  AND deadline < time::now()
FETCH person, action, meeting;
"""

QUERY_CROSS_MEETING_DELTA = """
-- Given a meeting_id, find actions from PREVIOUS meetings still pending
-- whose owners attended this meeting
SELECT
    person.name AS person,
    action.description AS action,
    originated_in.meeting.title AS meeting_origin
FROM committed
WHERE status = 'pending'
  AND (SELECT VALUE id FROM meeting ORDER BY date DESC LIMIT 1)[0] != $meeting_id
FETCH person, action;
"""

QUERY_SINGLE_POINT_OF_FAILURE = """
-- For each person: count pending outgoing committed edges
-- + count people blocked by their actions
-- Return top 3
SELECT
    person.name AS person,
    count(->committed[WHERE status='pending']) AS open_commitments,
    count(->committed->action->blocks<-committed<-person) AS blocking_count,
    (open_commitments + blocking_count * 1.5) AS risk_score
FROM person
ORDER BY risk_score DESC
LIMIT 3;
"""

QUERY_CONTRADICTION_CHECK = """
-- Find existing decisions with embedding similarity > 0.85 to new decision
SELECT id, description,
    vector::similarity::cosine(embedding, $embedding) AS similarity
FROM decision
WHERE vector::similarity::cosine(embedding, $embedding) > 0.85
  AND id != $exclude_id
ORDER BY similarity DESC;
"""

QUERY_TOPIC_COMMITMENT_HISTORY = """
-- Given a topic name, traverse full chain:
-- topic <- discussed <- meeting <- originated_in <- action <- committed <- person
SELECT
    person.name AS person,
    action.description AS action,
    action.status AS status,
    meeting.date AS meeting_date,
    meeting.title AS meeting_title
FROM topic
WHERE name = $topic_name
    ->discussed<-meeting
    <-originated_in<-action
    <-committed<-person
FETCH person, action, meeting;
"""
