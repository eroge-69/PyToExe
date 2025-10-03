import socket
import threading
import pickle
import struct
from perlin_noise import PerlinNoise

HOST = "127.0.0.1"
PORT = 5555

# Game constants
WORLD_WIDTH = 200
WORLD_HEIGHT = 50
TILE_SIZE = 16
BUFFER_SIZE = 8192

class GameServer:
    def __init__(self):
        self.world = self.generate_world()
        self.players = {}
        self.player_lock = threading.Lock()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
    def generate_world(self):
        """Generate terrain using Perlin noise"""
        noise = PerlinNoise(octaves=4)
        world = []
        
        for x in range(WORLD_WIDTH):
            col = []
            # Normalize noise to 0-1 range and scale to world height
            height = int((noise(x / WORLD_WIDTH) + 1) / 2 * 20) + 10
            
            for y in range(WORLD_HEIGHT):
                if y < height - 3:
                    col.append("stone")
                elif y < height:
                    col.append("dirt")
                else:
                    col.append("air")
            world.append(col)
        
        return world
    
    def send_data(self, conn, data):
        """Send data with length prefix to avoid truncation"""
        try:
            serialized_data = pickle.dumps(data)
            # Prefix with data length
            message = struct.pack('>I', len(serialized_data)) + serialized_data
            conn.sendall(message)
        except Exception as e:
            print(f"Error sending data: {e}")
    
    def recv_data(self, conn):
        """Receive data with length prefix"""
        try:
            # First receive the length prefix (4 bytes)
            raw_length = conn.recv(4)
            if not raw_length:
                return None
            data_length = struct.unpack('>I', raw_length)[0]
            
            # Receive the actual data
            data = b''
            while len(data) < data_length:
                chunk = conn.recv(min(BUFFER_SIZE, data_length - len(data)))
                if not chunk:
                    return None
                data += chunk
            
            return pickle.loads(data)
        except Exception as e:
            print(f"Error receiving data: {e}")
            return None
    
    def handle_client(self, conn, addr):
        """Handle individual client connection"""
        print(f"[NEW CONNECTION] {addr}")
        
        # Initialize player with thread-safe locking
        with self.player_lock:
            self.players[addr] = {
                "x": 10.0, 
                "y": 0.0, 
                "name": f"Player_{len(self.players)}",
                "addr": addr
            }
        
        try:
            # Send initial world data to client
            initial_data = {
                "world": self.world,
                "players": self.players.copy(),
                "world_width": WORLD_WIDTH,
                "world_height": WORLD_HEIGHT
            }
            self.send_data(conn, initial_data)
            
            while True:
                # Receive player data
                received = self.recv_data(conn)
                if received is None:
                    break
                
                # Update player position with thread safety
                with self.player_lock:
                    if addr in self.players:
                        self.players[addr]["x"] = received.get("x", self.players[addr]["x"])
                        self.players[addr]["y"] = received.get("y", self.players[addr]["y"])
                
                # Send game state back to client
                response = {
                    "players": self.players.copy(),  # Send copy to avoid race conditions
                    "world_width": WORLD_WIDTH,
                    "world_height": WORLD_HEIGHT
                }
                self.send_data(conn, response)
                    
        except (ConnectionResetError, ConnectionAbortedError) as e:
            print(f"Connection lost with {addr}: {e}")
        except Exception as e:
            print(f"Unexpected error with {addr}: {e}")
        finally:
            # Clean up player with thread safety
            with self.player_lock:
                if addr in self.players:
                    del self.players[addr]
            conn.close()
            print(f"[DISCONNECT] {addr}")
    
    def start(self):
        """Start the game server"""
        try:
            self.server_socket.bind((HOST, PORT))
            self.server_socket.listen()
            print(f"[LISTENING] Server on {HOST}:{PORT}")
            
            while True:
                conn, addr = self.server_socket.accept()
                client_thread = threading.Thread(
                    target=self.handle_client, 
                    args=(conn, addr), 
                    daemon=True
                )
                client_thread.start()
                print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
                
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self.server_socket.close()

if __name__ == "__main__":
    server = GameServer()
    server.start()