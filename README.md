[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/i1U55jTT)
# CSC4303 Assignment-4: Chord DHT (12 points)

### Deadline: March 30, 2025, 23:59

### Name:

### Student ID:

## Overview

This assignment involves implementing the Chord Distributed Hash Table (DHT) protocol, a scalable peer-to-peer lookup protocol that provides a way to locate keys in a distributed network environment. Chord is notable for its simplicity, provable correctness, and performance guarantees.

Your task is to implement the core algorithms of a Chord DHT including key lookup, node join/leave, stabilization mechanisms, and fault tolerance using successor lists.

## Background

The Chord protocol specifies how to find the location of keys, how new nodes join the system, and how to recover from node failures. Each node in a Chord system maintains a routing table called a finger table that enables fast key lookups in O(log N) time, where N is the number of nodes in the system.

Chord arranges nodes in a logical ring where each node has a successor and a predecessor. Keys are assigned to nodes based on consistent hashing, which provides load balancing and minimizes the number of keys that must move when nodes join or leave the system.

## Assignment Requirements

### Core Requirements

1. **Chord protocol**

    - Implement the `find_successor(id)` method to find the successor for a given identifier.
    - Implement the `closest_preceding_node(id)` method to find the closest preceding node for a given identifier.
    - Implement the `create()` method to create a new Chord ring.
    - Implement the `join(existing_node_addr)` method to join an existing ring.
    - Implement the `stabilize()` method to verify a node's successor.
    - Implement the `notify(node_addr)` method to handle predecessor updates.
    - Implement the `fix_fingers()` method to refresh finger table entries.

    _Note_: The stabilization protocol is called manually in the test suite. In reality the protocol should run periodically in the background.

2. **Key Storage**

    - Implement the `put(key, value)` method to store data in the DHT.
    - Implement the `get(key)` method to retrieve data from the DHT.
    - Implement the `transfer_keys(new_node_addr)` method to handle key redistribution.

### Advanced Requirements (Optional)

3. **Finger Table Failure Recovery**

    The key step in failure recovery is maintaining a correct finger table. The original Chord paper suggests a "successor-list" of nearest successors to achieve this. The method `check_predecessor()` is called manually in the test suite to simulate periodic call. You can create additional methods as needed to perform failure recovery.

    _Note_: Chord DHT would require replication for key storage recovery. This is out of scope for this assignment.

## Testing

A comprehensive test suite is provided in the `test_dht.py` file. This test suite verifies:

1. Basic chord protocol (create, join, stabilize, fix_fingers)
2. Key storage and retrieval (put, get)
3. Key transfers upon node join (transfer_keys)
4. Finger table failure recovery

To run the test suite:

```bash
python test_dht.py
```

## References

Stoica, I., Morris, R., Karger, D., Kaashoek, M. F., & Balakrishnan, H. (2001). Chord: A scalable peer-to-peer lookup service for internet applications. _ACM SIGCOMM Computer Communication Review_, 31(4), 149-160.

## Submission Guidelines

1. Complete the implementation of all required methods in the `chord_node.py` file.
2. Ensure that all test cases in `test_dht.py` pass successfully. Save the test results to `output_dht.txt`.
3. Submit the following files to your GitHub Classroom repository:
    - Your completed `chord_node.py` implementation
    - The `output_dht.txt` file containing the test results
    - A report in `.md` (Markdown) format

## Grading Criteria

-   Basic Chord Protocol (create, join, stabilize, fix_fingers) (4 points)
    -   Must pass the tests in `create_chord_network` (correct ring creation, stabilization, and finger table setup).
    -   Manual inspection will be done on finger table correctness and node routing behavior.
-   Key Storage and Retrieval (4 points)
    -   Must pass the tests in `test_chord_key_storage` and `test_edge_cases` (correct key-value storage, retrieval, handling of non-existent and duplicate keys).
-   Key Transfers Upon Node Join (2 points)
    -   Must pass the test in `test_key_transfer_with_new_node` (correct transfer of responsibility and key redistribution after a new node joins).
-   Implementation Report (2 points)
    -   Provide a brief explanation for the following functions: `find_successor`, `closest_preceding_node`, `create`, `join`, `stabilize`, `notify`, `fix_fingers`, `put`, `get`, `transfer_keys`
    -   0.2 points per function
-   Finger Table Failure Recovery (Bonus 2 points)
    -   Pass the test in `test_node_failure_recovery` (correctly detect node failure, update predecessor/finger tables, and maintain network stability).
    -   Bonus points will be added to your assignment score, but the total score for all assignments (including bonus points) cannot exceed 60 points (60% of the final grade).

Good luck, and enjoy implementing your distributed hash table!

---

Author: Juan Albert Wibowo
