import csv
import random
import wordle

ALLOWED_FULL = [word.strip() for word in open(wordle.ALLOWED_GUESSES_PATH).readlines()]

from alive_progress import alive_bar

class WordleAI():
    __slots__ = ['__letters', '__wordle', '__words', '__first_guess', '__next_guess', '__guesses', '__won', '__results', '__result_str', '__yellow_tried']


    def __init__(self, wordle: wordle.Wordle, starting_word: str = 'soare') -> None:
        self.__letters = {
            'CORRECT_ALL': set(),
            'CORRECT_LETTER': set(),
            'WRONG': set()
        }

        self.__wordle = wordle
        self.__words = [word for word in ALLOWED_FULL]
        self.__first_guess = starting_word
        self.__next_guess = self.__first_guess
        self.__guesses = 0
        self.__won = False
        self.__results = [None for _ in range(4)]
        self.__result_str = ''
        self.__yellow_tried = []


    def make_guess(self, raw_guess: str) -> wordle.Guess:
        return self.__wordle.make_guess(raw_guess)


    def read_report(self, guess: wordle.Guess):
        feedback = guess.get_feedback()
        for i in range(len(feedback)):
            letter, result = feedback[i]
            if result == wordle.CORRECT_ALL:
                self.__letters['CORRECT_ALL'].add((letter, i))

                if (letter, None) in self.__letters['WRONG']:
                    self.__letters['WRONG'].remove((letter, None))
            elif result == wordle.CORRECT_LETTER:
                self.__letters['CORRECT_LETTER'].add((letter, i))
                self.__yellow_tried.append((letter, i))
                if (letter, None) in self.__letters['WRONG']:
                    self.__letters['WRONG'].remove((letter, None))
            elif result == wordle.WRONG and (letter not in [record[0] for record in self.__letters['CORRECT_ALL']] and letter not in [record[0] for record in self.__letters['CORRECT_LETTER']]):
                self.__letters['WRONG'].add((letter, None))


    def narrow_words(self):
        for letter, index in self.__letters['CORRECT_ALL']:
            self.__words = [word for word in self.__words if word[index] == letter]
        for letter, index in self.__letters['CORRECT_LETTER']:
            self.__words = [word for word in self.__words if letter in word]
        for letter, _ in self.__letters['WRONG']:
            self.__words = [word for word in self.__words if letter not in word]
        for letter, index in self.__yellow_tried:
            self.__words = [word for word in self.__words if word[index] != letter]


    def run(self):
        score = 0
        while score < 100 and self.__guesses < wordle.MAX_GUESSES:
            guess = self.make_guess(self.__next_guess)
            self.read_report(guess)
            score = guess.get_score()
            if self.__guesses == 0:
                self.__results[0] = self.__next_guess
                self.__results[1] = score
            self.narrow_words()
            self.__next_guess = random.choice(self.__words)
            self.__guesses += 1
        
        if score == 100:
            self.__won = True

        self.__results[2] = self.__won
        self.__results[3] = [word for word in self.__words]
        self.__result_str = f'"{self.__results[0]}","{self.__results[1]}","{self.__results[2]}","{self.__results[3]}"\n'

    
    def get_result(self) -> list: return self.__results
    def get_result_str(self) -> str: return self.__result_str


def write_result_dict(final_words, out_filename, iters):
    with open(out_filename, 'a') as file:
        file.write('\n')
        file.write(f'Iterations: {iters}\n')
        for entry in final_words:
            word = entry[0]
            avg_score = entry[1]
            file.write(f'    {word} : {avg_score}\n')


def output_file_to_dict(filename):
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



def main():
    iterations = 25000000
    iteration = 0
    result_dict = dict()
    score_filename = f'first_quess_results_score.txt'
    winrate_filename = f'first_quess_results_winrate.txt'
    try:
        with alive_bar(iterations) as bar:
            while iteration < iterations:
                # print(f'Running iteration {iteration}')
                game = wordle.Wordle()
                # print(game.get_answer())
                bot = WordleAI(game, random.choice(ALLOWED_FULL))
                bot.run()
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
    write_result_dict(final_words_score, score_filename, iterations)
    write_result_dict(final_words_winrate, winrate_filename, iterations)

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


if __name__ == '__main__':
    main()
