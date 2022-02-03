'''
Rudimentary AI to solve wordle puzzle, either from web GUI or internal CLI

Author: Kamron Cole kjc8084@rit.edu
'''
import functools
import time

import numpy as np
import alive_progress as ap
from pynput.keyboard import Controller

import wordle as w
import wordle_utils as wu
import wordle_ai_utils as utils


class WordleAI():
    '''
    Rudimentary AI to solve wordle puzzle, either from web GUI or internal CLI
    '''
    __slots__ = ['__hints_dict', '__wordle', '__word_weights_dict', '__next_guess',
                 '__guesses', '__won', '__probability_distribution']


    def __init__(self, game: w.Wordle, starting_word: str = 'proms') -> None:
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

        self.__wordle = game
        self.__word_weights_dict = dict(utils.WORD_WEIGHTS_LETTER_PROB)
        self.__next_guess = starting_word
        self.__guesses = 0
        self.__won = False
        weights = self.__word_weights_dict.values()
        self.__probability_distribution = np.array(list(weights)) / sum(weights)


    def make_guess(self, raw_guess: str) -> w.Guess:
        '''
        Make a guess on an internal Wordle game
        '''
        return self.__wordle.make_guess(raw_guess)


    def read_report(self, guess: w.Guess) -> None:
        '''
        Read a guess's report and add letters to dict that will help solve
        for a word by removing invalid entries from the word list
        '''
        feedback = guess.get_feedback()
        for i, token in enumerate(feedback):
            letter, result = token
            # If is correct letter and in correct position
            if result == wu.CORRECT_ALL:
                self.__hints_dict['INCLUDED'].add(letter)
                self.__hints_dict['CORRECT'].add((letter, i))
                # Backwards check to make sure letter is not included and excluded at the same time
                if letter in self.__hints_dict['EXCLUDED']:
                    self.__hints_dict['EXCLUDED'].remove(letter)
            # If is correct letter but in the wrong position
            if result == wu.CORRECT_LETTER:
                self.__hints_dict['INCLUDED'].add(letter)
                self.__hints_dict['GUESSED'].add((letter, i))
                # Backwards check to make sure letter is not included and excluded at the same time
                if letter in self.__hints_dict['EXCLUDED']:
                    self.__hints_dict['EXCLUDED'].remove(letter)
            # If letter not in the word and hasn't already been marked as included
            if result == wu.WRONG and letter not in self.__hints_dict['INCLUDED']:
                # Guesses with multiple letters will not put wrong repeated letters in EXCLUDED
                # if answer only has 1 of said letter. This attempts to fix that
                self.__hints_dict['GUESSED'].add((letter, i))
                self.__hints_dict['EXCLUDED'].add(letter)


    def update_probability_distribution(self):
        '''
        Update probablility distribution after words list has been narrowed
        '''
        weights = self.__word_weights_dict.values()
        self.__probability_distribution = np.array(list(weights)) / sum(weights)


    def narrow_words(self) -> None:
        '''
        Using a dict of all feedback gained from previous guesses, remove words and
        their weight from from their respective list so that the remaining words meet
        the criteria of the answer
        '''
        if self.__next_guess in self.__word_weights_dict:
            self.__word_weights_dict.pop(self.__next_guess)

        self.__word_weights_dict = {word: self.__word_weights_dict[word]
                                    for word in self.__word_weights_dict.keys()
                                    if not utils.is_junk(word, self.__hints_dict)}

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


    def prioritize_unique_letters(self):
        '''
        Choose a new word to guess that tries to eliminate a majority of the unique letters
        in the words remaining
        '''
        common_letters = self.find_unique_letters()
        words_with_common_letters = utils.find_words_with_most_unique_letters(common_letters)
        word = utils.choose_word_from_unique_words(words_with_common_letters)
        return word


    def calc_next_guesses(self, score: int) -> str:
        '''
        Find next guess based on score
        '''
        guess = ''
        # randomly choose next guess from a weighted list
        word_list = list(self.__word_weights_dict.keys())
        prob_dist = self.__probability_distribution
        guess = np.random.choice(word_list, 1, False, prob_dist)[0]

        # If there are guesses left and score is above a threshold and there
        # are more word left then guesses prioritize removing unique letters
        # over guessing a correct word
        above_score_thresh = score >= utils.SCORE_THRESHOLD
        guesses_left = self.__guesses < utils.GUESS_THRESHOLD
        guessable = (wu.MAX_GUESSES - self.__guesses) >= len(self.__word_weights_dict)
        if above_score_thresh and guesses_left and not guessable:
            guess = self.prioritize_unique_letters()
        return guess


    def run_web_gui(self) -> None:
        '''
        Attempt to solve web GUI Wordle game by reading board state in from images and
        narrowing down word list from consecutive guesss' feedback
        '''
        keyboard = Controller()
        score = 0
        time.sleep(1)
        while score < 100 and self.__guesses < wu.MAX_GUESSES:
            try:
                # check on game window
                game_img = utils.get_screen(utils.WORDLE_GAME_BOX_1080P)
                board = utils.read_img_to_board(game_img)
                # make guess
                utils.type_guess(keyboard, self.__next_guess)
                # wait for website animation to finish
                time.sleep(3)
                # update internal board from image
                game_img = utils.get_screen(utils.WORDLE_GAME_BOX_1080P)
                board = utils.read_img_to_board(game_img)
                guess = board.get_guesses()[self.__guesses]
                score = guess.get_score()
                self.read_report(guess) # update hints dict from guess report
                print(guess, score)

                if score >= 100: # if game is solved, end
                    break

                self.narrow_words() # remove invalid words from dictionary of possible words
                self.__guesses += 1
                self.__next_guess = self.calc_next_guesses(score)
            except AttributeError as attr_e:
                msg = f'{wu.RED}Error: {attr_e}\n' \
                    + f'likely because board was not found, or not in focus.{wu.WHITE}'
                print(msg)
                time.sleep(3)
        time.sleep(1)

        if score == 100:
            self.__won = True

        return self.__won


    def run_cli(self):
        '''
        Attempt to solve CLI Wordle game by reading board state in from Wordle game and narrowing
        down word list from consecutive guesss' feedback
        '''
        score = 0
        while score < 100 and self.__guesses < wu.MAX_GUESSES:
            guess = self.make_guess(self.__next_guess)
            score = guess.get_score()
            self.read_report(guess) # update hints dict from guess report

            if score >= 100: # if game is solved, end
                break

            self.narrow_words() # remove invalid words from dictionary of possible words
            self.__guesses += 1
            self.__next_guess = self.calc_next_guesses(score)

        if score == 100:
            self.__won = True

        return self.__won


    def get_remaining_words(self) -> list:
        '''
        Get list of remaining words from words weight dict
        '''
        return list(self.__word_weights_dict.keys())


    def get_next_guess(self) -> str:
        '''
        Return current next guess
        '''
        return self.__next_guess


def test_winrate():
    '''
    Run multiple iterations to get a rough guess of the AI's winrate,
    usually run between various changes to find optimal values
    '''
    wins = 0
    loses = 0
    iterations = 100000
    with ap.alive_bar(iterations) as prog_bar:
        for _ in range(iterations):
            game = w.Wordle()
            bot = WordleAI(game)
            result = bot.run_cli()
            if result:
                wins += 1
            else:
                loses += 1
                print(f'Loss: {loses}')
                print(game.get_answer())
                print(game)
            prog_bar()
        print(f'Wins: {wins}')
        print(f'Loses: {loses}')
        print(f'Win rate: {round((wins / iterations) * 100, 2)}%')
        print(f'Loss rate: {round((loses / iterations) * 100, 2)}%')


def web_solver():
    '''
    Solve a wordle game via web GUI
    '''
    game = w.Wordle()
    bot = WordleAI(game)
    bot.run_web_gui()


def cli_solver():
    '''Solve a wordle game via CLI'''
    game = w.Wordle()
    print(game.get_answer())
    bot = WordleAI(game)
    bot.run_cli()
    print(game)


def main():
    '''
    Main
    '''
    # web_solver()
    # test_winrate()
    cli_solver()


if __name__ == '__main__':
    main()
