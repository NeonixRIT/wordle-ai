import wordle
import numpy as np
import json
import matplotlib.pyplot as plt
import wordle_utils as utils

with open(utils.NEW_ALLOWED_GUESSES_PATH, 'r', encoding='utf-8') as file:
    ALLOWED_WORDS = sorted([word.strip() for word in file.readlines()])

# words_freq = {}
# with open('./assets/word_frequencies.txt') as words_f:
#     words_freq = {item.split(' ')[0].strip(): float(item.split(' ')[1].strip()) if float(item.split(' ')[1].strip()) > 0 else 1e-19 for item in words_f.readlines()}

# indexes = [float(i) for i, item in enumerate(sorted(words_freq.items(), key=lambda item: item[1]))]
# values = np.array([float(item[1]) for i, item in enumerate(words_freq.items())])
#
# norm_v = values / np.sum(values)
# word_weight_dict = {k: v for k, v in zip(words_freq.keys(), norm_v)}
# print(word_weight_dict)

# print(list(norm_v))
#
# plt.plot(norm_v)
# plt.show()
# print(values)
# exit()


def count_letters():
    count_dict = dict()
    for word in ALLOWED_WORDS:
        for letter in word:
            if letter not in count_dict:
                count_dict[letter] = 0
            count_dict[letter] += 1
    return count_dict


def winrate_dict(filename):
    winrate_dict = dict()
    with open(filename) as file:
        next(file)
        next(file)
        for line in file.readlines():
            tokens = line.strip().split(' : ')
            word = tokens[0]
            winrate = eval(tokens[1])[3]
            winrate_dict[word] = winrate
    return winrate_dict


def weighed_results(count_dict):
    total = len(ALLOWED_WORDS) * 5
    weight_dict = dict()
    for letter in count_dict:
        num_letters = count_dict[letter]
        weight_dict[letter] = round((num_letters / total), 4)
    return weight_dict


def word_weight(weighted_dict):
    word_weights = dict()
    for word in ALLOWED_WORDS:
        word_dict = dict()
        for letter in word:
            if letter in word_dict:
                weight = word_dict[letter][0]
                n = word_dict[letter][1]
                new_n = n + 1
                new_weight = round((weight * (n / new_n)) + (weight / new_n), 5)
                word_dict[letter] = [new_weight, new_n]
            else:
                word_dict[letter] = [weighted_dict[letter], 1]
        word_weights[word] = 0
        for key in word_dict:
            word_weights[word] += word_dict[key][0]
        word_weights[word] = round(word_weights[word], 4)
    return word_weights


def patterns_for_word_group(group_num, total_groups, all_patterns: dict):
    result_patterns = {}
    if group_num == total_groups - 1:
        word_group = ALLOWED_WORDS[len(ALLOWED_WORDS) // total_groups * group_num:]
    else:
        word_group = ALLOWED_WORDS[len(ALLOWED_WORDS) // total_groups * group_num:len(ALLOWED_WORDS) // total_groups * (group_num + 1)]

    for answer in word_group:
        print(f'[{group_num}] Building patterns for {answer} ({len(result_patterns)}/{len(word_group)})...')
        patterns = []
        for first_guess in ALLOWED_WORDS:
            pattern = wordle.Guess(first_guess, answer).get_score_pattern()
            patterns.append(pattern)
        result_patterns[answer] = patterns

    all_patterns[group_num] = result_patterns


def main():
    # count_dict = count_letters()
    # weight_dict = weighed_results(count_dict)
    #
    # word_weights = word_weight(weight_dict)
    # with open('./assets/nyt_word_weights_letter_prob.json', 'w') as file:
    #     json.dump(word_weights, file)

    # words, weight = list(zip(*winrates_dict.items()))
    # rachar
    # andom_word = np.random.choice(words, 5, False, np.array(weight) / sum(weight))
    # print(random_word)
    # full_list = sorted([list for list in winrates_dict.items()], key= lambda item: item[1], reverse=True)
    # top_10_list = full_list[:10]
    # for entry in top_10_list:
    #     print(entry)
    # import wordle_ai
    # import wordle_ai_utils as utils
    # import time
    # time.sleep(3)
    # total_words = len(unlimited_words)
    # starting_index = {k: int(v) for k, v in sorted(removed_words.items(), key=lambda item: int(item[1]))}.popitem()[1] + 1
    # word_num = starting_index
    # for word in sorted(unlimited_words[starting_index:]):
    #     try:
    #         utils.enable_unlimited()
    #         game = wordle.Wordle()
    #         bot = wordle_ai.WordleAI(game, word)
    #         bot.test_word_unlimited()
    #     except AttributeError:
    #         with open('./assets/removed_unlimited_words.txt', 'a') as file:
    #             file.write(f'{word}:{word_num}\n')
    #         print(word)
    #         unlimited_words.remove(word)
    #     word_num += 1
    #     print(f'progress: {round((word_num / total_words) * 100, 4)}%')
    #
    # up_removed_words = {}
    # with open('./assets/removed_unlimited_words.txt') as words_f:
    #     up_removed_words = {item.split(':')[0].strip(): item.split(':')[1].strip() for item in words_f.readlines()}
    #
    # for key in up_removed_words:
    #     if key in unlimited_words:
    #         unlimited_words.remove(key)
    #
    # count_dict = count_letters()
    # weight_dict = weighed_results(count_dict)
    #
    # word_weights = word_weight(weight_dict)
    #
    # with open('./assets/unlimited_words.txt', 'w') as file:
    #     for word in unlimited_words:
    #         file.write(f'{word}\n')
    #
    # with open('./assets/unlimited_word_weights_letter_prob.json', 'w') as file:
    #     json.dump(word_weights, file)
    # from pickle import dump, load
    # from multiprocessing import cpu_count, Pool, Manager

    # all_patterns = Manager().dict()
    # for i in range(cpu_count()):
    #     all_patterns[i] = {}

    # with Pool(cpu_count()) as p:
    #     p.starmap(patterns_for_word_group, [(i, cpu_count(), all_patterns) for i in range(cpu_count())])

    # print('Building answer to patterns...')
    # all_patterns = dict(all_patterns)
    # answer_to_patterns = {}
    # for group_num in range(len(all_patterns)):
    #     print(f'\t [{group_num}] Started...')
    #     for word in sorted(list(all_patterns[group_num].keys())):
    #         answer_to_patterns[word] = list(all_patterns[group_num][word])

    # print('Building final patterns list...')
    # final_patterns_list = []
    # for answer_word in sorted(list(answer_to_patterns.keys())):
    #     final_patterns_list.append(answer_to_patterns[answer_word])

    # print('Saving pickled list...')
    # with open('./assets/patterns.pkl', 'wb') as file:
    #     dump(final_patterns_list, file)
    # import sys
    # with open('./assets/patterns.pkl', 'rb') as file:
    #     patterns = load(file)
    #     print(type(patterns))
    #     print(len(patterns))
    #     for i in range(14855):
    #         pattern = patterns[i][i]
    #         assert pattern == (20, 20, 20, 20, 20)
    # import json
    # word_weights = None
    # with open('./assets/nyt_first_guess_word_weights_info_theory.json') as file:
    #     word_weights = json.load(file)




    pass


if __name__ == '__main__':
    main()
