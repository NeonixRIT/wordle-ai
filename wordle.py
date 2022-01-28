import os
import random

RED = '\033[1;31m'
GREEN = '\033[1;32m'
WHITE = '\033[0m'
YELLOW = '\033[1;33m'

CORRECT_ALL = 100 # correct letter and position.
CORRECT_LETTER = 50 # correct letter wrong position.
WRONG = 0 # Wrong letter and position.

GUESS_RESULT_DICT = {
    CORRECT_ALL: GREEN,
    CORRECT_LETTER: YELLOW,
    WRONG: WHITE
}

WORD_LEN = 5
MAX_GUESSES = 6
ASSETS_PATH = '/assets'
ALLOWED_GUESSES_PATH = f'.{ASSETS_PATH}/wordle-allowed-guesses.txt'
POSSIBLE_ANSWERS_PATH = f'.{ASSETS_PATH}/wordle-answers.txt'

ALLOWED_WORDS = sorted([word.strip() for word in open(ALLOWED_GUESSES_PATH).readlines()])
WORDS = sorted([word.strip() for word in open(POSSIBLE_ANSWERS_PATH).readlines()])

class Guess:
    __slots__ = ['__guess', '__answer', '__feedback']


    def __init__(self, guess: str, answer: str):
        self.__guess = guess
        self.__answer = answer
        self.__feedback = self.__build_feedback()


    def __str__(self):
        string = ''
        for letter, result in self.__feedback:
            string += f'{GUESS_RESULT_DICT[result]}[{letter}]{WHITE}'
        return string


    def __build_feedback(self) -> list:
        result = []
        for i in range(len(self.__guess)):
            letter = self.__guess[i]
            if letter == self.__answer[i]:
                result.append((letter, CORRECT_ALL))
            elif letter in self.__answer and (letter, CORRECT_LETTER) not in result:
                result.append((letter, CORRECT_LETTER))
            else:
                result.append((letter, WRONG))
        return result


    def get_feedback(self) -> list:
        return self.__feedback


    def is_answer(self) -> bool:
        return self.__guess == self.__answer
        

class Board:
    __slots__ = ['__board', '__guesses']


    def __init__(self):
        self.__board = ['[ ][ ][ ][ ][ ]' for _ in range(MAX_GUESSES)]
        self.__guesses = 0


    def __str__(self) -> str:
        string = ''
        for guess in self.__board:
            string += f'{guess}\n'
        return string


    def make_guess(self, guess: Guess):
        self.__board[self.__guesses] = guess
        self.__guesses += 1


class Wordle:
    __slots__ = ['__allowed_words', '__words', '__answer', '__guesses', '__board']

    
    def __init__(self):
        self.__board = Board()
        self.__allowed_words = ALLOWED_WORDS
        self.__words = WORDS
        self.__answer = random.choice(self.__words)
        self.__guesses = 0

    
    def __str__(self):
        return str(self.__board)
    

    def make_guess(self, raw_guess: str) -> Guess:
        raw_guess = raw_guess.lower()
        if raw_guess not in self.__allowed_words:
            os.system('cls')
            print(f'{RED}"{raw_guess}" is not on the word list.{WHITE}')
            return None

        guess = Guess(raw_guess, self.__answer)
        self.__board.make_guess(guess)

        return guess


    def play(self):
        while self.__guesses < MAX_GUESSES:
            print(self.__board)
            print()
            raw_guess = input('Make a guess: ')
            guess = self.make_guess(raw_guess)
            if guess == None:
                continue

            if guess.is_answer():
                print(self.__board)
                print(f'{GREEN}Congratulations! {self.__guesses}/{MAX_GUESSES}{WHITE}')
                return

            self.__guesses += 1
            os.system('cls')
            print()
        print(self.__board)
        print(f'{RED}Unluckers! Maybe next time.{WHITE}')


    def get_answer(self):
        return self.__answer


    def get_board(self):
        return self.__board


def main():
    game = Wordle()
    game.play()


if __name__ == '__main__':
    main()
