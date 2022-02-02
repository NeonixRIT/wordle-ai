'''
Rudimentary AI to solve wordle puzzle, either from web GUI or internal CLI

Author: Kamron Cole kjc8084@rit.edu
'''
import csv
import json
import random
import time
import wordle
import wordle_ai_utils

import numpy as np

from alive_progress import alive_bar
from pynput.keyboard import Key, Controller

WORD_WEIGHTS_LETTER_PROB = json.loads(open('./assets/word_weights_letter_prob.json').read())
WORD_WEIGHT_WINRATE = json.loads(open('./assets/word_weights_winrate.json').read())
ALLOWED_FULL, WEIGHTS = list(zip(*WORD_WEIGHTS_LETTER_PROB.items()))


class WordleAI():
    '''
    Rudimentary AI to solve wordle puzzle, either from web GUI or internal CLI
    '''
    __slots__ = ['__hints_dict', '__wordle', '__word_weights_dict', '__first_guess', '__next_guess', '__guesses', '__won', '__results', '__result_str', '__probability_distribution']


    def __init__(self, wordle: wordle.Wordle, starting_word: str = 'proms') -> None:
        self.__hints_dict = {
            'INCLUDED': set(), # Letters in the word
            'EXCLUDED': set(), # Letters not in the word
            # Where included letters belong
            'CORRECT': set(),
            # Where included letters do not belong
            'GUESSED': set()
        }

        self.__wordle = wordle
        self.__word_weights_dict = dict(WORD_WEIGHTS_LETTER_PROB)
        self.__first_guess = starting_word
        self.__next_guess = self.__first_guess
        self.__guesses = 0
        self.__won = False
        self.__results = [None for _ in range(4)]
        self.__result_str = ''
        weights = self.__word_weights_dict.values()
        self.__probability_distribution = np.array(list(weights)) / sum(weights)


    def make_guess(self, raw_guess: str) -> wordle.Guess:
        '''
        Make a guess on an internal Wordle game
        '''
        return self.__wordle.make_guess(raw_guess)


    def read_report(self, guess: wordle.Guess) -> None:
        '''
        Read a guess's report and add letters to dict that will help solve for a word by removing invalid entries from the word list
        '''
        feedback = guess.get_feedback()
        for i in range(len(feedback)):
            letter, result = feedback[i]
            if result == wordle.CORRECT_ALL:
                self.__hints_dict['INCLUDED'].add(letter)
                self.__hints_dict['CORRECT'].add((letter, i))
                if letter in self.__hints_dict['EXCLUDED']:
                    self.__hints_dict['EXCLUDED'].remove(letter)
            if result == wordle.CORRECT_LETTER:
                self.__hints_dict['INCLUDED'].add(letter)
                self.__hints_dict['GUESSED'].add((letter, i))
                if letter in self.__hints_dict['EXCLUDED']:
                    self.__hints_dict['EXCLUDED'].remove(letter)
            if result == wordle.WRONG and letter not in self.__hints_dict['INCLUDED']:
                self.__hints_dict['GUESSED'].add((letter, i))
                self.__hints_dict['EXCLUDED'].add(letter)
                


    def narrow_from_correct_all(self):
        for letter, index in self.__hints_dict['CORRECT']:
            self.__word_weights_dict = {word: self.__word_weights_dict[word] for word in self.__word_weights_dict.keys() if word[index] == letter}
                    
    
    def narrow_from_correct_letter(self):
        for letter in self.__hints_dict['INCLUDED']:
            self.__word_weights_dict = {word: self.__word_weights_dict[word] for word in self.__word_weights_dict.keys() if letter in word}
    
    
    def narrow_from_wrong_letter(self):
        for letter in self.__hints_dict['EXCLUDED']:
            self.__word_weights_dict = {word: self.__word_weights_dict[word] for word in self.__word_weights_dict.keys() if letter not in word}
    
    
    def narrow_from_correct_letters_pos_tried(self):
        for letter, index in self.__hints_dict['GUESSED']:
            self.__word_weights_dict = {word: self.__word_weights_dict[word] for word in self.__word_weights_dict.keys() if word[index] != letter}
            

    def update_probability_distribution(self):
        weights = self.__word_weights_dict.values()
        self.__probability_distribution = np.array(list(weights)) / sum(weights)
    
    
    def narrow_words(self) -> None:
        '''
        Using a dict of all feedback gained from previous guesses, remove words and their weight from from their respective list so that the remaining words meet the criteria of the answer
        '''
        self.__word_weights_dict.pop(self.__next_guess)
        self.narrow_from_correct_all()
        self.narrow_from_correct_letter()
        self.narrow_from_correct_letters_pos_tried()
        self.narrow_from_wrong_letter()
        self.update_probability_distribution()


    def type_guess(self, keyboard, guess: str) -> None:
        '''
        Type a guess into the web GUI wordle game
        '''
        for letter in guess:
            keyboard.press(letter)
            keyboard.release(letter)
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)


    def run_web_gui(self) -> None:
        '''
        Attempt to solve web GUI Wordle game by reading board state in from images and narrowing down word list from consecutive guesss' feedback
        '''
        keyboard = Controller()
        score = 0
        time.sleep(1)
        while score < 100 and self.__guesses < wordle.MAX_GUESSES:
            try:
                # check on game window
                game_img = wordle_ai_utils.get_screen(wordle_ai_utils.WORDLE_GAME_BOX_1080P)
                board = wordle_ai_utils.read_img_to_board(game_img)
                # make guess
                self.type_guess(keyboard, self.__next_guess)
                # wait for website animation to finish
                time.sleep(3)
                # update internal board from image
                game_img = wordle_ai_utils.get_screen(wordle_ai_utils.WORDLE_GAME_BOX_1080P)
                board = wordle_ai_utils.read_img_to_board(game_img)
                guess = board.get_guesses()[self.__guesses]
                score = guess.get_score()
                print(guess, score)
                self.read_report(guess)
                if self.__guesses == 0:
                    self.__results[0] = self.__next_guess
                    self.__results[1] = score
                    
                if score >= 100:
                    break
                
                self.narrow_words()
                self.__next_guess = np.random.choice(list(self.__word_weights_dict.keys()), 1, False, self.__probability_distribution)[0]
                self.__guesses += 1
            except AttributeError as e:
                print(f'{wordle.RED}Error: {e}\nlikely because board was not found, or not in focus.{wordle.WHITE}')
                time.sleep(3)
        time.sleep(1)
        if score == 100:
            self.__won = True

        self.__results[2] = self.__won
        self.__results[3] = [word for word in self.__word_weights_dict.keys()]
        self.__result_str = f'"{self.__results[0]}","{self.__results[1]}","{self.__results[2]}","{self.__results[3]}"\n'


    def run_cli(self):
        '''
        Attempt to solve CLI Wordle game by reading board state in from Wordle game and narrowing down word list from consecutive guesss' feedback
        '''
        score = 0
        while score < 100 and self.__guesses < wordle.MAX_GUESSES:
            guess = self.make_guess(self.__next_guess)
            score = guess.get_score()
            self.read_report(guess)
            if self.__guesses == 0:
                self.__results[0] = self.__next_guess
                self.__results[1] = score
            
            if score >= 100:
                break
            
            self.narrow_words()
            self.__next_guess = np.random.choice(list(self.__word_weights_dict.keys()), 1, False, self.__probability_distribution)[0]
            self.__guesses += 1
        
        if score == 100:
            self.__won = True

        self.__results[2] = self.__won
        self.__results[3] = [word for word in self.__word_weights_dict.keys()]
        self.__result_str = f'"{self.__results[0]}","{self.__results[1]}","{self.__results[2]}","{self.__results[3]}"\n'

    
    def get_result(self) -> list: return self.__results
    def get_result_str(self) -> str: return self.__result_str
    def get_remaining_words(self) -> list: return list(self.__word_weights_dict.keys())
    def get_starting_word(self) -> str: return self.__first_guess
    def get_sug_next_guesses(self) -> str: return np.random.choice(list(self.__word_weights_dict.keys()), 1, False, self.__probability_distribution)[0]


def write_result_dict(final_words: list[str], out_filename: str, iters: int) -> None:
    '''
    Write results dict into a file to save results
    '''
    with open(out_filename, 'a') as file:
        file.write('\n')
        file.write(f'Iterations: {iters}\n')
        for entry in final_words:
            word = entry[0]
            avg_score = entry[1]
            file.write(f'    {word} : {avg_score}\n')


def output_file_to_dict(filename: str) -> dict[str, list[float, int]]:
    '''
    Read csv file of WordleAI results and compile data into a result dict
    This function is only used for compiling really old data from WordleAI
    '''
    result_dict = dict()
    with open(filename) as file:
        reader = csv.reader(file)
        for record in reader:
            guess = record[0]
            score = int(record[1])
            if guess in result_dict:
                avg_score = result_dict[guess][0]
                n = result_dict[guess][1]
                new_average = round((avg_score * (n / (n + 1))) + (score / (n + 1)), 2)
                result_dict[guess] = [new_average, n + 1]
            else:
                result_dict[guess] = [score, 1]
    return result_dict


def data_compiler() -> None:
    '''
    Helper function used to run multiple iterations to compile some set of data
    '''
    iterations = 100000
    iteration = 0
    result_dict = dict()
    score_filename = f'first_guess_results_score.txt'
    winrate_filename = f'first_guess_results_winrate.txt'
    words, weights = (ALLOWED_FULL, WEIGHTS)
    probability_dist = np.array(weights) / sum(weights)
    try:
        with alive_bar(iterations) as bar:
            while iteration < iterations:
                # print(f'Running iteration {iteration}')
                game = wordle.Wordle()
                # print(game.get_answer())
                bot = WordleAI(game, np.random.choice(words, 1, False, probability_dist)[0])
                bot.run_cli()
                results = bot.get_result()
                guess = results[0]
                score = results[1]
                won = results[2]
                answer = results[3]
                if guess in result_dict:
                    avg_score = result_dict[guess][0]
                    n = result_dict[guess][1]
                    num_wins = result_dict[guess][2]
                    new_n = n + 1
                    new_wins = num_wins + int(won)
                    new_win_rate = new_wins / new_n
                    new_average = round((avg_score * (n / (new_n))) + (score / (new_n)), 2)
                    result_dict[guess] = [new_average, new_n, new_wins, new_win_rate]
                else:
                    result_dict[guess] = [score, 1, int(won), int(won)]

                iteration += 1
                bar()
    except (Exception, KeyboardInterrupt) as e:
        print(f'\n{wordle.RED}Error has occured: {e}{wordle.WHITE}')

    final_words_score = sorted([list for list in result_dict.items()], key= lambda item: item[1], reverse=True)
    final_words_winrate = sorted([list for list in result_dict.items()], key= lambda item: item[1][3], reverse=True)
    write_result_dict(final_words_score, score_filename, iteration)
    write_result_dict(final_words_winrate, winrate_filename, iteration)

    print('Top 10 starting words for score:')
    print()
    print('    word'.ljust(16) + 'score')
    top_10_words_score = final_words_score[:10]
    for i in range(len(top_10_words_score)):
        print(f'    {top_10_words_score[i][0]}'.ljust(16) + str(top_10_words_score[i][1][0]))

    print()
    print('Top 10 starting words for winrate:')
    print()
    print('    word'.ljust(16) + 'winrate')
    top_10_words_winrate = final_words_winrate[:10]
    for i in range(len(top_10_words_winrate)):
        print(f'    {top_10_words_winrate[i][0]}'.ljust(16) + str(top_10_words_winrate[i][1][3]))
        

def test_winrate():
    wins = 0
    loses = 0
    for _ in range(10000):
        game = wordle.Wordle()
        bot = WordleAI(game)
        bot.run_cli()
        results = bot.get_result()
        if results[2]:
            wins += 1
        else:
            loses += 1
            print(f'Loss: {loses}')
            print(game.get_answer())
            print(bot.get_result()[3])
            print(game)
    print(f'Wins: {wins}')
    print(f'Loses: {loses}')
    
    
def web_solver():
    game = wordle.Wordle()
    bot = WordleAI(game) #, np.random.choice(words, 1, False, probability_dist)[0])
    bot.run_web_gui()
    
    
def cli_solver():
    game = wordle.Wordle('those')
    print(game.get_answer())
    bot = WordleAI(game) #, np.random.choice(words, 1, False, probability_dist)[0])
    bot.run_cli()
    print(game)
    
    
def main():
    # data_compiler()
    # web_solver()
    test_winrate()
    # cli_solver()

if __name__ == '__main__':
    main()
