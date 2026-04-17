
1. Leader-based write path

When a client sends a write:
	1.	Client can connect to any ZooKeeper server.
	2.	The write is forwarded to the leader.
	3.	The leader creates a proposal for that transaction.
	4.	Followers acknowledge the proposal.
	5.	Once a quorum acknowledges it, the leader commits it.
	6.	All servers apply that write in the same order.  ￼

2. flow

Client write
   |
   v
Follower/Leader node
   |
   v
Leader creates proposal
   |
   +--> Follower 1 ACK
   +--> Follower 2 ACK
   |
Quorum reached
   |
   v
COMMIT
   |
   +--> All nodes apply transaction in same order

3. The three Zab phases

ZooKeeper’s internal docs describe atomic broadcast with leader activation and active messaging. In practical training terms, you can think of Zab as moving through these phases:

Discovery
A leader is identified after failure or startup.

Synchronization
The leader makes followers catch up so they share the same committed history.

Broadcast
Normal operation: proposals, acknowledgments, commit, apply.