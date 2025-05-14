import socket
import threading
import json
import time
import math

class Node:
    def __init__(self, node_id, host, port, m=5):
        self.node_id = node_id
        self.host = host
        self.port = port
        self.m = m  # number of bits in the identifier
        self.predecessor = None  # Will store (node_id, host, port) tuple
        self.successor = (node_id, host, port)  # initially points to self address
        # finger table: indices 1..m; initialize each entry to self address
        self.finger = [None] * (m + 1)
        for i in range(1, m + 1):
            self.finger[i] = (node_id, host, port)
        self.next = 1  # next stores the index of the finger to fix
        self.data = {}  # Add storage for key-value pairs
        self.running = True  # Add control flag
        
        # Initialize the server socket before starting the thread
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Start the TCP server thread after server socket is initialized
        self.server_thread = threading.Thread(target=self.run_server)
        self.server_thread.daemon = True
        self.server_thread.start()

    # Helper function to check if 'id' is in the half-open interval (start, end]
    def in_interval(self, id, start, end, inclusive_right=True):
        """
        Check if 'id' falls within the interval (start, end] on the Chord ring.
        
        Args:
            id: The identifier to check
            start: Start of the interval (exclusive)
            end: End of the interval (inclusive if inclusive_right is True)
            inclusive_right: Whether the right endpoint is inclusive
            
        Returns:
            True if id is in the interval, False otherwise
        """
        # TODO: Implement interval check, considering ring wraparound
        if start < end:
            if inclusive_right:
                return start < id and id <= end
            else:
                return start < id and id < end
        else:  # start >= end, then the interval wraps around
            if inclusive_right:
                return id > start or id <= end
            else:
                return id > start or id < end

    def find_successor(self, id):
        """
        Find the successor node for a given identifier.
        
        Args:
            id: The identifier to find successor for
            
        Returns:
            (node_id, host, port) of the successor
        """
        # TODO
        if self.in_interval(id, self.node_id, self.successor[0]):
            return self.successor
        else:
            # Find the closest preceding node and delegate the search
            n_prime = self.closest_preceding_node(id)
            if n_prime == (self.node_id, self.host, self.port):
                return self.successor
            else:
                return self.remote_call(n_prime, "find_successor", {"id": id})

    def closest_preceding_node(self, id):
        """
        Find the closest preceding node for a given identifier.
        
        Args:
            id: The identifier to find closest preceding node for
            
        Returns:
            (node_id, host, port) of the closest preceding node
        """
        # TODO
        # Iterate through the finger table in reverse order
        for i in range(self.m, 0, -1):
            finger_node = self.finger[i]
            if finger_node and self.in_interval(finger_node[0], self.node_id, id, inclusive_right=False):
                return finger_node
        # If no suitable node is found, return self
        return (self.node_id, self.host, self.port)

    def create(self):
        """
        Create a new Chord ring.
        """
        # TODO
        self.predecessor = None
        self.successor = (self.node_id, self.host, self.port)
        for i in range(1, self.m + 1):
            self.finger[i] = (self.node_id, self.host, self.port)

    def join(self, existing_node_addr):
        """
        Join an existing Chord ring.
        
        Args:
            existing_node_addr: (node_id, host, port) of a node in the existing ring
        """
        # TODO
        self.predecessor = None
        # Find this node's successor through the existing node
        successor = self.remote_call(existing_node_addr, "find_successor", {"id": self.node_id})
        if successor:
            self.successor = successor
            self.remote_call(successor, "transfer_keys", {
                "node_id": self.node_id,
                "host": self.host,
                "port": self.port
            })
        else:
            raise Exception("Failed to join the ring")
    

    def ping(self, node_addr):
        """
        Newly Added.
        
        Check if the target node is alive by sending a 'ping' request.
        """
        try:
            response = self.remote_call(node_addr, "ping", {})
            return response == "pong"
        except:
            return False

    def stabilize(self):
        """
        Verify if this node's immediate successor is consistent, and tells the successor about this node.
        """
        # TODO      

        # Check if the successor is accessible, if not, then search for the first alive nodes in the finger table
        if not self.ping(self.successor):
            for i in range(1, self.m + 1):
                if self.finger[i] and self.ping(self.finger[i]):
                    self.successor = self.finger[i]
                    break
            else:
                # in the condition no alive nodes (Just for test use, )
                self.successor = (self.node_id, self.host, self.port)

        try:
            # Get the successor's predecessor
            x = self.remote_call(self.successor, "get_predecessor", {})
            if x and self.in_interval(x[0], self.node_id, self.successor[0], inclusive_right=False):
                self.successor = x  # Update successor if x is between self and current successor
            # Notify the successor that this node might be its predecessor
            self.remote_call(self.successor, "notify", {
                "node_id": self.node_id,
                "host": self.host,
                "port": self.port
            })
        except Exception as e:
            print(f"Stabilize failed: {e}")



    def notify(self, node_addr):
        """
        Called by another node claiming to be this node's predecessor.
        
        Args:
            node_addr: (node_id, host, port) of the potential predecessor
        """
        # TODO
        if self.predecessor is None or self.in_interval(node_addr[0], self.predecessor[0], self.node_id, inclusive_right=False):
            self.predecessor = node_addr

    def fix_fingers(self):
        """
        Refresh finger table entries. self.next stores the index of the finger to fix.
        """
        # TODO
        self.next += 1
        if self.next > self.m:
            self.next = 1
        # Calculate the identifier for the next finger entry
        finger_id = (self.node_id + (2 ** (self.next - 1))) % (2 ** self.m)
        self.finger[self.next] = self.find_successor(finger_id)

    def check_predecessor(self):
        """
        Check if the predecessor has failed.
        """
        # TODO
        if self.predecessor:
            try:
                response = self.remote_call(self.predecessor, "ping", {})
                if response != "pong":
                    self.predecessor = None
            except Exception:
                self.predecessor = None
    
    # Helper function to hash a key to chord ring space
    def hash_key(self, key):
        """
        Hash a key to an identifier in the chord ring space.
        
        Args:
            key: The key to hash
            
        Returns:
            The hashed identifier in the range [0, 2^m - 1]
        """
        # TODO
        return hash(key) % (2 ** self.m)
    
    def put(self, key, value):
        """
        Store a key-value pair in the DHT.
        
        Args:
            key: The key to store
            value: The value to store
            
        Returns:
            True if the operation succeeded, False otherwise
        """
        # TODO
        id = self.hash_key(key)
        successor = self.find_successor(id)
        if successor == (self.node_id, self.host, self.port):
            # Store locally if this node is responsible
            self.data[key] = value
            return True
        else:
            # Delegate to the responsible node
            return self.remote_call(successor, "store", {"key": key, "value": value})
    
    def get(self, key):
        """
        Retrieve a value from the DHT.
        
        Args:
            key: The key to retrieve
            
        Returns:
            The associated value, or None if the key is not found
        """
        # TODO
        id = self.hash_key(key)
        successor = self.find_successor(id)
        if successor == (self.node_id, self.host, self.port):
            # Retrieve locally if this node is responsible
            return self.data.get(key)
        else:
            # Delegate to the responsible node
            return self.remote_call(successor, "retrieve", {"key": key})

    def transfer_keys(self, new_node_addr):
        """
        Transfer keys that now belong to the new node.
        
        Args:
            new_node_addr: (node_id, host, port) of the new node
        """
        # TODO
        new_node_id, _, _ = new_node_addr
        # if predecessor is none, then use self to start
        if self.predecessor:
            pred_id = self.predecessor[0]
        else:
            pred_id = self.node_id

        # Identify keys that belong to the new node's range
        keys_to_transfer = {}
        for key, value in self.data.items():
            hashed_key = self.hash_key(key) 
            if self.in_interval(hashed_key, pred_id, new_node_id):
                keys_to_transfer[key] = value
                
        # Transfer each key-value pair to the new node and remove locally
        for key, value in keys_to_transfer.items():
            self.remote_call(new_node_addr, "store", {"key": key, "value": value})
            del self.data[key]

    # Remote call helper: sends a JSON request to a given node and waits for a response.
    def remote_call(self, node_addr, command, params, timeout=5.0):
        """
        Make a remote call to another node.
        
        Args:
            node_addr: (node_id, host, port) of the target node
            command: The command to execute
            params: Parameters for the command
            timeout: Socket timeout in seconds
            
        Returns:
            The result of the remote call, or None if it failed
        """
        # Implementation provided - handles both local and remote calls
        node_id, host, port = node_addr
        
        # Check if the node is us
        if node_id == self.node_id and host == self.host and port == self.port:
            # Local call handling
            if command == "find_successor":
                id = params.get("id")
                return self.find_successor(id)
            elif command == "closest_preceding_node":
                id = params.get("id")
                return self.closest_preceding_node(id)
            elif command == "get_predecessor":
                return self.predecessor
            elif command == "notify":
                node_id = params.get("node_id")
                host = params.get("host")
                port = params.get("port")
                self.notify((node_id, host, port))
                return (self.node_id, self.host, self.port)
            elif command == "ping":
                return "pong"
            elif command == "store":
                key = params.get("key")
                value = params.get("value")
                self.data[key] = value
                return True
            elif command == "retrieve":
                key = params.get("key")
                return self.data.get(key)
            elif command == "get_data":
                return self.data
            elif command == "transfer_keys":
                node_id = params.get("node_id")
                host = params.get("host")
                port = params.get("port")
                self.transfer_keys((node_id, host, port))
                return True
            else:
                return "Unknown command"
        
        # Check if node is stopped or unavailable
        if node_id == -1 or host == "" or port == 0:
            raise Exception(f"Cannot contact node {node_id} - node address is invalid")
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)  # Added timeout parameter
                s.connect((host, port))
                message = json.dumps({"command": command, "params": params})
                s.sendall(message.encode())
                data = s.recv(4096)
                if data:
                    response = json.loads(data.decode())
                    return response.get("result")
            return None
        except (socket.timeout, ConnectionRefusedError, OSError) as e:
            raise Exception(f"Failed to connect to node {node_id} at {host}:{port} - {str(e)}")

    # TCP server: listens for incoming requests and handles them in separate threads.
    def run_server(self):
        # Implementation provided - handles TCP server operation
        try:
            # Socket is already initialized in __init__, just bind and listen
            self.server.bind((self.host, self.port))
            self.server.listen(5)
            
            while self.running:
                try:
                    self.server.settimeout(1)  # Add timeout to check running flag
                    client, addr = self.server.accept()
                    client_thread = threading.Thread(target=self.handle_client, args=(client,))
                    client_thread.daemon = True
                    client_thread.start()
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:  # Only print error if we're supposed to be running
                        print(f"Server error: {e}")
        except Exception as e:
            print(f"Failed to start server: {e}")

    def handle_client(self, client_socket):
        # Implementation provided - handles incoming client connections
        try:
            data = client_socket.recv(4096)
            if not data:
                client_socket.close()
                return
            request = json.loads(data.decode())
            command = request.get("command")
            params = request.get("params")
            result = None

            if command == "find_successor":
                id = params.get("id")
                result = self.find_successor(id)
            elif command == "closest_preceding_node":
                id = params.get("id")
                result = self.closest_preceding_node(id)
            elif command == "get_predecessor":
                result = self.predecessor
            elif command == "notify":
                node_id = params.get("node_id")
                host = params.get("host")
                port = params.get("port")
                node_addr = (node_id, host, port)
                self.notify(node_addr)
                result = (self.node_id, self.host, self.port)
            elif command == "ping":
                result = "pong"
            elif command == "store":
                # Handle store operation
                key = params.get("key")
                value = params.get("value")
                self.data[key] = value
                result = True
            elif command == "retrieve":
                # Handle retrieve operation
                key = params.get("key")
                result = self.data.get(key)
            elif command == "get_data":
                # Return all data stored in this node
                result = self.data
            elif command == "transfer_keys":
                # Handle transfer_keys operation
                node_id = params.get("node_id")
                host = params.get("host")
                port = params.get("port")
                node_addr = (node_id, host, port)
                self.transfer_keys(node_addr)
                result = True
            else:
                result = "Unknown command"

            response = json.dumps({"result": result})
            client_socket.sendall(response.encode())
        except Exception as e:
            error_response = json.dumps({"result": None, "error": str(e)})
            client_socket.sendall(error_response.encode())
        finally:
            client_socket.close()

    def stop(self):
        """Stop the node's server thread and mark as stopped."""
        self.running = False
        if self.server:
            self.server.close() 