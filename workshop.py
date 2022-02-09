import wordle
import numpy as np
import json

unlimited_words = []
with open('./assets/dictionary.txt') as words_f:
    unlimited_words = [word.strip() for word in words_f if len(word.strip()) == 5]
    
removed_words = {}
with open('./assets/removed_unlimited_words.txt') as words_f:
    removed_words = {item.split(':')[0].strip(): item.split(':')[1].strip() for item in words_f.readlines()}
    

def count_letters():
    count_dict = dict()
    for word in unlimited_words:
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
    total = len(unlimited_words) * 5
    weight_dict = dict()
    for letter in count_dict:
        num_letters = count_dict[letter]
        weight_dict[letter] = round((num_letters / total), 4)
    return weight_dict


def word_weight(weighted_dict):
    word_weights = dict()
    for word in unlimited_words:
        word_dict = dict()
        for letter in word:
            if letter in word_dict:
                weight = word_dict[letter][0]
                n = word_dict[letter][1]
                new_n = n + 1
                new_weight = round((weight * (n / (new_n))) + (weight / (new_n)), 5)
                word_dict[letter] = [new_weight, new_n]
            else:
                word_dict[letter] = [weighted_dict[letter], 1]
        word_weights[word] = 0
        for key in word_dict:
            word_weights[word] += word_dict[key][0]
        word_weights[word] = round(word_weights[word], 4)
    return word_weights


def main():
    # count_dict = count_letters()
    # weight_dict = weighed_results(count_dict)

    # word_weights = word_weight(weight_dict)
    # winrates_dict = winrate_dict('first_guess_results_winrate.txt')
    # with open('./assets/word_weights_winrate.json', 'w') as file:
    #     json.dump(winrates_dict, file)
    # with open('./assets/unlimited_word_weights_letter_prob.json', 'w') as file:
    #     json.dump(word_weights, file)
    # word_weights = None
    # with open('./assets/word_weights.json') as file:
    #     word_weights = json.loads(file.read())
    
    # words, weight = list(zip(*winrates_dict.items()))
    # rachar
    # andom_word = np.random.choice(words, 5, False, np.array(weight) / sum(weight))
    # print(random_word)
    # full_list = sorted([list for list in winrates_dict.items()], key= lambda item: item[1], reverse=True)
    # top_10_list = full_list[:10]
    # for entry in top_10_list:
    #     print(entry)
    import wordle_ai
    import wordle_ai_utils as utils
    import time
    time.sleep(3)
    total_words = len(unlimited_words)
    starting_index = {k: int(v) for k, v in sorted(removed_words.items(), key=lambda item: int(item[1]))}.popitem()[1] + 1
    word_num = starting_index
    for word in sorted(unlimited_words[starting_index:]):
        try:
            utils.enable_unlimited()
            game = wordle.Wordle()
            bot = wordle_ai.WordleAI(game, word)
            bot.test_word_unlimited()
        except AttributeError:
            with open('./assets/removed_unlimited_words.txt', 'a') as file:
                file.write(f'{word}:{word_num}\n')
            print(word)
            unlimited_words.remove(word)
        word_num += 1
        print(f'progress: {round((word_num / total_words) * 100, 4)}%')
        
    up_removed_words = {}
    with open('./assets/removed_unlimited_words.txt') as words_f:
        up_removed_words = {item.split(':')[0].strip(): item.split(':')[1].strip() for item in words_f.readlines()}
        
    for key in up_removed_words:
        if key in unlimited_words:
            unlimited_words.remove(key)

    count_dict = count_letters()
    weight_dict = weighed_results(count_dict)

    word_weights = word_weight(weight_dict)

    with open('./assets/unlimited_words.txt', 'w') as file:
        for word in unlimited_words:
            file.write(f'{word}\n')
    
    with open('./assets/unlimited_word_weights_letter_prob.json', 'w') as file:
        json.dump(word_weights, file)


if __name__ == '__main__':
    main()
