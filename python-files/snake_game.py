import pygame
import socket
import json
import threading
import random

# Game constants
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
GRID_SIZE = 16
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Camera constants
CAMERA_MARGIN_PIXELS = 80 # Margin in pixels (5 grid units * 16 pixels/grid unit)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0) # Apple color
PURPLE = (128, 0, 128) # Grape color

class SnakeClient:
    def __init__(self, server_ip, server_port, player_name="Player"):
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket.settimeout(0.1) # Small timeout for non-blocking receive
        self.player_name = player_name
        self.game_state = {"snakes": {}, "apples": [], "grapes": []}
        self.running = True
        # Bind to a random port to get a unique address for this client
        self.client_socket.bind(("0.0.0.0", 0))
        self.my_addr = self.client_socket.getsockname() 
        self.my_player_id = str(self.my_addr) # Use this as our unique ID for the server

        # Camera offset
        self.camera_offset_x = 0
        self.camera_offset_y = 0

        # Start receiving thread
        self.receive_thread = threading.Thread(target=self._receive_data)
        self.receive_thread.daemon = True
        self.receive_thread.start()

    def _receive_data(self):
        while self.running:
            try:
                data, _ = self.client_socket.recvfrom(4096)
                self.game_state = json.loads(data.decode())
            except socket.timeout:
                pass
            except json.JSONDecodeError:
                print("Received malformed JSON from server")
            except Exception as e:
                if self.running:
                    print(f"Error receiving data: {e}")

    def send_message(self, message_type, payload={}):
        message = {"type": message_type, **payload}
        self.client_socket.sendto(json.dumps(message).encode(), (self.server_ip, self.server_port))

    def join_game(self):
        self.send_message("join", {"name": self.player_name})

    def send_input(self, direction):
        self.send_message("input", {"direction": direction})

    def get_my_snake_data(self):
        return self.game_state["snakes"].get(self.my_player_id)

    def update_camera(self, my_snake_head):
        head_pixel_x = my_snake_head[0] * GRID_SIZE
        head_pixel_y = my_snake_head[1] * GRID_SIZE

        # Adjust camera_offset_x
        if head_pixel_x - self.camera_offset_x < CAMERA_MARGIN_PIXELS:
            self.camera_offset_x = head_pixel_x - CAMERA_MARGIN_PIXELS
        elif head_pixel_x - self.camera_offset_x > SCREEN_WIDTH - CAMERA_MARGIN_PIXELS - GRID_SIZE:
            self.camera_offset_x = head_pixel_x - (SCREEN_WIDTH - CAMERA_MARGIN_PIXELS - GRID_SIZE)
        
        # Adjust camera_offset_y
        if head_pixel_y - self.camera_offset_y < CAMERA_MARGIN_PIXELS:
            self.camera_offset_y = head_pixel_y - CAMERA_MARGIN_PIXELS
        elif head_pixel_y - self.camera_offset_y > SCREEN_HEIGHT - CAMERA_MARGIN_PIXELS - GRID_SIZE:
            self.camera_offset_y = head_pixel_y - (SCREEN_HEIGHT - CAMERA_MARGIN_PIXELS - GRID_SIZE)


    def stop(self):
        self.running = False
        self.receive_thread.join(timeout=1)
        self.client_socket.close()

def get_user_input(prompt, default_value):
    # This function is a placeholder for getting user input in a Pygame-friendly way
    # For now, we'll use a simple input() call, which will block the Pygame window.
    # A more robust solution would involve a Pygame-based input box.
    user_input = input(f"{prompt} (default: {default_value}): ")
    return user_input if user_input else default_value

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pixelated Snake")
    clock = pygame.time.Clock()

    font = pygame.font.Font(None, 24)

    # Get server IP and port from user
    server_ip = get_user_input("Enter server IP address", "127.0.0.1")
    server_port_str = get_user_input("Enter server port", "12345")
    try:
        server_port = int(server_port_str)
    except ValueError:
        print("Invalid port, using default 12345")
        server_port = 12345

    player_name = get_user_input("Enter your player name", f"Player_{random.randint(1, 100)}")

    client = SnakeClient(server_ip, server_port, player_name)
    client.join_game()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    client.send_input((0, -1))
                elif event.key == pygame.K_DOWN:
                    client.send_input((0, 1))
                elif event.key == pygame.K_LEFT:
                    client.send_input((-1, 0))
                elif event.key == pygame.K_RIGHT:
                    client.send_input((1, 0))

        screen.fill(BLACK)

        my_snake = client.get_my_snake_data()
        if my_snake and my_snake["body"]:
            client.update_camera(my_snake["body"][0])

        # Draw all snakes from the game state received from the server
        for player_id, snake_data in client.game_state["snakes"].items():
            if snake_data["body"] and not snake_data.get("dead", False):
                color = tuple(snake_data["color"]) # Colors are sent as lists, convert to tuple
                for segment in snake_data["body"]:
                    draw_x = segment[0] * GRID_SIZE - client.camera_offset_x
                    draw_y = segment[1] * GRID_SIZE - client.camera_offset_y
                    # Only draw if within screen bounds
                    if -GRID_SIZE < draw_x < SCREEN_WIDTH and -GRID_SIZE < draw_y < SCREEN_HEIGHT:
                        pygame.draw.rect(screen, color, (draw_x, draw_y, GRID_SIZE, GRID_SIZE))

        # Draw apples
        for apple_pos in client.game_state["apples"]:
            draw_x = apple_pos[0] * GRID_SIZE - client.camera_offset_x
            draw_y = apple_pos[1] * GRID_SIZE - client.camera_offset_y
            if -GRID_SIZE < draw_x < SCREEN_WIDTH and -GRID_SIZE < draw_y < SCREEN_HEIGHT:
                pygame.draw.rect(screen, RED, (draw_x, draw_y, GRID_SIZE, GRID_SIZE))

        # Draw grapes
        for grape_pos in client.game_state["grapes"]:
            draw_x = grape_pos[0] * GRID_SIZE - client.camera_offset_x
            draw_y = grape_pos[1] * GRID_SIZE - client.camera_offset_y
            if -GRID_SIZE < draw_x < SCREEN_WIDTH and -GRID_SIZE < draw_y < SCREEN_HEIGHT:
                pygame.draw.rect(screen, PURPLE, (draw_x, draw_y, GRID_SIZE, GRID_SIZE))

        # Display score for current player
        if my_snake:
            score_text = font.render(f"Score: {my_snake["score"]}", True, WHITE)
            screen.blit(score_text, (SCREEN_WIDTH - score_text.get_width() - 10, 10))

        # Display leaderboard
        leaderboard_y = 40
        leaderboard_title = font.render("Leaderboard:", True, WHITE)
        screen.blit(leaderboard_title, (SCREEN_WIDTH - leaderboard_title.get_width() - 10, leaderboard_y))
        leaderboard_y += 20

        # Sort players by score for leaderboard
        sorted_players = sorted(client.game_state["snakes"].items(), key=lambda item: item[1]["score"], reverse=True)

        for player_id, snake_data in sorted_players:
            player_name = snake_data["name"]
            player_score = snake_data["score"]
            player_color = tuple(snake_data["color"])
            leaderboard_entry = font.render(f"{player_name}: {player_score}", True, player_color)
            screen.blit(leaderboard_entry, (SCREEN_WIDTH - leaderboard_entry.get_width() - 10, leaderboard_y))
            leaderboard_y += 20

        pygame.display.flip()

        clock.tick(10) # Game speed

    client.stop()
    pygame.quit()

if __name__ == "__main__":
    main()

