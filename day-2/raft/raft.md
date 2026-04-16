# Raft Terminology (System Design Reference)

A concise, structured glossary of all important terms used in the Raft consensus algorithm.

---

## 1. Core Concepts

### Cluster
A group of servers (nodes) participating in Raft. Typically 3, 5, or 7 nodes.

### Node (Server)
An individual machine/process participating in the Raft protocol.

### State Machine
The application logic that consumes committed log entries.  
Example: database, key-value store.

---

## 2. Node Roles

### Follower
- Passive role
- Responds to leader or candidate requests
- Does not initiate actions on its own

### Candidate
- Temporary role during election
- Requests votes from other nodes
- Becomes leader if majority votes received

### Leader
- Handles all client requests
- Replicates logs to followers
- Maintains authority via heartbeats

---

## 3. Time & Terms

### Term
- Logical clock in Raft
- Increases monotonically
- Used to detect stale leaders

Example:
Term 1 → Term 2 → Term 3

### Election Timeout
- Time a follower waits before starting election
- Randomized to avoid split votes

### Heartbeat Interval
- Periodic signal sent by leader to followers
- Prevents new elections

---

## 4. RPCs (Remote Procedure Calls)

### RequestVote RPC
Used by candidates to request votes.

Fields:
- term
- candidateId
- lastLogIndex
- lastLogTerm

### AppendEntries RPC
Used by leader to:
- replicate logs
- send heartbeats

Fields:
- term
- leaderId
- prevLogIndex
- prevLogTerm
- entries[]
- leaderCommit

---

## 5. Log Structure

### Log Entry
A record containing:
- command (operation)
- term (when it was created)

### Log Index
Position of entry in the log (starts from 1)

### Log Matching Property
If two logs have same index and term → entries are identical

---

## 6. Replication & Commit

### Replication
Leader sends log entries to followers using AppendEntries

### Majority (Quorum)
More than half of nodes

Example:
- 5 nodes → majority = 3
- 3 nodes → majority = 2

### Commit Index
Index of highest log entry known to be committed

### Committed Entry
Entry replicated on majority of nodes

### Apply (State Machine Apply)
Process of executing committed entries on state machine

---

## 7. Election Mechanics

### Vote
A node grants vote to a candidate per term

### Voting Rules
- One vote per term per node
- Vote only if candidate log is up-to-date

### Up-to-date Log
A log is considered newer if:
1. Higher term
2. If same term → higher index

---

## 8. Safety Guarantees

### Leader Completeness
Committed entries are always present in future leaders

### Election Safety
Only one leader per term

### Log Consistency
Followers' logs eventually match leader

### State Machine Safety
No two nodes apply different commands at same index

---

## 9. Failure Handling

### Leader Failure
- Followers detect missing heartbeat
- New election triggered

### Network Partition
- Majority side continues
- Minority side becomes unavailable

---

## 10. Internal Leader State

### nextIndex[]
For each follower:
- Next log index to send

### matchIndex[]
For each follower:
- Highest index replicated on that follower

---

## 11. Snapshotting (Log Compaction)

### Snapshot
Compressed representation of state machine

### Log Compaction
Removing old logs after snapshot

### InstallSnapshot RPC
Used to send snapshot to lagging followers

---

## 12. Client Interaction

### Client Request
Sent only to leader

### Redirection
Follower redirects client to leader

### Linearizability
Strong consistency guarantee provided by Raft

---

## 13. Quick Summary Table

| Term | Meaning |
|------|--------|
| Term | Logical clock |
| Leader | Handles writes |
| Follower | Passive node |
| Candidate | Election state |
| Log Entry | Operation record |
| Commit | Majority replicated |
| Apply | Execute on state machine |
| Quorum | Majority nodes |
| Heartbeat | Leader keep-alive |
| Snapshot | Compacted state |

---

## One-line Summary

Raft ensures distributed consensus by electing a leader and replicating logs across a majority of nodes while maintaining strong consistency and fault tolerance.