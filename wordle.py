"""
Command line Wordle game

Author: Kamron Cole kjc8084@rit.edu
"""
import numpy as np

import wordle_utils as utils

# Old Wordle Possible guesses including answers
# ALLOWED_WORDS = None
# with open(utils.ALLOWED_GUESSES_PATH, 'r', encoding='utf-8') as file:
#     ALLOWED_WORDS = sorted([word.strip() for word in file.readlines()])

# Old Wordle Possible answers
# ANSWERS = None
# with open(utils.POSSIBLE_ANSWERS_PATH, 'r', encoding='utf-8') as file:
#     ANSWERS = sorted([word.strip() for word in file.readlines()])

# New York Times Wordle Words
with open(utils.NEW_ALLOWED_GUESSES_PATH, 'r', encoding='utf-8') as file:
    ALLOWED_WORDS = sorted([word.strip() for word in file.readlines()])

with open(utils.NEW_POSSIBLE_ANSWERS_PATH, 'r', encoding='utf-8') as file:
    ANSWERS = sorted([word.strip() for word in file.readlines()])

class Guess:
    """
    A players single guess in a Wordle game
    """
    __slots__ = ['__guess', '__answer', '__feedback', '__score', '__answer_dict', '__score_pattern']

    def __init__(self, *args):
        """
        Params:
            guess:str - players guess
            answer:str - wordle games answer

            OR

            results:list[str, int] - same list returned by __build_feedback
        """
        if len(args) == 2 and isinstance(args[0], str) and isinstance(args[1], str):
            self.__guess = args[0]
            self.__answer = args[1]
            self.__score = 0
            self.__answer_dict = dict()
            # Build dictionary mapping letter to indexes
            # len of any dictionary value is letter count
            for i, letter in enumerate(self.__answer):
                letter = self.__answer[i]
                if letter not in self.__answer_dict:
                    self.__answer_dict[letter] = []
                self.__answer_dict[letter].append(i)
            self.__feedback = self.__build_feedback()
        elif len(args) == 1 and isinstance(args[0], list) and len(args[0]) == utils.WORD_LEN:
            self.__feedback = args[0]
            self.__guess, self.__score, self.__score_pattern = utils.values_from_result(self.__feedback)
            self.__answer = self.__guess if self.is_answer() else None
            self.__answer_dict = None

    def __str__(self):
        string = ''
        for letter, result in self.__feedback:
            string += f'{utils.GUESS_RESULT_DICT[result]}[{letter}]{utils.WHITE}'
        return string

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, Guess):
            return False

        if __o.get_feedback() == self.get_feedback():
            return True
        return False

    def __build_feedback(self) -> list:
        """
        Build a list<str, int> containing (letter in word,
        hint result) where the index is a letter's position and
        hint result is decided depending on the answer. Hint result is used to colorize output.
        """
        result = []
        for i, letter in enumerate(self.__guess):
            # if letter in word and in correct position
            if letter in self.__answer_dict and i in self.__answer_dict[letter]:
                # make result entry
                item = [letter, utils.CORRECT_ALL]
                flag = [letter, utils.CORRECT_LETTER]
                # change previous entry of same letter to proper value
                utils.remove_flag_from_dict(flag, result, self.__answer_dict)
                result.append(item)
                # remove already used letter index from dictionary
                self.__answer_dict[letter].remove(i)
            # if letter in word but not in correct position
            elif letter in self.__answer_dict and len(self.__answer_dict[letter]) > 0:
                flag = [letter, utils.CORRECT_LETTER]
                # change previous entry of same letter to proper value
                utils.remove_flag_from_dict(flag, result, self.__answer_dict)
                result.append(flag)
            else: # letter not in word
                result.append([letter, utils.WRONG])
        self.__score = sum([score[1] for score in result])
        self.__score_pattern = tuple([score[1] for score in result])
        return result

    def get_feedback(self) -> list:
        """
        Get the feedback report built on init
        """
        return self.__feedback

    def is_answer(self) -> bool:
        """
        A guess is an answer if its score is MAX_SCORE
        used instead of __guess == __answer because
        a guess can be made where the answer is unknown
        """
        return self.__score == utils.MAX_SCORE

    def get_score(self) -> int:
        """
        Get a guess's score, calculated on init
        """
        return self.__score

    def get_guess_raw(self) -> str:
        """
        Get the raw string used to build feedback report
        """
        return self.__guess

    def get_score_pattern(self) -> tuple:
        """
        Get tuple of just the score values
        """
        return self.__score_pattern


class Board:
    """
    Wordle game board that keeps track of player's previous guesses
    """
    __slots__ = ['__board', '__guesses']

    def __init__(self):
        self.__board = ['[ ][ ][ ][ ][ ]' for _ in range(utils.MAX_GUESSES)]
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
        """
        Insert guess into the board and prepare it for next guess.
        """
        self.__board[self.__guesses] = guess
        self.__guesses += 1

    def get_guesses(self) -> list:
        """
        Get list of guesses in a board
        """
        return self.__board

    def get_guesses_num(self) -> int:
        """
        Get number of guesses currently contained in the board
        """
        return self.__guesses

    def is_empty(self) -> bool:
        """
        If board length is 0 (0 guesses made), board is empty
        """
        return self.__guesses == 0


class Wordle:
    """
    Wordle game where a player attempts to guess a certain length word within
    a certain number of guesses gives feedback on the letter's position and whether
    the word contains it for each guess
    """
    __slots__ = ['__allowed_words', '__words', '__answer', '__guesses', '__board']

    def __init__(self, answer=None):
        self.__board = Board()
        self.__allowed_words = ALLOWED_WORDS
        self.__words = ANSWERS

        if not answer:
            self.__answer = np.random.choice(self.__words, 1)[0]
        else:
            self.__answer = answer

        self.__guesses = 0

    def __str__(self):
        return str(self.__board)

    def make_guess(self, raw_guess: str) -> Guess | None:
        """
        Given a word, make a guess and check that it is valid
        """
        raw_guess = raw_guess.lower()
        if raw_guess not in self.__allowed_words:
            utils.clear_screen()
            print(f'{utils.RED}"{raw_guess}" is not on the word list.{utils.WHITE}')
            return None

        guess = Guess(raw_guess, self.__answer)
        self.__board.make_guess(guess)

        return guess

    def play(self):
        """
        Play the game through a command line, prompting for a guess MAX_GUESSES number of times
        invalid guesses arent counted
        """
        utils.clear_screen()
        print()
        while self.__guesses < utils.MAX_GUESSES:
            print(self.__board)
            print()
            raw_guess = input('Make a guess: ')
            guess = self.make_guess(raw_guess)
            if not guess:
                continue

            self.__guesses += 1
            if guess.is_answer():
                utils.clear_screen()
                print(self.__board)
                win_sufix = f'{utils.MAX_GUESSES}{utils.WHITE}'
                print(f'{utils.GREEN}Congratulations! {self.__guesses}/{win_sufix}')
                return

            utils.clear_screen()
            print()
        print(f'{utils.GREEN}{self.__answer}{utils.WHITE}')
        print(self.__board)
        print(f'{utils.RED}Unluckers! Maybe next time.{utils.WHITE}')

    def get_answer(self) -> str:
        """
        Get game's current answer
        """
        return self.__answer

    def get_board(self) -> Board:
        """
        Get board representation of current game
        """
        return self.__board


def main():
    """
    Play a Wordle game
    """
    game = Wordle()
    game.play()


if __name__ == '__main__':
    main()
