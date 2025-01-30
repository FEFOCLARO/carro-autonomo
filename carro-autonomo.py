import pygame
import numpy as np
import random
from collections import defaultdict
import time

class CarEnvironment:
    def __init__(self, width=800, height=600):
        # Inicializa a interface do Pygame com essas dimensões
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Carro automatizado")
        
        # Define as cores que usaremos
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
        
        # Define a track dimensions and grid size first
        self.WIDTH = width
        self.HEIGHT = height
        self.GRID_SIZE = 40  # Size of each grid cell
        self.COLS = width // self.GRID_SIZE
        self.ROWS = height // self.GRID_SIZE
        
        # Defining sizes relative to GRID_SIZE
        self.CAR_SIZE = int(self.GRID_SIZE * 0.8)  # Car will occupy 80% of cell
        self.WALL_SIZE = self.GRID_SIZE  # Walls occupy entire cell
        self.GOAL_SIZE = int(self.GRID_SIZE * 0.9)  # Goal occupies 90% of cell
        
        # Create the track layout - 1 represents walls, 0 represents valid path
        self.track = self.create_track()
        
        # Define starting position and goal
        self.start_pos = (1, 1)  # Top-left corner (avoiding walls)
        self.goal_pos = (self.COLS-2, self.ROWS-2)  # Bottom-right corner
        self.car_pos = self.start_pos
        
        # Track statistics
        self.episode = 0
        self.steps = 0
        self.best_episode = float('inf')

    def create_track(self):
        """Creates the track layout with walls and obstacles"""
        track = np.zeros((self.ROWS, self.COLS))
        
        # Create outer walls
        track[0, :] = 1  # Top wall
        track[-1, :] = 1  # Bottom wall
        track[:, 0] = 1  # Left wall
        track[:, -1] = 1  # Right wall
        
        # Add some internal walls for an interesting path
        # Verificando os limites antes de adicionar as paredes
        max_col = self.COLS - 1 
        max_row = self.ROWS - 1
        
        # Vertical walls
        track[3:8, 5] = 1  # First vertical wall
        track[5:10, 10] = 1   # Second vertical wall
        track[4:9, 15] = 1  # Third vertical wall
        
        # Horizontal walls
        track[5, 5:8] = 1  # First horizontal wall
        track[8, 10:13] = 1  # Second horizontal wall
        track[11, 13:16] = 1  # Third horizontal wall
        
        return track

    def get_state(self):
        """Converts the car's position into a state representation"""
        return self.car_pos

    def get_valid_actions(self):
        """Returns list of valid actions from current position"""
        valid = []
        x, y = self.car_pos
        
        # Check each possible move (up, right, down, left)
        possible_moves = [
            ('up', (x, y-1)),
            ('right', (x+1, y)),
            ('down', (x, y+1)),
            ('left', (x-1, y))
        ]
        
        for action, (next_x, next_y) in possible_moves:
            if (0 <= next_x < self.COLS and 
                0 <= next_y < self.ROWS and 
                not self.track[next_y, next_x]):
                valid.append(action)
                
        return valid

    def step(self, action):
        """Executes an action and returns new state, reward, and done flag"""
        self.steps += 1
        x, y = self.car_pos
        
        # Update position based on action
        if action == 'up': y -= 1
        elif action == 'right': x += 1
        elif action == 'down': y += 1
        elif action == 'left': x -= 1
        
        # Check if we hit a wall
        if self.track[y, x] == 1:
            return self.get_state(), -10, True
        
        # Update car position
        self.car_pos = (x, y)
        
        # Check if we reached the goal
        if self.car_pos == self.goal_pos:
            if self.steps < self.best_episode:
                self.best_episode = self.steps
            return self.get_state(), 100, True
        
        # Small negative reward to encourage finding shortest path
        return self.get_state(), -0.1, False

    def reset(self):
        """Resets the car to starting position"""
        self.car_pos = self.start_pos
        self.steps = 0
        return self.get_state()

    def render(self):
        """Draws the current state of the environment"""
        self.screen.fill(self.WHITE)
        
        # Draw track
        for y in range(self.ROWS):
            for x in range(self.COLS):
                if self.track[y, x] == 1:
                    pygame.draw.rect(self.screen, self.BLACK,
                                  (x * self.GRID_SIZE, 
                                   y * self.GRID_SIZE,
                                   self.WALL_SIZE, 
                                   self.WALL_SIZE))
        
        # Draw goal with larger size and centered in cell
        goal_x = self.goal_pos[0] * self.GRID_SIZE + (self.GRID_SIZE - self.GOAL_SIZE) // 2
        goal_y = self.goal_pos[1] * self.GRID_SIZE + (self.GRID_SIZE - self.GOAL_SIZE) // 2
        pygame.draw.rect(self.screen, self.GREEN,
                        (goal_x, goal_y,
                         self.GOAL_SIZE, 
                         self.GOAL_SIZE))
        
        # Draw car with larger size and centered in cell
        car_x = self.car_pos[0] * self.GRID_SIZE + (self.GRID_SIZE - self.CAR_SIZE) // 2
        car_y = self.car_pos[1] * self.GRID_SIZE + (self.GRID_SIZE - self.CAR_SIZE) // 2
        pygame.draw.rect(self.screen, self.BLUE,
                        (car_x, car_y,
                         self.CAR_SIZE, 
                         self.CAR_SIZE))
        
        # Display episode and steps information
        font = pygame.font.Font(None, 36)
        text = font.render(f'Episode: {self.episode}  Steps: {self.steps}  Best: {self.best_episode}', 
                          True, self.BLACK)
        self.screen.blit(text, (10, 10))
        
        pygame.display.flip()


class QLearningAgent:
    def __init__(self, learning_rate=0.1, discount_factor=0.95, epsilon=1.0):
        self.q_table = defaultdict(lambda: defaultdict(float))
        self.lr = learning_rate  # How much new information overrides old
        self.gamma = discount_factor  # How much future rewards matter
        self.epsilon = epsilon  # Exploration rate
        self.min_epsilon = 0.01
        self.epsilon_decay = 0.995

    def choose_action(self, state, valid_actions):
        """Selects action using epsilon-greedy policy"""
        if random.random() < self.epsilon:
            return random.choice(valid_actions)
        else:
            # Choose the action with highest Q-value
            return max(valid_actions, 
                      key=lambda a: self.q_table[state][a])

    def learn(self, state, action, reward, next_state, next_valid_actions):
        """Updates Q-value for state-action pair"""
        # Find the maximum Q-value for the next state
        next_max = max([self.q_table[next_state][a] 
                       for a in next_valid_actions], default=0)
        
        # Update Q-value using the Bellman equation
        current_q = self.q_table[state][action]
        new_q = current_q + self.lr * (
            reward + self.gamma * next_max - current_q)
        self.q_table[state][action] = new_q
        
        # Decay exploration rate
        self.epsilon = max(self.min_epsilon, 
                          self.epsilon * self.epsilon_decay)

def main():
    # Create environment and agent
    env = CarEnvironment()
    agent = QLearningAgent()
    
    # Training loop
    running = True
    clock = pygame.time.Clock()
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        # Reset environment for new episode
        state = env.reset()
        done = False
        env.episode += 1
        
        while not done and running:
            # Get valid actions and choose one
            valid_actions = env.get_valid_actions()
            action = agent.choose_action(state, valid_actions)
            
            # Take action and observe result
            next_state, reward, done = env.step(action)
            
            # Learn from the experience
            next_valid_actions = env.get_valid_actions()
            agent.learn(state, action, reward, next_state, next_valid_actions)
            
            state = next_state
            
            # Render the environment
            env.render()
            clock.tick(30)  # Control simulation speed
            
    pygame.quit()

if __name__ == "__main__":
    main()