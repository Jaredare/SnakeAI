import torch
import numpy as np 
import random
from collections import deque

from snake import SnakeGameAI, Play_Step_Combo_Contents
from model import Linear_QNet, QTrainer
from helper import plot


# PLOT determines whether or not you will see a real-time graph of the scores and average score of the AI or not.
PLOT = False
# DISPLAY_SCREEN determines whether or not you will see the game being played by the bot every 50 games
DISPLAY_SCREEN = False
# SLEEP_TIME determines how quickly the game will be played on the screen if you choose to display it. It is measured in seconds.
SLEEP_TIME = 0.5
MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001 #recommended 0.001 or 0.01
game = SnakeGameAI()
combo_index = Play_Step_Combo_Contents

class Agent: 

    def __init__(self):
        self.n_games = 0
        self.epsilon = 0 # randomness, overwritten later
        self.gamma = 0.9 # discount rate
        self.memory = deque(maxlen=MAX_MEMORY) # popleft()
        self.model = Linear_QNet(12, 256, 4)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

        
    # Gets the state of the game, what the AI is fed.
    def get_state(self, game, combo, direction):
        state = game.snake_eyes(combo[combo_index.SNAKE], combo[combo_index.FRUIT], direction)
        return state
        # return np.array(state, dtype=int)


    def remember(self, state, action, reward, next_state, death):
        self.memory.append((state, action, reward, next_state, death)) # popleft if MAX_MEMORY is reached


    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, deaths = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, deaths)

    def train_short_memory(self, state, action, reward, next_state, death):
        self.trainer.train_step(state, action, reward, next_state, death)

    def get_action(self, state, direction):
        # random moves: tradeoff between exploration and exploitation
        self.epsilon = 80 - self.n_games
        if random.randint(0, 200) < self.epsilon:
            move = game.random_brain(direction)
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
        
        # This is a note to myself, almost thinking out loud. V
        # We don't return final move, because in the video they use a list that says [0, 0, 0]
        # and they replace one of those with a 1 to show which direction to turn. 
        # We instead return the move because we aren't using a list to determine 
        # which move we take, we're using the number. 
        return move


def train():
    mean_score = 0
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    deaths = []
    agent = Agent()
    game = SnakeGameAI()
    

    play_step_combo, direction = game.reset()
    while True:
        # Get the previous state
        state_old = agent.get_state(game, play_step_combo, direction)

        # Get the move we'll be using
        final_move = agent.get_action(state_old, direction)

        # If the game is a multiple of 50, then enable the screen so we can see what progress has been made.
        if agent.n_games > 1200 and agent.n_games % 50 == 0 and DISPLAY_SCREEN == True:
            list_play_step_combo = list(play_step_combo)

            list_play_step_combo.pop(combo_index.SCREEN)
            screen = True
            list_play_step_combo.insert(combo_index.SCREEN, screen)

            list_play_step_combo.pop(combo_index.SLEEP_TIME)
            sleep_time = SLEEP_TIME
            list_play_step_combo.insert(combo_index.SLEEP_TIME, sleep_time)

            play_step_combo = tuple(list_play_step_combo)
            

        # Perform the move and get the new state
        reward, death, score, play_step_combo, direction = game.play_step(play_step_combo, final_move)
        state_new = agent.get_state(game, play_step_combo, direction)

        # If the game is a multiple of 50, display it's stats.
        if agent.n_games % 50 == 0:
        #and play_step_combo[combo_index.TURN] < 6:
            print(f"Game: {agent.n_games}, Current turn: {play_step_combo[combo_index.TURN]}, Score: {score}, Record: {record}, Average of previous runs: {mean_score:.3f}", end=" ")
            print(f"Snake: {play_step_combo[combo_index.SNAKE]}, Fruit: {play_step_combo[combo_index.FRUIT]}, Direction choice: {final_move}, Reward: {reward}")
        
        # Trains the short memory
        agent.train_short_memory(state_old, final_move, reward, state_new, death)

        # Remember stores these things in memory so that the neural network can learn off of them more in the future with train_long_memory.
        agent.remember(state_old, final_move, reward, state_new, death)

        if death != False:
            # train long memory aka replay memory or experience replay, and optionally plot the result
            if score > record:
                record = score
                agent.model.save()
            agent.n_games += 1
            agent.train_long_memory()
            play_step_combo, direction = game.reset()
            deaths.append(death)
            death = False
            
            total_score += score
            mean_score = total_score / agent.n_games
            if PLOT:
                plot_scores.append(score)
                plot_mean_scores.append(mean_score)
                plot(plot_scores, plot_mean_scores)



if __name__ == "__main__":
    train()
