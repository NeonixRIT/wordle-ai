'''
Modified from: https://github.com/patrickloeber/snake-ai-pytorch/
'''

import torch
import random
import numpy as np

from torch.utils.data import Dataset, DataLoader
from wordle import Wordle, get_state_from_board
from wordle_ai import WordleAI, ALLOWED_WORDS
from collections import deque
from model import Linear_QNet, QTrainer
from helper import plot

MAX_MEMORY = 200_000
BATCH_SIZE = 14855
LR = 0.01

class Agent:

    def __init__(self, device: torch.device | None = None):
        self.n_games = 0
        self.epsilon = 0 # randomness
        self.gamma = 0.9 # discount rate
        self.memory = deque(maxlen=MAX_MEMORY) # popleft()
        self.model = Linear_QNet(61, [780, 26], 14855, device)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def get_state(self, game: Wordle):
        state = get_state_from_board(game.get_board())
        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done)) # popleft if MAX_MEMORY is reached

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)
        # for state, action, reward, nexrt_state, done in mini_sample:
        #     self.trainer.train_step(state, action, reward, next_state, done)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state, game_helper: WordleAI):
        # random moves: tradeoff exploration / exploitation
        x = 14855
        self.epsilon = x - self.n_games
        final_move = 0
        if random.randint(0, int(x * 2.5)) < self.epsilon:
            final_move = np.random.choice(game_helper.get_valid_actions())
        else:
            state0 = torch.tensor(state, dtype=torch.float, device=self.model.device)
            prediction = self.model(state0)
            valid_mask = game_helper.get_valid_action_mask(self.model.device)
            prob_mask = game_helper.get_prob_action_mask(self.model.device)
            masked_prediction = (prediction * prob_mask) + valid_mask
            # for i, val in enumerate(masked_prediction):
            #     if val < -100:
            #         continue
            #     print(f'{i}: {val}', end=', ')
            final_move = torch.argmax(masked_prediction).item()
            # print(f'\n{masked_prediction[final_move]}')
        return final_move


def train(device: torch.device | None = None):
    try:
        plot_scores = []
        plot_mean_scores = []
        plot_win_rates = []
        total_score = 0
        record = 0
        win_streak = 0
        games_won = 0
        agent = Agent(device)
        game_helper = WordleAI(Wordle())
        while True:
            # get old state
            state_old = agent.get_state(game_helper.get_game())

            # get move
            final_move = agent.get_action(state_old, game_helper)
            # print(game_helper._WordleAI__available_words)
            # print(final_move)
            # input()

            # perform move and get new state
            reward, done = game_helper.play_step(final_move)
            state_new = agent.get_state(game_helper.get_game())

            # train short memory
            agent.train_short_memory(state_old, final_move, reward, state_new, done)

            # remember
            agent.remember(state_old, final_move, reward, state_new, done)

            if done:
                # forget games if guess on first try by chance
                if game_helper.get_game().get_guesses_left() == 5:
                    continue

                # train long memory, plot result
                # print(game_helper.get_game())
                agent.n_games += 1
                agent.train_long_memory()

                if game_helper.get_game().is_game_won():
                    games_won += 1
                    win_streak += 1
                    if win_streak > record:
                        record = win_streak
                        agent.model.save()
                    print(f'Game won! Games won: {games_won}')
                    if games_won % 1000 == 0:
                        agent.trainer.lr /= 1.5
                        if agent.trainer.lr < 0.0001:
                            agent.trainer.lr = 0.0001
                else:
                    win_streak = 0
                print('Game', agent.n_games, 'Reward', reward, 'Winstreak:', win_streak, 'Record:', record)
                print('\n')
                plot_scores.append(reward)
                total_score += reward
                mean_score = total_score / agent.n_games
                win_rate = (games_won / agent.n_games) * 1000
                plot_win_rates.append(win_rate)
                plot_mean_scores.append(mean_score)
                plot(plot_scores, plot_mean_scores, plot_win_rates)
                game_helper.reset()
    except (KeyboardInterrupt, Exception) as e:
        agent.model.save()
        print(game_helper._WordleAI__available_words)
        print(game_helper.get_valid_actions())
        print(game_helper._WordleAI__hints_dict)
        state0 = torch.tensor(state_old, dtype=torch.float, device=agent.model.device)
        prediction = agent.model(state0)
        valid_mask = game_helper.get_valid_action_mask(agent.model.device)
        prob_mask = game_helper.get_prob_action_mask(agent.model.device)
        masked_prediction = (prediction * prob_mask) + valid_mask
        for i, val in enumerate(masked_prediction):
            if val < -100:
                continue
            print(f'{i}: {val}', end=', ')
        raise e


def play(device: torch.device | None = None):
    model = Linear_QNet(61, [780, 26], 14855, device=device)
    model.load('./model/model_98.pth')
    game_helper = WordleAI(Wordle())

    while not game_helper.get_game().is_game_over():
        state = get_state_from_board(game_helper.get_game().get_board())
        state0 = torch.tensor(state, dtype=torch.float, device=model.device)
        prediction = model(state0)
        valid_mask = game_helper.get_valid_action_mask(model.device)
        prob_mask = game_helper.get_prob_action_mask(model.device)
        masked_prediction: list[torch.Tensor]
        masked_prediction = (prediction * prob_mask) + valid_mask
        final_moves = torch.topk(masked_prediction, 5)
        print(f'Suggested moves: {[(ALLOWED_WORDS[i], round(float(masked_prediction[i]), 4)) for i in final_moves.indices if i in game_helper.get_valid_actions()]}')
        print(game_helper.get_game())
        guess = input('Enter guess: ')
        game_helper.play_step(ALLOWED_WORDS.index(guess))


if __name__ == '__main__':
    torch.set_num_threads(40)
    if not torch.backends.mps.is_available():
        if not torch.backends.mps.is_built():
            print('MPS not available because the current PyTorch install was not '
                  'built with MPS enabled.')
        else:
            print('MPS not available because the current MacOS version is not 12.3+ '
                  'and/or you do not have an MPS-enabled device on this machine.')

    device = torch.device('mps')
    train(device)
