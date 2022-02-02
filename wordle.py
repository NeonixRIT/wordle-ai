'''
Command line Wordle game

Author: Kamron Cole kjc8084@rit.edu
'''
import os
import random
import numpy as np

# Colours used in output
RED = '\033[1;31m'
GREEN = '\033[1;32m'
WHITE = '\033[0m'
YELLOW = '\033[1;33m'

# Game Constants
WORD_LEN = 5
MAX_GUESSES = 6
ASSETS_PATH = '/assets'
ALLOWED_GUESSES_PATH = f'.{ASSETS_PATH}/wordle-allowed-guesses.txt'
POSSIBLE_ANSWERS_PATH = f'.{ASSETS_PATH}/wordle-answers.txt'

ALLOWED_WORDS = sorted([word.strip() for word in open(ALLOWED_GUESSES_PATH).readlines()]) # Possible guesses including answers
WORDS = sorted([word.strip() for word in open(POSSIBLE_ANSWERS_PATH).readlines()]) # Possible answers

# Numerical values too handle guess results easier
CORRECT_ALL = 20 # correct letter and position.
CORRECT_LETTER = 10 # correct letter wrong position.
WRONG = 0 # Wrong letter and position.
MAX_SCORE = CORRECT_ALL * WORD_LEN # Correct guess score

# Assign colour to guess result
GUESS_RESULT_DICT = {
    CORRECT_ALL: GREEN,
    CORRECT_LETTER: YELLOW,
    WRONG: WHITE
}

class Guess:
    '''
    A players single guess in a Wordle game
    '''
    __slots__ = ['__guess', '__answer', '__feedback', '__score', '__answer_dict']


    def __init__(self, *args):
        '''
        Params:
            guess:str - players guess
            answer:str - wordle games answer
            OR
            results:list[str, int] - same list returned by __build_feedback
        '''
        if len(args) == 2 and isinstance(args[0], str) and isinstance(args[1], str):
            self.__guess = args[0]
            self.__answer = args[1]
            self.__score = 0
            self.__answer_dict = dict()
            # Build dictionary mapping letter to indexes, len of any dictionary value is letter count
            for i in range(len(self.__answer)):
                letter = self.__answer[i]
                if letter not in self.__answer_dict:
                    self.__answer_dict[letter] = []
                self.__answer_dict[letter].append(i)
            self.__feedback = self.__build_feedback()
        elif len(args) == 1 and isinstance(args[0], list) and len(args[0]) == WORD_LEN:
            self.__feedback = args[0]
            self.__guess, self.__score = self.__values_from_result(self.__feedback)
            self.__answer = self.__guess if self.is_answer() else None
            self.__answer_dict = None


    def __str__(self):
        string = ''
        for letter, result in self.__feedback:
            string += f'{GUESS_RESULT_DICT[result]}[{letter}]{WHITE}'
        return string

    
    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, Guess):
            return False

        if __o.get_feedback() == self.get_feedback():
            return True
        return False


    def __backward_check_result(self, flag, result, answer_dict):
        '''
        Goes back in results list and changes score in first instance of flag (list[letter, score]) to the proper value.
        '''
        if flag in result:
            for j in range(len(result)):
                if result[j] == flag:
                    if len(answer_dict[flag[0]]) > 1: # if there the letter in the word and all the same letter havent been parsed yet
                        result[j][1] = CORRECT_LETTER
                    else:
                        result[j][1] = WRONG
                    break


    def __build_feedback(self) -> list:
        '''
        Build a list<str, int> containing (letter in word, hint result) where the index is a letter's position and 
        hint result is decided depending on the answer. Hint result is used to colorize output.
        '''
        result = []
        for i in range(len(self.__guess)):
            letter = self.__guess[i]
            if letter in self.__answer_dict and i in self.__answer_dict[letter]: # if letter in word and in correct position
                item = [letter, CORRECT_ALL] # make result entry
                flag = [letter, CORRECT_LETTER]
                self.__backward_check_result(flag, result, self.__answer_dict) # change previous entry of same letter to proper value
                result.append(item)
                self.__score += CORRECT_ALL
                self.__answer_dict[letter].remove(i) # remove already used letter index from dictionary
            elif letter in self.__answer_dict and len(self.__answer_dict[letter]) > 0: # if letter in word but not in correct position
                flag = [letter, CORRECT_LETTER]
                self.__backward_check_result(flag, result, self.__answer_dict) # change previous entry of same letter to proper value
                result.append(flag)
                self.__score += CORRECT_LETTER
            else: # letter not in word
                result.append([letter, WRONG])
                self.__score += WRONG
        return result


    def __values_from_result(self, result:list[str, int]) -> tuple:
        guess = ''
        score = 0
        for letter, value in result:
            guess += letter
            score += value
        return guess, score


    def get_feedback(self) -> list: return self.__feedback
    def is_answer(self) -> bool: return self.__score == MAX_SCORE
    def get_score(self) -> int: return self.__score
    def get_guess_raw(self) -> str: return self.__guess
        

class Board:
    '''
    Wordle game board that keeps track of player's previous guesses
    '''
    __slots__ = ['__board', '__guesses']


    def __init__(self):
        self.__board = ['[ ][ ][ ][ ][ ]' for _ in range(MAX_GUESSES)]
        self.__guesses = 0


    def __str__(self) -> str:
        string = ''
        for guess in self.__board:
            string += f'{guess}\n'
        return string

    
    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, Guess):
            return False

        for i in range(len(self.get_guesses())):
            if __o.get_gesses()[i] != self.get_guesses()[i]:
                return False
        return True


    def make_guess(self, guess: Guess):
        '''
        insert guess into the board and prepare it for next guess.
        '''
        self.__board[self.__guesses] = guess
        self.__guesses += 1

    
    def get_guesses(self) -> list: return self.__board
    def get_guesses_num(self) -> int: return self.__guesses
    def is_empty(self) -> bool: return self.__guesses == 0


class Wordle:
    '''
    Wordle game where a player attempts to guess a certain length word within a certain number of guesses and is given feedback on the letter's position and whether the word contains it for each guess
    '''
    __slots__ = ['__allowed_words', '__words', '__answer', '__guesses', '__board']

    
    def __init__(self, answer = None):
        self.__board = Board()
        self.__allowed_words = ALLOWED_WORDS
        self.__words = WORDS
        
        if not answer:
            self.__answer = random.choice(self.__words)
        else:
            self.__answer = answer
            
        self.__guesses = 0

    
    def __str__(self):
        return str(self.__board)
    

    def make_guess(self, raw_guess: str) -> Guess:
        '''
        given a word, make a guess and
        '''
        raw_guess = raw_guess.lower()
        if raw_guess not in self.__allowed_words:
            self.__clear_screen()
            print(f'{RED}"{raw_guess}" is not on the word list.{WHITE}')
            return None

        guess = Guess(raw_guess, self.__answer)
        self.__board.make_guess(guess)

        return guess


    def play(self):
        '''
        Play the game through a command line, prompting for a guess MAX_GUESSES number of times, invalid guesses arent counted
        '''
        self.__clear_screen()
        print()
        while self.__guesses < MAX_GUESSES:
            print(self.__board)
            print()
            raw_guess = input('Make a guess: ')
            guess = self.make_guess(raw_guess)
            if guess == None:
                continue

            self.__guesses += 1
            if guess.is_answer():
                self.__clear_screen()
                print(self.__board)
                print(f'{GREEN}Congratulations! {self.__guesses}/{MAX_GUESSES}{WHITE}')
                return

            self.__clear_screen()
            print()
        print(f'{GREEN}{self.__answer}{WHITE}')
        print(self.__board)
        print(f'{RED}Unluckers! Maybe next time.{WHITE}')

    
    def __clear_screen(self):
        '''
        clear terminal based on operating system
        '''
        if os.name == 'nt':
             os.system('cls')
        else: 
            os.system('clear')
        pass


    def get_answer(self) -> str: return self.__answer
    def get_board(self) -> Board: return self.__board


def main():
    game = Wordle('could')
    print(game.get_answer())
    game.play()


if __name__ == '__main__':
    main()
