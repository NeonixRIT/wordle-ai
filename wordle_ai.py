'''
Rudimentary AI to solve wordle puzzle, either from web GUI or internal CLI

Author: Kamron Cole kjc8084@rit.edu
'''
import functools
import json
import time

import wordle
import wordle_ai_utils

import numpy as np

from alive_progress import alive_bar
from pynput.keyboard import Key, Controller

WORD_WEIGHTS_LETTER_PROB = json.loads(open('./assets/word_weights_letter_prob.json').read())
WORD_WEIGHT_WINRATE = json.loads(open('./assets/word_weights_winrate.json').read())
ALLOWED_FULL, WEIGHTS = list(zip(*WORD_WEIGHTS_LETTER_PROB.items()))

SCORE_THRESHOLD = 60
GUESS_THRESHOLD = wordle.MAX_GUESSES - 1 
WORDS_LEN_THRESHOLD = 3


class WordleAI():
    '''
    Rudimentary AI to solve wordle puzzle, either from web GUI or internal CLI
    '''
    __slots__ = ['__hints_dict', '__wordle', '__word_weights_dict', '__first_guess', '__next_guess', '__guesses', '__won', '__results', '__result_str', '__probability_distribution']


    def __init__(self, wordle: wordle.Wordle, starting_word: str = 'proms') -> None:
        self.__hints_dict = {
            # Letters in the word
            'INCLUDED': set(),
             # Letters not in the word
            'EXCLUDED': set(),
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
            if result == wordle.CORRECT_ALL: # If is correct letter and in correct position
                self.__hints_dict['INCLUDED'].add(letter)
                self.__hints_dict['CORRECT'].add((letter, i))
                if letter in self.__hints_dict['EXCLUDED']: # Backwards check to make sure letter is not included and excluded at the same time
                    self.__hints_dict['EXCLUDED'].remove(letter)
            if result == wordle.CORRECT_LETTER: # If is correct letter but in the wrong position
                self.__hints_dict['INCLUDED'].add(letter)
                self.__hints_dict['GUESSED'].add((letter, i))
                if letter in self.__hints_dict['EXCLUDED']: # Backwards check to make sure letter is not included and excluded at the same time
                    self.__hints_dict['EXCLUDED'].remove(letter)
            if result == wordle.WRONG and letter not in self.__hints_dict['INCLUDED']: # If letter not in the word and hasn't already been marked as included
                self.__hints_dict['GUESSED'].add((letter, i)) # Guesses with multiple letters will not put wrong repeated letters in EXCLUDED if answer only has 1 of said letter. This attempts to fix that
                self.__hints_dict['EXCLUDED'].add(letter)


    def narrow_from_correct_all(self):
        '''
        Remove words from words list that do not have correct letters in the correct index
        '''
        for letter, index in self.__hints_dict['CORRECT']:
            self.__word_weights_dict = {word: self.__word_weights_dict[word] for word in self.__word_weights_dict.keys() if word[index] == letter}


    def narrow_from_correct_letter(self):
        '''
        Remove words from words list that do not have a correct letter in it
        '''
        for letter in self.__hints_dict['INCLUDED']:
            self.__word_weights_dict = {word: self.__word_weights_dict[word] for word in self.__word_weights_dict.keys() if letter in word}


    def narrow_from_wrong_letter(self):
        '''
        Remove words from words list that have a wrong letter in it
        '''
        for letter in self.__hints_dict['EXCLUDED']:
            self.__word_weights_dict = {word: self.__word_weights_dict[word] for word in self.__word_weights_dict.keys() if letter not in word}


    def narrow_from_correct_letters_pos_tried(self):
        '''
        Remove words from words list that has correct letters in the wrong position that have already been tried
        '''
        for letter, index in self.__hints_dict['GUESSED']:
            self.__word_weights_dict = {word: self.__word_weights_dict[word] for word in self.__word_weights_dict.keys() if word[index] != letter}


    def update_probability_distribution(self):
        '''
        Update probablility distribution after words list has been narrowed
        '''
        weights = self.__word_weights_dict.values()
        self.__probability_distribution = np.array(list(weights)) / sum(weights)


    def narrow_words(self) -> None:
        '''
        Using a dict of all feedback gained from previous guesses, remove words and their weight from from their respective list so that the remaining words meet the criteria of the answer
        '''
        if self.__next_guess in self.__word_weights_dict:
            self.__word_weights_dict.pop(self.__next_guess)
        self.narrow_from_correct_all()
        self.narrow_from_correct_letter()
        self.narrow_from_correct_letters_pos_tried()
        self.narrow_from_wrong_letter()
        self.update_probability_distribution()


    def find_unique_letters(self) -> set:
        '''
        Find unique letters in the remaining words list, if common letters is empty, 
        meaning all remaining words have letters in common but not in the same order,
        remove a word from remaining words list and try again
        '''
        words_left = list(self.__word_weights_dict.keys())
        common_letters = functools.reduce(lambda x, y: set(x) ^ set(y), words_left)
        while not common_letters:
            words_left.pop()
            common_letters = functools.reduce(lambda x, y: set(x) ^ set(y), words_left)
        return common_letters


    def find_words_with_most_unique_letters(self, unique_letters: set) -> set:
        '''
        Find set of words that have the unique letters in common,
        if no word exists with all unique letter in common,
        remove a unique letter and try again
        '''
        all_words_left = []
        for letter in unique_letters:
            words_left = [word for word in ALLOWED_FULL if letter in word]
            all_words_left.append(words_left)
        
        words = functools.reduce(lambda x, y: set(x) & set(y), all_words_left)
        while not words:
            all_words_left.pop()
            words = functools.reduce(lambda x, y: set(x) & set(y), all_words_left)
        return words


    def choose_word_from_unique_words(self, unique_words: set) -> str:
        '''
        Rebuild a weighted words dict with the unique words
        Choose a random word from the weighted words dict
        '''
        common_word_weights = dict()
        for word in unique_words:
            common_word_weights[word] = WORD_WEIGHTS_LETTER_PROB[word]
        prob_dist = np.array(list(common_word_weights.values())) / sum(common_word_weights.values())
        return np.random.choice(list(common_word_weights.keys()), 1, False, prob_dist)[0]


    def prioritize_unique_letters(self):
        '''
        Choose a new word to guess that tries to eliminate a majority of the unique letters in the words remaining
        '''
        common_letters = self.find_unique_letters()
        words_with_common_letters = self.find_words_with_most_unique_letters(common_letters)
        word = self.choose_word_from_unique_words(words_with_common_letters)
        return word


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
                self.read_report(guess) # update hints dict from guess report
                print(guess, score) 
                    
                if score >= 100: # if game is solved, end
                    break
                
                self.narrow_words() # remove invalid words from dictionary of possible words
                self.__guesses += 1
                # randomly choose next guess from a weighted list
                self.__next_guess = np.random.choice(list(self.__word_weights_dict.keys()), 1, False, self.__probability_distribution)[0]
                # If there are guesses left and score/remaining words are above a threshold prioritize removing unique letters over guessing a correct word
                if score >= SCORE_THRESHOLD and self.__guesses < GUESS_THRESHOLD and len(self.__word_weights_dict) > WORDS_LEN_THRESHOLD:
                    self.__next_guess = self.prioritize_unique_letters()
            except AttributeError as e:
                print(f'{wordle.RED}Error: {e}\nlikely because board was not found, or not in focus.{wordle.WHITE}')
                time.sleep(3)
        time.sleep(1)

        if score == 100:
            self.__won = True

        return self.__won


    def run_cli(self):
        '''
        Attempt to solve CLI Wordle game by reading board state in from Wordle game and narrowing down word list from consecutive guesss' feedback
        '''
        score = 0
        while score < 100 and self.__guesses < wordle.MAX_GUESSES:
            guess = self.make_guess(self.__next_guess)
            score = guess.get_score()
            self.read_report(guess) # update hints dict from guess report
            
            if score >= 100: # if game is solved, end
                break
            
            self.narrow_words() # remove invalid words from dictionary of possible words
            self.__guesses += 1
            # randomly choose next guess from a weighted list
            self.__next_guess = np.random.choice(list(self.__word_weights_dict.keys()), 1, False, self.__probability_distribution)[0]
            # If there are guesses left and score/remaining words are above a threshold prioritize removing unique letters over guessing a correct word
            if score >= SCORE_THRESHOLD and self.__guesses < GUESS_THRESHOLD and len(self.__word_weights_dict) > WORDS_LEN_THRESHOLD:
                self.__next_guess = self.prioritize_unique_letters()
        
        if score == 100:
            self.__won = True

        return self.__won


    def get_remaining_words(self) -> list: return list(self.__word_weights_dict.keys())
    def get_starting_word(self) -> str: return self.__first_guess
    def get_sug_next_guesses(self) -> str: return np.random.choice(list(self.__word_weights_dict.keys()), 1, False, self.__probability_distribution)[0]


def test_winrate():
    '''
    Run multiple iterations to get a rough guess of the AI's winrate, usually run between various changes to find optimal values
    '''
    wins = 0
    loses = 0
    iterations = 10000
    with alive_bar(iterations) as bar:
        for _ in range(iterations):
            game = wordle.Wordle()
            bot = WordleAI(game)
            result = bot.run_cli()
            if result:
                wins += 1
            else:
                loses += 1
                # print(f'Loss: {loses}')
                # print(game.get_answer())
                # print(game)
            bar()
        print(f'Wins: {wins}')
        print(f'Loses: {loses}')
        print(f'Win rate: {round((wins / iterations) * 100, 2)}%')
        print(f'Loss rate: {round((loses / iterations) * 100, 2)}%')


def web_solver():
    '''
    Solve a wordle game via web GUI
    '''
    game = wordle.Wordle()
    bot = WordleAI(game)
    bot.run_web_gui()


def cli_solver():
    '''Solve a wordle game via CLI'''
    game = wordle.Wordle()
    print(game.get_answer())
    bot = WordleAI(game)
    bot.run_cli()
    print(game)


def main():
    '''
    Main
    '''
    # web_solver()
    test_winrate()
    # cli_solver()
    return


if __name__ == '__main__':
    main()
