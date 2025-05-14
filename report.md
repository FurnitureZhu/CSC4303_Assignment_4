# Chord DHT Implementation Report

This report provides a brief explanation for the following functions: `find_successor`, `closest_preceding_node`, `create`, `join`,
`stabilize`, `notify`, `fix_fingers`, `put`, `get`, `transfer_keys`.

## 1. `find_successor(id)`
- **Purpose**: Find the successor node for a given identifier.
- **Implementation Details**: Checks if the ID lies between the current node and its successor; if so, then returns the successor. Otherwise, delegates the query to the closest preceding node.

## 2. `closest_preceding_node(id)`
- **Purpose**: Find the closest preceding node for a given identifier.
- **Implementation Details**: Iterates the finger table in reverse order, returning the first node whose ID is in the open interval `(self.node_id, id)`. Returns the current node if no suitable predecessor is found, ensuring robust query forwarding.

## 3. `create()`
- **Purpose**: Create a new Chord ring.
- **Implementation Details**: Just form a self-contained ring ready for other nodes to join.

## 4. `join(existing_node_addr)`
- **Purpose**: Integrates the current node into an existing Chord ring via a known node.
- **Implementation Details**: Find node's successor through the existing node and also has a Error raise if no successors.

## 5.1: `ping(self, node_addr)`
- **Purpose**: <span style="color: green;">**Newly Added Function**</span> Check if the target node is alive by sending a 'ping' request, return False if file to send. This Function is used for **Finger Table Failure Recovery**

## 5.2: `stabilize()`
- **Purpose**:  Verify if this node's immediate successor is consistent, and tells the successor about this node. And realize the Finger Table Failure Recovery.
- **Implementation Details**: Pings the successor to check liveness; if unreachable, selects a new successor from the finger table. Retrieves the successor’s predecessor and updates the successor if needed, notifying it via `remote_call`. Handles errors to ensure stability. 

## 6. `notify(node_addr)`
- **Purpose**: Called by another node claiming to be this node's predecessor.
- **Implementation Details**: Updates the predecessor if it is `None` or if the new node’s ID lies between the current predecessor and the current node, using `in_interval` for correctness.

## 7. `fix_fingers()`
- **Purpose**: Refresh finger table entries. self.next stores the index of the finger to fix.
- **Implementation Details**: Increments the `next` index to update one finger entry per call, computing the target ID as `node_id + 2^(next-1) mod 2^m`. Calls `find_successor` to set the entry, cycling through indices to maintain all entries.

## 8. `put(key, value)`
- **Purpose**: Stores a key-value pair in the DHT.
- **Implementation Details**: Hashes the key using `hash_key` and finds the successor via `find_successor`. Stores locally if the current node is responsible; otherwise, delegates to the successor via `remote_call`. Returns `True` on success.

## 9. `get(key)`
- **Purpose**: Retrieve a value from the DHT.
- **Implementation Details**: Hashes the key and finds the successor. Retrieves locally if the current node is responsible; otherwise, uses `remote_call` to fetch from the successor. Returns `None` if the key is not found.

## 10. `transfer_keys(new_node_addr)`
- **Purpose**: Transfer keys that now belong to the new node.
- **Implementation Details**: Identifies keys whose hashed values lie in `(pred_id, new_node_id]` using a dictionary comprehension. Transfers these keys to the new node via `remote_call` and removes them locally, ensuring minimal data movement.


