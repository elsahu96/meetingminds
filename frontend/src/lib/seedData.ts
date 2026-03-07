import type { GraphNode, GraphEdge, Transcript, ChatMessage } from "@/types";

export const SEED_NODES: GraphNode[] = [];
// [
//   { id: 'alice',  type: 'person',   label: 'alice_chen',        tooltip: { type: 'PERSON',   name: 'Alice Chen',          role: 'Eng Lead',       commits: '4 open',           risk: '4.2/5' } },
//   { id: 'bob',    type: 'person',   label: 'bob_okafor',        tooltip: { type: 'PERSON',   name: 'Bob Okafor',          role: 'Backend Eng',    commits: '1 open',           risk: '1.1/5' } },
//   { id: 'carol',  type: 'person',   label: 'carol_zhang',       tooltip: { type: 'PERSON',   name: 'Carol Zhang',         role: 'Product Mgr',    commits: '2 open',           risk: '1.8/5' } },
//   { id: 'david',  type: 'person',   label: 'david_kim',         tooltip: { type: 'PERSON',   name: 'David Kim',           role: 'DevOps',         commits: '1 open',           risk: '0.9/5' } },
//   { id: 'm42',    type: 'meeting',  label: 'sprint-plan-w12',   tooltip: { type: 'MEETING',  name: 'Sprint Planning',     role: 'Mar 5 2025',     commits: '3 actions',        risk: '—' } },
//   { id: 'm43',    type: 'meeting',  label: 'sprint-rev-w12',    tooltip: { type: 'MEETING',  name: 'Sprint Review',       role: 'Mar 12 2025',    commits: '2 actions',        risk: '—' } },
//   { id: 'a17',    type: 'action',   label: 'payments-refactor', overdue: true, tooltip: { type: 'ACTION',   name: 'Payments Refactor',   role: 'Alice · Mar5',   commits: 'OVERDUE',          risk: 'high' } },
//   { id: 'a18',    type: 'action',   label: 'fix-auth-503',      tooltip: { type: 'ACTION',   name: 'Fix Auth 503s',       role: 'Bob · done',     commits: 'DONE',             risk: '—' } },
//   { id: 'a19',    type: 'action',   label: 'k8s-upgrade',       tooltip: { type: 'ACTION',   name: 'K8s 1.29 Upgrade',   role: 'David · done',   commits: 'DONE',             risk: '—' } },
//   { id: 'a20',    type: 'action',   label: 'export-spec',       tooltip: { type: 'ACTION',   name: 'Write Export Spec',  role: 'Carol · Mon',    commits: 'pending',          risk: 'low' } },
//   { id: 'd3',     type: 'decision', label: 'deprioritise-exp',  tooltip: { type: 'DECISION', name: 'Deprioritise Export', role: 'Carol · W12 Plan', commits: 'CONTRADICTED',   risk: 'high' } },
//   { id: 'd9',     type: 'decision', label: 'proceed-export',    tooltip: { type: 'DECISION', name: 'Proceed w/ Export',  role: 'Carol · W12 Rev', commits: 'contradicts d3',  risk: 'high' } },
//   { id: 'bl1',    type: 'blocker',  label: 'payments-block',    tooltip: { type: 'BLOCKER',  name: 'Payments Merge Block', role: '3 people',      commits: 'severity:high',    risk: '—' } },
//   { id: 'tp1',    type: 'topic',    label: 'payments-svc',      tooltip: { type: 'TOPIC',    name: 'Payments Service',   role: 'backend',        commits: 'importance:0.91',  risk: '—' } },
//   { id: 'tp2',    type: 'topic',    label: 'export-feature',    tooltip: { type: 'TOPIC',    name: 'Export Feature',     role: 'product',        commits: 'importance:0.74',  risk: '—' } },
// ]

export const SEED_EDGES: GraphEdge[] = [
  { source: "alice", target: "a17", type: "committed" },
  { source: "bob", target: "a18", type: "committed" },
  { source: "david", target: "a19", type: "committed" },
  { source: "carol", target: "a20", type: "committed" },
  { source: "a17", target: "m42", type: "originated" },
  { source: "a18", target: "m42", type: "originated" },
  { source: "a20", target: "m43", type: "originated" },
  { source: "a17", target: "bl1", type: "blocks" },
  { source: "d3", target: "d9", type: "contradicts" },
  { source: "m42", target: "tp1", type: "originated" },
  { source: "m43", target: "tp2", type: "originated" },
  { source: "alice", target: "m42", type: "committed" },
  { source: "bob", target: "m42", type: "committed" },
  { source: "carol", target: "m43", type: "committed" },
];

export const SEED_TRANSCRIPTS: Transcript[] = [
  {
    id: "t0",
    title: "Sprint Planning — Week 12",
    date: "2025-03-05",
    status: "done",
    progress: 100,
    text: `Alice: The payments refactor is my top priority this sprint. I'll have it done by Friday.
Bob: The auth service 503s are blocking me. I'll fix them by Wednesday.
Carol: I've decided to deprioritise the export feature for this sprint.
David: I'll get the K8s upgrade to 1.29 done by end of sprint.`,
  },
  {
    id: "t1",
    title: "Sprint Review — Week 12",
    date: "2025-03-12",
    status: "queued",
    progress: 0,
    text: `Alice: The payments refactor is still not done, I need one more day.
Bob: Auth 503s are fixed and deployed. All tests passing.
Carol: I think we should proceed with the export feature. Let me write the spec by Monday.
David: K8s upgrade is complete. Running 1.29 in staging.`,
  },
];

export const SEED_CHAT: ChatMessage[] = [
  {
    id: "cm1",
    role: "user",
    text: "What was promised last week that hasn't been delivered?",
    timestamp: new Date("2025-03-12T14:32:00"),
  },
  {
    id: "cm2",
    role: "agent",
    text: `Found <span class="hl-pill">1 broken promise</span> from Sprint Planning (Mar 5):<br/><br/><strong>Alice Chen</strong> committed to completing the payments service refactor by <strong>Mar 5</strong>. As of Mar 12 this is still <span style="color:var(--tw-color-red, #ff4d6a)">status: pending</span> — 7 days overdue.<br/><br/>Additionally <strong>3 people</strong> (Bob, Carol, David) have actions blocked pending Alice's merge.`,
    citations: [
      { label: "Sprint Planning · Mar 5", nodeId: "m42" },
      { label: "action:a17", nodeId: "a17" },
      { label: "person:alice", nodeId: "alice" },
    ],
    timestamp: new Date("2025-03-12T14:32:05"),
  },
  {
    id: "cm3",
    role: "user",
    text: "Who is a single point of failure right now?",
    timestamp: new Date("2025-03-12T14:35:00"),
  },
  {
    id: "cm4",
    role: "agent",
    text: `<span class="hl-pill">Alice Chen</span> — risk score 4.2/5<br/><br/>· <strong>4 open commitments</strong> (most on team)<br/>· <strong>2 people directly blocked</strong> on her deliverables<br/>· <strong>1 contradiction</strong> she's central to<br/><br/>If Alice goes on leave today, the sprint delivery fails.`,
    citations: [
      { label: "person:alice_chen", nodeId: "alice" },
      { label: "centrality:0.82" },
    ],
    timestamp: new Date("2025-03-12T14:35:08"),
  },
];

export const PROCESS_STEPS = [
  {
    cls: "active" as const,
    icon: "◌",
    text: "Ingesting Sprint Review transcript…",
  },
  {
    cls: "done" as const,
    icon: "✓",
    text: "Transcript split · 4 turns detected",
    tag: "4",
  },
  {
    cls: "active" as const,
    icon: "◌",
    text: "Resolving speakers against existing graph…",
  },
  {
    cls: "done" as const,
    icon: "✓",
    text: "Speakers matched · 4 known persons",
    tag: "4",
  },
  {
    cls: "active" as const,
    icon: "◌",
    text: "Extracting entities · claude-3-5-sonnet…",
  },
  {
    cls: "done" as const,
    icon: "✓",
    text: "Entities extracted · confidence 0.94",
    tag: "0.94",
  },
  { cls: "active" as const, icon: "◌", text: "Writing to SurrealDB…" },
  {
    cls: "done" as const,
    icon: "✓",
    text: "Graph updated · 6 nodes · 8 edges",
    tag: "+6/+8",
  },
  {
    cls: "warn" as const,
    icon: "⚠",
    text: "Contradiction detected · d9 vs d3",
    tag: "HIGH",
  },
  {
    cls: "done" as const,
    icon: "✓",
    text: "Checkpoint saved · sprint-review-w12",
  },
];
