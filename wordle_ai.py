import random
import wordle

from alive_progress import alive_bar

ALLOWED_FULL = [word.strip() for word in open(wordle.POSSIBLE_ANSWERS_PATH).readlines()]

class WordleAI():
    __slots__ = ['__letters', '__wordle', '__words', '__first_guess', '__next_guess', '__guesses', '__won', '__results', '__result_str', '__yellow_tried']


    def __init__(self, wordle: wordle.Wordle) -> None:
        self.__letters = {
            'CORRECT_ALL': set(),
            'CORRECT_LETTER': set(),
            'WRONG': set()
        }

        self.__wordle = wordle
        self.__words = [word for word in ALLOWED_FULL]
        self.__first_guess = 'soare'
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
    won = 0
    lost = 0
    for _ in range(10000):
        game = wordle.Wordle()
        # print(game.get_answer())
        bot = WordleAI(game)
        bot.run()
        results = bot.get_result()
        guess = results[0]
        score = results[1]
        won = results[2]
        answer = results[3]
        if won:
            won += 1
        else:
            lost += 1
        # print(game)
        # print(game.get_answer())
        # print(answer)
    print(f'Won: {won}')
    print(f'Lost: {lost}')



if __name__ == '__main__':
    main()
