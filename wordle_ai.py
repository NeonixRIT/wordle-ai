import csv
import random
import re
import wordle

from alive_progress import alive_bar

ALLOWED_FULL = [word.strip() for word in open(wordle.ALLOWED_GUESSES_PATH).readlines()]

class WordleAI():
    __slots__ = ['__letters', '__wordle', '__words', '__first_guess', '__next_guess', '__guesses', '__won', '__results', '__iteration', '__result_str']


    def __init__(self, wordle, iteration) -> None:
        self.__letters = {
            'CORRECT_ALL': [],
            'CORRECT_LETTER': [],
            'WRONG': []
        }

        self.__wordle = wordle
        self.__words = [word for word in ALLOWED_FULL]
        self.__first_guess = random.choice(self.__words)
        self.__next_guess = self.__first_guess
        self.__guesses = 0
        self.__won = False
        self.__results = [None for _ in range(4)]
        self.__result_str = ''
        self.__iteration = iteration
        super().__init__()


    def make_guess(self, raw_guess: str) -> wordle.Guess:
        return self.__wordle.make_guess(raw_guess)


    def read_report(self, guess: wordle.Guess) -> int:
        score = 0
        feedback = guess.get_feedback()
        for i in range(len(feedback)):
            letter, result = feedback[i]
            if result == wordle.CORRECT_ALL:
                self.__letters['CORRECT_ALL'].append((letter, i))
                score += 20
            elif result == wordle.CORRECT_LETTER:
                self.__letters['CORRECT_LETTER'].append((letter, i))
                score += 10
            elif result == wordle.WRONG and letter not in (record[0] for record in self.__letters['CORRECT_LETTER']):
                self.__letters['WRONG'].append((letter, None))
                score += 0
        return score


    def narrow_words(self):
        for letter, index in self.__letters['CORRECT_ALL']:
            self.__words = [word for word in self.__words if word[index] == letter]
        for letter, index in self.__letters['CORRECT_LETTER']:
            self.__words = [word for word in self.__words if letter in word]
        for letter, _ in self.__letters['WRONG']:
            self.__words = [word for word in self.__words if letter not in word]


    def run(self):
        score = 0
        while score < 100 and self.__guesses < wordle.MAX_GUESSES:
            guess = self.make_guess(self.__next_guess)
            score = self.read_report(guess)
            if self.__guesses == 0:
                self.__results[0] = self.__next_guess
                self.__results[1] = score
            # print(guess, score)
            self.narrow_words()
            self.__next_guess = random.choice(self.__words)
            self.__guesses += 1
        
        if score == 100:
            self.__won = True

        self.__results[2] = self.__won
        self.__results[3] = [word for word in self.__words]
        self.__result_str = f'"{self.__results[0]}","{self.__results[1]}","{self.__results[2]}","{self.__results[3]}"\n'

    
    def get_result(self):
        return self.__results


    def get_result_str(self):
        return self.__result_str


def compile_results(results_dict) -> dict:
    avg_results_dict = dict()
    for word, data in results_dict.items():
        avg_results_dict[word] = 0.0 if data[1] == 0 else round(data[0] / data[1], 2)
    return avg_results_dict


def write_result_dict(final_words, out_filename, iters):
    with open(out_filename, 'a') as file:
        file.write('\n')
        file.write(f'Iterations: {iters}\n')
        for entry in final_words:
            word = entry[0]
            avg_score = entry[1]
            file.write(f'    {word} : {avg_score}\n')


def main():
    iterations = 100000000
    iteration = 0
    result_dict = dict()
    result_filename = f'first_quess_results.txt'
    try:
        with alive_bar(iterations) as bar:
            while iteration < iterations:
                # print(f'Running iteration {iteration}')
                game = wordle.Wordle()
                # print(game.get_answer())
                bot = WordleAI(game, iteration)
                bot.run()
                results = bot.get_result()
                guess = results[0]
                score = results[1]
                won = results[2]
                answer = results[3]
                if guess in result_dict:
                    avg_score = result_dict[guess][0]
                    n = result_dict[guess][1]
                    new_average = round((avg_score * (n / (n + 1))) + (score / (n + 1)), 2)
                    result_dict[guess] = [new_average, n + 1]
                else:
                    result_dict[guess] = [score, 1]
                            
                iteration += 1
                bar()
    except (Exception, KeyboardInterrupt) as e:
        print(f'\n{wordle.RED}Error has occured: {e}{wordle.WHITE}')

    final_words = sorted([[word, score] for word, score in result_dict.items()], key= lambda item: item[1], reverse=True)
    write_result_dict(final_words, result_filename, iterations)

    print('Top 10 starting words:')
    print()
    print('    word'.ljust(16) + 'score')
    top_10_words = final_words[:10]
    for i in range(len(top_10_words)):
        print(f'    {top_10_words[i][0]}'.ljust(16) + str(top_10_words[i][1][0]))
    


if __name__ == '__main__':
    main()
