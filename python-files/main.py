import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
import random
import pickle
import sys

class ConnectFour:
    def __init__(self):
        self.board = np.zeros((6, 7), dtype=int)
        self.current_player = 1

    def make_move(self, col):
        for row in range(5, -1, -1):
            if self.board[row][col] == 0:
                self.board[row][col] = self.current_player
                self.current_player = -self.current_player
                return True
        return False

    def check_win(self, player):
        # Horizontal
        for r in range(6):
            for c in range(4):
                if np.all(self.board[r, c:c+4] == player):
                    return True
        # Vertical
        for r in range(3):
            for c in range(7):
                if np.all(self.board[r:r+4, c] == player):
                    return True
        # Diagonal /
        for r in range(3):
            for c in range(4):
                if all(self.board[r+i][c+i] == player for i in range(4)):
                    return True
        # Diagonal \
        for r in range(3):
            for c in range(3, 7):
                if all(self.board[r+i][c-i] == player for i in range(4)):
                    return True
        return False

    def is_draw(self):
        return np.all(self.board != 0)

    def get_valid_moves(self):
        return [c for c in range(7) if self.board[0][c] == 0]

    def display(self):
        print("Board:")
        for row in self.board:
            print(' '.join(['.' if x == 0 else 'X' if x == 1 else 'O' for x in row]))
        print("Columns: 0 1 2 3 4 5 6")

class DQN(nn.Module):
    def __init__(self):
        super(DQN, self).__init__()
        self.conv1 = nn.Conv2d(1, 64, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(128, 256, kernel_size=3, padding=1)
        self.fc1 = nn.Linear(256 * 6 * 7, 512)
        self.fc2 = nn.Linear(512, 7)

    def forward(self, x):
        x = x.view(-1, 1, 6, 7)  # batch, channels, height, width
        x = torch.relu(self.conv1(x))
        x = torch.relu(self.conv2(x))
        x = torch.relu(self.conv3(x))
        x = x.view(-1, 256 * 6 * 7)
        x = torch.relu(self.fc1(x))
        return self.fc2(x)

class Agent:
    def __init__(self, epsilon=1.0, epsilon_min=0.01, epsilon_decay=0.995, gamma=0.99, batch_size=128, replay_size=200000):
        self.model = DQN()
        self.target_model = DQN()
        self.target_model.load_state_dict(self.model.state_dict())
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.0005)
        self.loss_fn = nn.MSELoss()
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.gamma = gamma
        self.batch_size = batch_size
        self.memory = deque(maxlen=replay_size)
        self.update_target_every = 200
        self.steps = 0
        self.double_dqn = True

    def get_action(self, state, valid_moves, explore=True):
        epsilon = self.epsilon if explore else 0.0
        if random.random() < epsilon:
            return random.choice(valid_moves)
        state_tensor = torch.tensor(state.reshape(6, 7), dtype=torch.float).unsqueeze(0)
        with torch.no_grad():
            q_values = self.model(state_tensor)[0].numpy()
        masked_q = np.full(7, -np.inf)
        for m in valid_moves:
            masked_q[m] = q_values[m]
        return np.argmax(masked_q)

    def add_experience(self, state, action, reward, next_state, done, next_valid_moves):
        self.memory.append((state, action, reward, next_state, done, next_valid_moves))

    def train(self):
        if len(self.memory) < self.batch_size:
            return
        batch = random.sample(self.memory, self.batch_size)
        states = np.array([b[0] for b in batch])
        actions = torch.tensor([b[1] for b in batch], dtype=torch.long)
        rewards = torch.tensor([b[2] for b in batch], dtype=torch.float)
        next_states = np.array([b[3] for b in batch])
        dones = torch.tensor([b[4] for b in batch], dtype=torch.float)
        next_valids = [b[5] for b in batch]

        states_tensor = torch.tensor(states.reshape(-1, 6, 7), dtype=torch.float)
        next_states_tensor = torch.tensor(next_states.reshape(-1, 6, 7), dtype=torch.float)

        q_values = self.model(states_tensor).gather(1, actions.unsqueeze(1)).squeeze(1)

        with torch.no_grad():
            if self.double_dqn:
                next_q_model = self.model(next_states_tensor)
                next_q_target = self.target_model(next_states_tensor)
                max_next_q = torch.zeros(self.batch_size)
                for i in range(self.batch_size):
                    if dones[i]:
                        max_next_q[i] = 0
                    else:
                        masked = torch.full((7,), -float('inf'))
                        for m in next_valids[i]:
                            masked[m] = next_q_model[i][m]
                        next_action = masked.argmax()
                        max_next_q[i] = next_q_target[i][next_action]
            else:
                next_q_target = self.target_model(next_states_tensor)
                max_next_q = torch.zeros(self.batch_size)
                for i in range(self.batch_size):
                    if dones[i]:
                        max_next_q[i] = 0
                    else:
                        masked = torch.full((7,), -float('inf'))
                        for m in next_valids[i]:
                            masked[m] = next_q_target[i][m]
                        max_next_q[i] = masked.max()

        target_q = rewards + (1 - dones) * self.gamma * (-max_next_q) 

        loss = self.loss_fn(q_values, target_q)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        self.steps += 1
        if self.steps % self.update_target_every == 0:
            self.target_model.load_state_dict(self.model.state_dict())

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def save(self, path):
        torch.save(self.model.state_dict(), path + '_model.pth')
        torch.save(self.target_model.state_dict(), path + '_target_model.pth')
        with open(path + '_agent.pkl', 'wb') as f:
            pickle.dump({
                'epsilon': self.epsilon,
                'steps': self.steps
            }, f)

    def load(self, path):
        self.model.load_state_dict(torch.load(path + '_model.pth'))
        self.target_model.load_state_dict(torch.load(path + '_target_model.pth'))
        with open(path + '_agent.pkl', 'rb') as f:
            data = pickle.load(f)
            self.epsilon = data['epsilon']
            self.steps = data['steps']

def train_self_play(agent, num_games, log_every=100):
    for game_num in range(1, num_games + 1):
        game = ConnectFour()
        states, actions, rewards, next_states, dones, next_valids = [], [], [], [], [], []
        while True:
            board = game.board.copy()
            if game.current_player == -1:
                board = -board
            state = board.flatten()
            valid_moves = game.get_valid_moves()
            if not valid_moves:
                break
            action = agent.get_action(state, valid_moves, explore=True)
            game.make_move(action)
            next_board = game.board.copy()
            if game.current_player == -1:
                next_board = -next_board
            next_state = next_board.flatten()
            next_valid_moves = game.get_valid_moves()
            player_just_moved = -game.current_player
            done = False
            reward = 0
            if game.check_win(player_just_moved):
                reward = 1
                done = True
            elif game.is_draw():
                reward = 0
                done = True

            states.append(state)
            actions.append(action)
            rewards.append(reward)
            next_states.append(next_state)
            dones.append(done)
            next_valids.append(next_valid_moves)
            if done:
                break
            
        for i in range(len(states)):
            agent.add_experience(states[i], actions[i], rewards[i], next_states[i], dones[i], next_valids[i])
        agent.train()  
        if game_num % log_every == 0:
            print(f"Completed {game_num} self-play games. Epsilon: {agent.epsilon:.4f}")

def play_against_human(agent, human_player=1):
    game = ConnectFour()
    if human_player == -1:
        game.current_player = 1 
        game.current_player = -1 if human_player == 1 else 1
    agent_player = -human_player
    while True:
        game.display()
        if game.current_player == human_player:
            try:
                col = int(input("Enter your column (0-6): "))
            except ValueError:
                print("Invalid input. Try again.")
                continue
            if col not in game.get_valid_moves():
                print("Invalid move. Try again.")
                continue
            game.make_move(col)
        else:
            board = game.board.copy()
            if game.current_player == -1:
                board = -board
            state = board.flatten()
            valid_moves = game.get_valid_moves()
            action = agent.get_action(state, valid_moves, explore=False)
            print(f"Agent plays column {action}")
            game.make_move(action)
        player_just_moved = -game.current_player
        if game.check_win(player_just_moved):
            game.display()
            winner = "Human" if player_just_moved == human_player else "Agent"
            print(f"{winner} wins!")
            break
        if game.is_draw():
            game.display()
            print("It's a draw!")
            break

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "load":
        agent = Agent()
        agent.load("connect_four_agent")
        print("Loaded agent from file.")
    else:
        agent = Agent()
    
    while True:
        print("\nOptions:")
        print("1: Train via self-play")
        print("2: Play against human (human starts)")
        print("3: Play against human (agent starts)")
        print("4: Save agent")
        print("5: Load agent")
        print("6: Exit")
        choice = input("Choose an option: ")
        if choice == "1":
            num_games = int(input("Enter number of self-play games: "))
            train_self_play(agent, num_games)
        elif choice == "2":
            play_against_human(agent, human_player=1)
        elif choice == "3":
            play_against_human(agent, human_player=-1)
        elif choice == "4":
            agent.save("connect_four_agent")
            print("Agent saved.")
        elif choice == "5":
            agent = Agent()
            agent.load("connect_four_agent")
            print("Agent loaded.")
        elif choice == "6":
            break
        else:
            print("Invalid choice.")