import wordle
import numpy as np
import json


def count_letters():
    count_dict = dict()
    for word in wordle.ALLOWED_WORDS:
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
    total = len(wordle.ALLOWED_WORDS) * 5
    weight_dict = dict()
    for letter in count_dict:
        num_letters = count_dict[letter]
        weight_dict[letter] = round((num_letters / total), 4)
    return weight_dict


def word_weight(weighted_dict):
    word_weights = dict()
    for word in wordle.ALLOWED_WORDS:
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
    import json
    winrates_dict = winrate_dict('first_guess_results_winrate.txt')
    with open('./assets/word_weights_winrate.json', 'w') as file:
        json.dump(winrates_dict, file)
    # with open('./assets/word_weights.json', 'w') as file:
    #     json.dump(word_weights, file)
    # word_weights = None
    # with open('./assets/word_weights.json') as file:
    #     word_weights = json.loads(file.read())
    
    words, weight = list(zip(*winrates_dict.items()))
    random_word = np.random.choice(words, 5, False, np.array(weight) / sum(weight))
    print(random_word)
    full_list = sorted([list for list in winrates_dict.items()], key= lambda item: item[1], reverse=True)
    top_10_list = full_list[:10]
    for entry in top_10_list:
        print(entry)


if __name__ == '__main__':
    main()
