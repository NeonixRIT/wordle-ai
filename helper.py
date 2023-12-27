'''
Sourced from: Modified from https://github.com/patrickloeber/snake-ai-pytorch/
'''
import matplotlib.pyplot as plt
from IPython import display

plt.ion()

def plot(scores, mean_scores, win_rates):
    display.clear_output(wait=True)
    display.display(plt.gcf())
    plt.clf()
    plt.title('Training...')
    plt.xlabel('Number of Games')
    plt.ylabel('Score')
    plt.plot(scores)
    plt.plot(mean_scores)
    plt.plot(win_rates)
    plt.ylim(ymin=0)
    plt.text(len(scores) - 1, scores[-1], f'reward\n{str(scores[-1])}')
    plt.text(len(mean_scores) - 1, mean_scores[-1], f'mean reward\n{str(mean_scores[-1])}')
    plt.text(len(win_rates) - 1, win_rates[-1], f'winrate\n{str(win_rates[-1] / 10)}')
    plt.show(block=False)
    plt.pause(.1)
