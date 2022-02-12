'''
Rudimentary AI to solve wordle puzzle, either from web GUI or internal CLI

Author: Kamron Cole kjc8084@rit.edu
'''
import math

import numpy as np

import wordle as w
import wordle_utils as wu
import wordle_ai_utils as utils

import json


def sigmoid(x):
    return 1 / (1 + (math.e ** -x))


def get_frequency_based_priors(n_common=3000, width_under_sigmoid=10):
    """
    We know that that list of wordle answers was curated by some human
    based on whether they're sufficiently common. This function aims
    to associate each word with the likelihood that it would actually
    be selected for the final answer.
    Sort the words by frequency, then apply a sigmoid along it.

    author: 3blue1brown 
    """
    freq_map = {}
    with open('./assets/freq_map.json') as words_f:
        freq_map = json.loads(words_f.read())
    words = np.array(list(freq_map.keys()))
    freqs = np.array([freq_map[w] for w in words])
    arg_sort = freqs.argsort()
    sorted_words = words[arg_sort]

    # We want to imagine taking this sorted list, and putting it on a number
    # line so that it's length is 10, situating it so that the n_common most common
    # words are positive, then applying a sigmoid
    x_width = width_under_sigmoid
    c = x_width * (-0.5 + n_common / len(words))
    xs = np.linspace(c - x_width / 2, c + x_width / 2, len(words))
    priors = dict()
    for word, x in zip(sorted_words, xs):
        priors[word] = sigmoid(x)
    # print(priors)
    return priors


word_weight_dict = get_frequency_based_priors()


def get_weights(words, priors):
    '''
    author: 3blue1brown
    '''
    frequencies = np.array([priors[word] for word in words])
    total = frequencies.sum()
    if total == 0:
        return np.zeros(frequencies.shape)
    return frequencies / total


weights = get_weights(list(word_weight_dict.keys()), word_weight_dict)
# print(list(weights))

word_weight_dict = dict(zip(word_weight_dict.keys(), weights))




class WordleAI():
    '''
    Rudimentary AI to solve wordle puzzle, either from web GUI or internal CLI
    '''
    __slots__ = ['__hints_dict', '__wordle', '__word_weights_dict', '__next_guess',
                 '__guesses', '__verbose', '__probability_distribution']


    def __init__(self, game: w.Wordle, starting_word: str = 'proms', verbose=True) -> None:
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
        self.__word_weights_dict = dict(word_weight_dict) # dict(utils.WORD_WEIGHTS_LETTER_PROB)
        self.__next_guess = starting_word
        self.__guesses = 0
        weights = self.__word_weights_dict.values()
        self.__probability_distribution = np.array(list(weights)) / sum(weights)
        self.__verbose = verbose


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
        score_pattern = []
        feedback = guess.get_feedback()
        for i, token in enumerate(feedback):
            letter, result = token
            score_pattern.append(result)
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
        return tuple(score_pattern)


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

        weights = self.__word_weights_dict.values()
        self.__probability_distribution = np.array(list(weights)) / sum(weights)


    def run_cli(self):
        '''
        Attempt to solve CLI Wordle game by reading board state in from Wordle game and narrowing
        down word list from consecutive guesss' feedback
        '''
        guess = self.make_guess(self.__next_guess)
        score_pattern = guess.get_score_pattern()
        self.read_report(guess)
        self.narrow_words()
        return score_pattern


    def get_remaining_words(self) -> list:
        '''
        Get list of remaining words from words weight dict
        '''
        return list(self.__word_weights_dict.keys())


    def get_remaining_weights(self) -> list:
        '''
        Get list of remaining words from words weight dict
        '''
        return list(self.__word_weights_dict.values())


    def get_next_guess(self) -> str:
        '''
        Return current next guess
        '''
        return self.__next_guess


def narrow_words(words, guess, hints_dict) -> None:
    '''
    Using a dict of all feedback gained from previous guesses, remove words and
    their weight from from their respective list so that the remaining words meet
    the criteria of the answer
    '''
    words_remaining = [word for word in words if not utils.is_junk(word, hints_dict)]

    raw_guess = guess.get_guess_raw()
    if raw_guess in words_remaining:
        words_remaining.remove(raw_guess)

    return words_remaining


def read_report(guess, hints_dict):
    feedback = guess.get_feedback()
    for i, token in enumerate(feedback):
        letter, result = token
        # If is correct letter and in correct position
        if result == wu.CORRECT_ALL:
            hints_dict['INCLUDED'].add(letter)
            hints_dict['CORRECT'].add((letter, i))
            # Backwards check to make sure letter is not included and excluded at the same time
            if letter in hints_dict['EXCLUDED']:
                hints_dict['EXCLUDED'].remove(letter)
        # If is correct letter but in the wrong position
        if result == wu.CORRECT_LETTER:
            hints_dict['INCLUDED'].add(letter)
            hints_dict['GUESSED'].add((letter, i))
            # Backwards check to make sure letter is not included and excluded at the same time
            if letter in hints_dict['EXCLUDED']:
                hints_dict['EXCLUDED'].remove(letter)
        # If letter not in the word and hasn't already been marked as included
        if result == wu.WRONG and letter not in hints_dict['INCLUDED']:
            # Guesses with multiple letters will not put wrong repeated letters in EXCLUDED
            # if answer only has 1 of said letter. This attempts to fix that
            hints_dict['GUESSED'].add((letter, i))
            hints_dict['EXCLUDED'].add(letter)


def check(possible_answers, data_dict):
    progress = 1
    tot_words = len(possible_answers)
    for raw_guess in possible_answers:
        raw_guess = 'weary'
        print(f'trying "{raw_guess}" ({progress}/{tot_words})...')
        patterns = {}
        for answer in possible_answers:
            hints_dict = {
                # Letters in the word
                'INCLUDED': set(),
                # Letters not in the word
                'EXCLUDED': set(),
                # Where included letters belong
                'CORRECT': set(),
                # Where included letters do not belong
                'GUESSED': set()
            }

            guess = w.Guess(raw_guess, answer)
            pattern = guess.get_score_pattern()
            read_report(guess, hints_dict)
            words_remaining = narrow_words(possible_answers, guess, hints_dict)
            p = (len(words_remaining) / tot_words)
            if p == 0:
                p = 1 / tot_words
            info = -math.log2(p) # info (bits). How many times we reduced the words list by half
            uncertainty = sum([word_weight_dict[word] * -math.log2(word_weight_dict[word]) for word in words_remaining]) # entropy of remaining words
            patterns[pattern] = [p, info, uncertainty, len(words_remaining)]
        data_dict[raw_guess] = {k: [v] for k, v in sorted(patterns.items(), key=lambda item: item[1][2], reverse=True)}
        entropy = sum([value[1][0] * value[1][1] for value in patterns.items() if value[1][0] != 0])
        print(f'Entropy: {entropy}')
        progress += 1
        print('Done.\n')


def tests1():
    '''
    Run multiple iterations to get a rough guess of the AI's winrate,
    usually run between various changes to find optimal values
    '''
    data_dict = {}
    try:
        check(sorted(list(utils.ALLOWED_FULL)), data_dict)
    except KeyboardInterrupt:
        pass
    for word in data_dict:
        print(word, ':')
        for pattern in data_dict[word]:
            print(f'    {pattern}: {data_dict[word][pattern]}')
        print()


def tests():
    '''
    Run multiple iterations to get a rough guess of the AI's winrate,
    usually run between various changes to find optimal values
    '''
    progress = 1
    tot_words = len(utils.ALLOWED_FULL)
    data_dict = {}
    try:
        for raw_guess in sorted(utils.ALLOWED_FULL):
            raw_guess = 'weary'
            print(f'trying "{raw_guess}" ({progress}/{tot_words})...')
            patterns = {}
            for answer in sorted(utils.ALLOWED_FULL):
                game = w.Wordle(answer)
                bot = WordleAI(game, raw_guess)
                score_pattern = bot.run_cli()
                p = (len(bot.get_remaining_words()) / tot_words) # probability(pattern)
                if p == 0:
                    p = 1 / tot_words
                info = -math.log2(p) # info (bits). How many times we reduced the words list by half
                # uncertainty = 0 # entropy of remaining words
                patterns[score_pattern] = [p, info, len(bot.get_remaining_words())]
            data_dict[raw_guess] = {k: [v] for k, v in sorted(patterns.items(), key=lambda item: item[1][0], reverse=True)}
            entropy = sum([value[1][0] * value[1][1] for value in patterns.items() if value[1][0] != 0])
            print(f'Entropy: {entropy}')
            progress += 1
            print('Done.\n')
    except KeyboardInterrupt:
        pass
    for word in data_dict:
        print(word, ':')
        for pattern in data_dict[word]:
            print(f'    {pattern}: {data_dict[word][pattern]}')
        print()



def main():
    '''
    Main
    '''
    tests1()


if __name__ == '__main__':
    main()
