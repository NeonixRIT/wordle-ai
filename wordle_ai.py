# import wordle as w
import wordle_utils as utils

# import pickle
# import torch
import numpy as np
# import json

import aiomysql
import asyncio

# from copy import deepcopy
from time import perf_counter
from os import cpu_count

import concurrent.futures as concurr

# Colours used in output
# RED = '\033[1;31m'
# GREEN = '\033[1;32m'
# WHITE = '\033[0m'
# YELLOW = '\033[1;33m'

# Game Constants
# WORD_LEN = 5
# MAX_GUESSES = 6
# ASSETS_PATH = '/assets'
# ALLOWED_GUESSES_PATH = f'.{ASSETS_PATH}/wordle-allowed-guesses.txt'
# NEW_ALLOWED_GUESSES_PATH = f'.{ASSETS_PATH}/wordle_nyt_allowed_guesses.txt'
# POSSIBLE_ANSWERS_PATH = f'.{ASSETS_PATH}/wordle-answers.txt'
# NEW_POSSIBLE_ANSWERS_PATH = f'.{ASSETS_PATH}/wordle_nyt_answers.txt'

# Numerical values too handle guess results easier
# CORRECT_ALL = 20 # correct letter and position.
# CORRECT_LETTER = 10 # correct letter wrong position.
# WRONG = 0 # Wrong letter and position.
# MAX_SCORE = CORRECT_ALL * WORD_LEN # Correct guess score

# Assign colour to guess result
# GUESS_RESULT_DICT = {
#     CORRECT_ALL: GREEN,
#     CORRECT_LETTER: YELLOW,
#     WRONG: WHITE
# }

# Numerical values too handle guess results easier
# CORRECT_ALL = 20 # correct letter and position.
# CORRECT_LETTER = 10 # correct letter wrong position.
# WRONG = 0 # Wrong letter and position.
# MAX_SCORE = CORRECT_ALL * WORD_LEN # Correct guess score

# Assign colour to guess result
# GUESS_RESULT_DICT = {
#     CORRECT_ALL: GREEN,
#     CORRECT_LETTER: YELLOW,
#     WRONG: WHITE
# }

# ALPHABET = 'abcdefghijklmnopqrstuvwxyz'

DB_CONFIG = {
    'user': 'wordleai',
    'password': 'wordleai',
    'db': 'wordleai',
    'host': '127.0.0.1',
    'port': 3306,
    'auth_plugin': 'mysql_native_password',
}

with open(utils.NEW_ALLOWED_GUESSES_PATH, 'r', encoding='utf-8') as file:
    ALLOWED_WORDS = sorted([word.strip() for word in file.readlines()])

# PATTERN_DTYPE = np.dtype([('pos0', 'i1'), ('pos1', 'i1'), ('pos2', 'i1'), ('pos3', 'i1'), ('pos4', 'i1')])
ALL_POSSIBLE_PATTERNS = [(i, j, k, p, m) for i in range(0, 21, 10) for j in range(0, 21, 10) for k in range(0, 21, 10) for p in range(0, 21, 10) for m in range(0, 21, 10)]
# ALL_POSSIBLE_PATTERNS_NPARRAY = np.array([(i, j, k, p, m) for i in range(0, 21, 10) for j in range(0, 21, 10) for k in range(0, 21, 10) for p in range(0, 21, 10) for m in range(0, 21, 10)], dtype=PATTERN_DTYPE)
ALL_POSSIBLE_PATTERNS_PAT_TO_IDX = {pattern: i for i, pattern in enumerate(ALL_POSSIBLE_PATTERNS)}
# PATTERNS = np.load('./assets/patterns.npy')

# PATTERN_LOCATION_LEN_IDX = {
#     47257244: [0], 14019939: [1], 10847464: [2], 14336735: [3], 4003247: [4],
#     2104052: [5], 5406402: [6], 1082824: [7], 1522078: [8], 12174005: [9], 2891195: [10],
#     2087306: [11], 3351048: [12], 697374: [13], 366378: [14], 994871: [15], 159407: [16],
#     155240: [17], 4124332: [18], 886590: [19], 906358: [20], 922195: [21], 166899: [22],
#     115663: [23], 553922: [24], 67045: [25], 172256: [26], 12419684: [27], 3005013: [28],
#     2006189: [29], 3210931: [30], 670251: [31], 330376: [32], 827788: [33], 138349: [34],
#     145310: [35], 3068022: [36], 547100: [37], 381332: [38], 652031: [39], 91952: [40],
#     44170: [41], 142557: [42], 15424: [43], 16461: [44], 776280: [45], 132301: [46], 101805: [47],
#     151641: [48], 18687: [49], 12611: [50], 51123: [51], 5151: [52], 5130: [53, 107], 8997174: [54],
#     1671226: [55], 2010308: [56], 1549696: [57], 278463: [58], 187728: [59], 888914: [60],
#     109594: [61], 266252: [62], 1351459: [63], 207171: [64], 193900: [65], 211050: [66], 26317: [67],
#     16842: [68], 104048: [69], 10472: [70], 13585: [71, 143], 887348: [72], 104132: [73], 188418: [74],
#     99167: [75], 10838: [76], 8326: [77, 155], 110952: [78], 5499: [79, 159], 39706: [80], 9441567: [81],
#     2474717: [82], 1376270: [83], 2370373: [84], 530419: [85], 224987: [86], 887501: [87], 149608: [88],
#     134191: [89], 2059234: [90], 399016: [91], 209160: [92], 434995: [93], 64409: [94], 26752: [95],
#     129348: [96], 14895: [97], 10633: [98], 635767: [99], 117937: [100], 73748: [101], 111962: [102],
#     14801: [103], 7417: [104], 57833: [105], 6278: [106], 2227240: [108], 446921: [109], 227953: [110],
#     450043: [111], 68711: [112], 26084: [113], 117241: [114], 14205: [115], 12538: [116], 424001: [117],
#     54718: [118], 29741: [119], 63980: [120], 4941: [121], 2154: [122], 14227: [123], 945: [124],
#     601: [125], 97870: [126], 13332: [127], 5299: [128], 13834: [129], 1150: [130], 215: [131],
#     4497: [132], 261: [133], 332: [134], 1230253: [135], 187103: [136], 178386: [137], 161219: [138],
#     20515: [139], 12734: [140], 96320: [141], 9475: [142], 150034: [144], 15791: [145], 13639: [146],
#     15699: [147], 1022: [148], 463: [149], 9018: [150], 437: [151], 778: [152], 76171: [153], 6744: [154],
#     6042: [156], 290: [157], 456: [158], 330: [160], 3904612: [162], # 0: [161, 215, 233, 239, 241]
#     811443: [163], 782748: [164], 899652: [165], 166450: [166], 99299: [167], 412090: [168], 47532: [169],
#     104004: [170], 770074: [171], 120152: [172], 105314: [173], 149440: [174], 18715: [175], 11044: [176],
#     51070: [177], 4855: [178], 5018: [179, 197], 372382: [180], 48751: [181], 69014: [182], 55927: [183],
#     5392: [184], 4606: [185, 209], 45512: [186], 2460: [187, 213], 13052: [188], 787575: [189],
#     119788: [190], 105449: [191], 151753: [192], 17290: [193], 11540: [194], 39556: [195], 3283: [196],
#     143705: [198], 13964: [199], 13927: [200], 19241: [201], 1280: [202], 591: [203], 4916: [204],
#     158: [205], 524: [206], 50402: [207], 4498: [208], 6672: [210], 210: [211], 424: [212], 192: [214],
#     870042: [216], 110944: [217], 169022: [218], 108528: [219], 14443: [220], 7658: [221, 227],
#     83342: [222], 5007: [223, 231], 22542: [224], 84486: [225], 8214: [226], 9855: [228],
#     574: [229], 566: [230], 312: [232], 107976: [234], 7128: [235, 237], 19332: [236], 540: [238],
#     15602: [240], 14855: [242]
# }
# PATTERN_LOCATION_LENS = [
#     47257244, 14336735, 14019939, 12419684, 12174005, 10847464, 9441567, 8997174, 5406402,
#     4124332, 4003247, 3904612, 3351048, 3210931, 3068022, 3005013, 2891195, 2474717, 2370373,
#     2227240, 2104052, 2087306, 2059234, 2010308, 2006189, 1671226, 1549696, 1522078, 1376270,
#     1351459, 1230253, 1082824, 994871, 922195, 906358, 899652, 888914, 887501, 887348, 886590,
#     870042, 827788, 811443, 787575, 782748, 776280, 770074, 697374, 670251, 652031, 635767,
#     553922, 547100, 530419, 450043, 446921, 434995, 424001, 412090, 399016, 381332, 372382,
#     366378, 330376, 278463, 266252, 227953, 224987, 211050, 209160, 207171, 193900, 188418,
#     187728, 187103, 178386, 172256, 169022, 166899, 166450, 161219, 159407, 155240, 151753,
#     151641, 150034, 149608, 149440, 145310, 143705, 142557, 138349, 134191, 132301, 129348,
#     120152, 119788, 117937, 117241, 115663, 111962, 110952, 110944, 109594, 108528, 107976,
#     105449, 105314, 104132, 104048, 104004, 101805, 99299, 99167, 97870, 96320, 91952, 84486,
#     83342, 76171, 73748, 69014, 68711, 67045, 64409, 63980, 57833, 55927, 54718, 51123, 51070,
#     50402, 48751, 47532, 45512, 44170, 39706, 39556, 29741, 26752, 26317, 26084, 22542, 20515,
#     19332, 19241, 18715, 18687, 17290, 16842, 16461, 15791, 15699, 15602, 15424, 14895, 14855,
#     14801, 14443, 14227, 14205, 13964, 13927, 13834, 13639, 13585, 13585, 13332, 13052, 12734,
#     12611, 12538, 11540, 11044, 10838, 10633, 10472, 9855, 9475, 9018, 8326, 8326, 8214, 7658,
#     7658, 7417, 7128, 7128, 6744, 6672, 6278, 6042, 5499, 5499, 5392, 5299, 5151, 5130, 5130,
#     5018, 5018, 5007, 5007, 4941, 4916, 4855, 4606, 4606, 4498, 4497, 3283, 2460, 2460, 2154,
#     1280, 1150, 1022, 945, 778, 601, 591, 574, 566, 540, 524, 463, 456, 437, 424, 332, 330,
#     312, 290, 261, 215, 210, 192, 158
# ]


def run_async_in_process(async_func, *args, **kwargs):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(async_func(*args, **kwargs))
    loop.close()
    del loop
    return result


async def create_pattern_locations_table(drop_if_existing=False):
    async with aiomysql.connect(**DB_CONFIG) as db_conn:
        db_conn: aiomysql.Connection
        async with db_conn.cursor() as cursor:
            cursor: aiomysql.Cursor
            if drop_if_existing:
                await cursor.execute('DROP TABLE IF EXISTS pattern_locations')
            await cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS pattern_locations (
                    pattern_idx TINYINT UNSIGNED NOT NULL,
                    row_idx SMALLINT UNSIGNED NOT NULL,
                    col_idx SMALLINT UNSIGNED NOT NULL,
                    PRIMARY KEY (pattern_idx, row_idx, col_idx)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                '''
            )
            await db_conn.commit()


async def create_first_guess_words_remaining_table(drop_if_existing=True):
    '''
    This table is guess info only for the first guess
    due to the time it takes to process.
    '''
    async with aiomysql.connect(**DB_CONFIG) as db_conn:
        db_conn: aiomysql.Connection
        async with db_conn.cursor() as cursor:
            cursor: aiomysql.Cursor
            if drop_if_existing:
                await cursor.execute('DROP TABLE IF EXISTS first_guess_words_remaining')
            await cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS first_guess_words_remaining (
                    guess_idx SMALLINT UNSIGNED NOT NULL,
                    pattern_idx TINYINT UNSIGNED NOT NULL,
                    word_remaining_idx SMALLINT UNSIGNED NOT NULL,
                    PRIMARY KEY (guess_idx, pattern_idx, word_remaining_idx)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                '''
            )
            await db_conn.commit()


async def create_guess_info_table(drop_if_existing=True):
    '''
    Create guess_info table in database
    This table is reset every time WordleAI starts a new game
    Holds information about what words are valid answers after each guess should
    the AI choose to guess that word.
    '''
    async with aiomysql.connect(**DB_CONFIG) as db_conn:
        db_conn: aiomysql.Connection
        async with db_conn.cursor() as cursor:
            cursor: aiomysql.Cursor
            if drop_if_existing:
                await cursor.execute('DROP TABLE IF EXISTS guess_info')
            await cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS guess_info (
                    guess_idx SMALLINT UNSIGNED NOT NULL,
                    pattern_idx TINYINT UNSIGNED NOT NULL,
                    word_remaining_idx SMALLINT UNSIGNED NOT NULL,
                    PRIMARY KEY (guess_idx, pattern_idx, word_remaining_idx)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                '''
            )
            await db_conn.commit()


async def clear_table(table_name: str):
    async with aiomysql.connect(**DB_CONFIG) as db_conn:
        db_conn: aiomysql.Connection
        async with db_conn.cursor() as cursor:
            cursor: aiomysql.Cursor
            await cursor.execute(f'DELETE FROM {table_name} WHERE 1=1')
            await db_conn.commit()


# class WordleAI:
#     """
#     Rudimentary AI to solve wordle puzzle, either from web GUI or internal CLI
#     """
#     __slots__ = ['__wordle', '__available_words', '__word_weights', '__last_guess_score', '__next_guess_info', '__valid_patterns', '__guessed']

#     def __init__(self, game: w.Wordle) -> None:
#         self.__wordle = game
#         self.__available_words = {i: word for i, word in enumerate(ALLOWED_WORDS)}
#         self.__valid_patterns = list(range(len(ALL_POSSIBLE_PATTERNS)))
#         self.__guessed = []
#         with open('./assets/nyt_first_guess_info.json', 'r', encoding='utf-8') as file_1:
#             self.__word_weights = json.load(file_1)
#         self.__last_guess_score = 0

#     async def get_next_guess_info_process(self, table_name, pattern_idx: int, row_idx, start_offset: int, batch_size: int):
#         async with aiomysql.connect(**DB_CONFIG) as db_conn:
#             db_conn: aiomysql.Connection
#             async with db_conn.cursor() as cursor:
#                 cursor: aiomysql.Cursor
#                 await cursor.execute(f'SELECT row_idx, col_idx FROM pattern_locations WHERE pattern_idx = {pattern_idx} AND row_idx = {row_idx} LIMIT {start_offset}, {batch_size}')
#                 batch = await cursor.fetchall()
#                 await cursor.execute(f'INSERT INTO {table_name} (guess_idx, pattern_idx, word_remaining_idx) VALUES {", ".join([str((row_idx, pattern_idx, col_idx)) for row_idx, col_idx in batch])}')
#                 await db_conn.commit()
#         # print(f'Processed {batch_size} rows of {pattern_idx}, {row_idx}.')

#     async def get_next_guess_info(self):
#         guess_num = MAX_GUESSES - self.__wordle.get_guesses_left()
#         table_in_use = 'first_guess_words_remaining' if guess_num == 0 else 'guess_info'
#         async with aiomysql.connect(**DB_CONFIG) as db_conn:
#             db_conn: aiomysql.Connection
#             async with db_conn.cursor() as cursor:
#                 cursor: aiomysql.Cursor
#                 with concurr.ProcessPoolExecutor(max_workers=cpu_count()) as executor:
#                     for pattern_idx in self.__valid_patterns:
#                         for row_idx in self.__available_words:
#                             await cursor.execute(f'SELECT COUNT(*) FROM pattern_locations WHERE pattern_idx = {pattern_idx} AND row_idx = {row_idx}')
#                             num_rows = (await cursor.fetchone())[0]
#                             if num_rows == 0:
#                                 continue
#                             if num_rows < cpu_count() * 2:
#                                 batch_size = 1
#                             else:
#                                 batch_size = num_rows // (cpu_count() * 2)
#                             print(f'Processing {num_rows} rows of {pattern_idx}, {row_idx} in batches of {batch_size}...')
#                             for start_offset in range(0, num_rows, batch_size):
#                                 executor.submit(run_async_in_process, self.get_next_guess_info_process, table_in_use, pattern_idx, row_idx, start_offset, batch_size)

#     def make_guess(self, word_index: int) -> w.Guess:
#         """
#         Make a guess on an internal Wordle game
#         """
#         if word_index not in self.__available_words:
#             raise ValueError(f'Word index {word_index} not in available words')
#         word = self.__available_words[word_index]
#         self.__guessed.append(word)
#         del self.__available_words[word_index]
#         return self.__wordle.make_guess(word)

#     async def narrow_words(self, guess_index: int, pattern: tuple[int, int, int, int, int]) -> None:
#         async with aiomysql.connect(**DB_CONFIG) as db_conn:
#             db_conn: aiomysql.Connection
#             async with db_conn.cursor() as cursor:
#                 cursor: aiomysql.Cursor
#                 pattern_index = ALL_POSSIBLE_PATTERNS_PAT_TO_IDX[pattern]
#                 await cursor.execute(f'SELECT col_idx FROM pattern_locations WHERE pattern_idx = {pattern_index} AND row_idx = {guess_index} AND col_idx NOT IN {tuple(self.__guessed)}')
#                 words_remaining = await cursor.fetchall()
#                 self.__available_words = {
#                     word_index[0]: ALLOWED_WORDS[word_index[0]] for word_index in words_remaining
#                 }

#     def narrow_patterns(self, guess_pattern: tuple[int, int, int, int, int]) -> None:
#         green_idxs = [i for i, score in enumerate(guess_pattern) if score == 20]
#         self.__valid_patterns = [i for i, pattern in enumerate(ALL_POSSIBLE_PATTERNS) if all([pattern[idx] == guess_pattern[idx] for idx in green_idxs])]

#     def get_reward(self) -> int:
#         """
#         Get reward for final game state

#         Things I want to incentivize:
#             Winning the game
#             Having more guesses left dont want to reward for guessing answer first try.

#         Things I want to disincentivize:
#             Losing the game

#         Ill adjust this as I go if obvious improvements are needed
#         """
#         guess = self.__wordle.get_board().get_last_guess()
#         guess_reward = guess.get_score() - self.__last_guess_score * 0.5 # MAX = 50
#         self.__last_guess_score = guess.get_score()

#         words_left = len(self.__available_words)
#         words_left_reward = ((len(ALLOWED_WORDS) - words_left) ** 2) * (1 / 4_400_000) # MAX = 50
#         if not self.__wordle.is_game_over():
#             return guess_reward + words_left_reward

#         game_won = self.__wordle.is_game_won()
#         guesses_left = self.__wordle.get_guesses_left()
#         game_won_reward = 600 if game_won else -800

#         # MAX = 200
#         guesses_left_reward = guesses_left * 50 if game_won else 0

#         # MAX = 200
#         words_left_reward = (words_left ** 2) * (1 / 1_100_000) if game_won else -((words_left ** 2) * (1 / 1_100_000))

#         return game_won_reward + guesses_left_reward + words_left_reward

#     async def play_step(self, word_index: int) -> tuple[int, bool]:
#         """
#         Play a step in the game
#         """
#         guess = self.make_guess(word_index)
#         guess_pattern = guess.get_score_pattern()
#         print(guess)
#         await self.narrow_words(word_index, guess_pattern)
#         self.narrow_patterns(guess_pattern)
#         await self.get_next_guess_info()
#         reward = self.get_reward()
#         done = self.__wordle.is_game_over()
#         return reward, done

#     def get_valid_action_mask(self, device: torch.device | None = None):
#         mask = [-1e6 if i not in self.__available_words else 0 for i in range(len(ALLOWED_WORDS))]
#         return torch.tensor(mask, dtype=torch.float, device=device)

#     def get_prob_action_mask(self, device: torch.device | None = None):
#         return torch.tensor(np.array(list(self.__word_weights_letter_prob.values())), dtype=torch.float, device=device)

#     def get_valid_actions(self):
#         self.narrow_words()
#         return list(self.__available_words.keys())

#     def reset(self) -> None:
#         self.__wordle = w.Wordle()
#         self.__available_words = {i: word for i, word in enumerate(ALLOWED_WORDS)}
#         with open('./assets/nyt_word_weights_letter_prob.json', 'r', encoding='utf-8') as file_1:
#             self.__word_weights_letter_prob = dict(json.loads(file_1.read()))
#         self.__guessed = set()
#         self.__last_guess_score = 0
#         self.__score = 0

#     def get_game(self) -> w.Wordle:
#         """
#         Get internal Wordle game
#         """
#         return self.__wordle


# def manual():
#     game = w.Wordle('sassy')
#     agent = WordleAI(game)
#     while not game.is_game_over():
#         print(game.get_board())
#         print([[agent._WordleAI__available_words[i], i] for i in agent.get_valid_actions()])
#         print(agent._WordleAI__hints_dict)
#         print(agent._WordleAI__letter_count)
#         action = int(input('Enter action: '))
#         agent.play_step(action)


async def just_data_yknow(first_guess_idx: int):
    start = perf_counter()
    async with aiomysql.connect(**DB_CONFIG) as db_conn:
        db_conn: aiomysql.Connection
        async with db_conn.cursor() as cursor:
            cursor: aiomysql.Cursor
            for first_pattern_idx in range(0, len(ALL_POSSIBLE_PATTERNS)):
                await cursor.execute(f'SELECT col_idx FROM pattern_locations WHERE pattern_idx = {first_pattern_idx} AND row_idx = {first_guess_idx} AND col_idx != {first_guess_idx}')
                first_words_remaining = [res[0] for res in (await cursor.fetchall())]
                first_words_remaining_len = len(first_words_remaining)
                if first_words_remaining_len == 0:
                    continue
                guess_pattern = ALL_POSSIBLE_PATTERNS[first_pattern_idx]
                green_idxs = [i for i, score in enumerate(guess_pattern) if score == 20]
                valid_patterns = [i for i, pattern in enumerate(ALL_POSSIBLE_PATTERNS) if all([pattern[idx] == guess_pattern[idx] for idx in green_idxs])]
                if len(valid_patterns) == 0:
                    continue
                values = []
                # i = 0
                for second_guess_idx in first_words_remaining:
                    await cursor.execute(f'SELECT * FROM second_guess_info WHERE first_guess_idx = {first_guess_idx} AND first_pattern_idx = {first_pattern_idx} AND second_guess_idx = {second_guess_idx}')
                    if (await cursor.fetchone()) is not None:
                        continue
                    expected_info = 0
                    for second_pattern_idx in valid_patterns:
                        # i += 1
                        # print(f'[{first_guess_idx}, {first_pattern_idx}, {second_guess_idx}]'.ljust(9), f'Processing ({i}/{first_words_remaining_len * len(valid_patterns)})', sep='', end='\r')
                        await cursor.execute(f'SELECT COUNT(*) FROM pattern_locations pl1 JOIN pattern_locations pl2 ON pl1.col_idx = pl2.col_idx WHERE pl1.pattern_idx = {second_pattern_idx} AND pl1.row_idx = {second_guess_idx}  AND pl1.col_idx NOT IN ({first_guess_idx}, {second_guess_idx}) AND pl2.pattern_idx = {first_pattern_idx} AND pl2.row_idx = {first_guess_idx} AND pl2.col_idx != {first_guess_idx}')
                        second_words_remaining_len = (await cursor.fetchone())[0]
                        if second_words_remaining_len == 0:
                            continue
                        pattern_prob = second_words_remaining_len / first_words_remaining_len
                        pattern_info = np.log2(1 / pattern_prob)
                        expected_info += pattern_prob * pattern_info
                    values.append(tuple([first_guess_idx, first_pattern_idx, second_guess_idx, expected_info]))
                if not values:
                    continue
                await cursor.execute(f'INSERT INTO second_guess_info (first_guess_idx, first_pattern_idx, second_guess_idx, expected_info) VALUES {", ".join([str(value) for value in values])}')
                await db_conn.commit()
                # print()
    return perf_counter() - start


async def main():
    # await create_first_guess_words_remaining_table()
    # await clear_table('first_guess_words_remaining')
    await clear_table('guess_info')
    # game = w.Wordle()
    # agent = WordleAI(game)
    first_guess_idxs = []
    async with aiomysql.connect(**DB_CONFIG) as db_conn:
        db_conn: aiomysql.Connection
        async with db_conn.cursor() as cursor:
            cursor: aiomysql.Cursor
            await cursor.execute('SELECT first_guess_idx FROM second_guess_info GROUP BY first_guess_idx HAVING COUNT(first_pattern_idx) != 14854')
            first_guess_idxs = [res[0] for res in (await cursor.fetchall())]

    print(f'Starting at {first_guess_idxs[0]} (1/{len(first_guess_idxs)})...')
    times = []
    with concurr.ProcessPoolExecutor(max_workers=cpu_count(), max_tasks_per_child=1) as executor:
        tasks = {executor.submit(run_async_in_process, just_data_yknow, first_guess_idx): first_guess_idx for first_guess_idx in first_guess_idxs}
        for task in concurr.as_completed(tasks):
            time = task.result()
            times.append(time)
            total_seconds = sum(times)
            mean_seconds = total_seconds // len(times)
            min_time = min(times)
            max_time = max(times)
            eta = (mean_seconds * (len(first_guess_idxs) - len(times))) // cpu_count()
            print(
                f' ({len(times)}/{len(first_guess_idxs)}) Min: {int(min_time // 60)}m {round(min_time % 60)}s',
                f'Max: {int(max_time // 60)}m {round(max_time % 60)}s',
                f'Mean: {int(mean_seconds // 60)}m {round(mean_seconds % 60)}s',
                f'Total: {int(total_seconds // 60)}m {round(total_seconds % 60)}s',
                f'ETA: {int(eta // 60)}m {round(eta % 60)}s {" " * 25}',
                sep=' - ',
                end='\r',
                flush=True
            )



    exit()


if __name__ == '__main__':
    asyncio.run(main())
