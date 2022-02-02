'''
Help a user solve a wordle from web GUI without doing it for them.
'''
import time

import wordle_utils
import wordle_ai_utils
import wordle_ai

def help_solve_gui():
    '''
    Helps a user solve a wordle from web GUI without doing it for them.
    '''
    bot = wordle_ai.WordleAI(None)
    score = 0
    time.sleep(1)
    guesses = 0
    possible_answers = [[], []]
    print(f'Recommended first guess: {bot.get_next_guess()}')
    input('Press Enter after you\'ve made your first guess...')
    while score < 100 and guesses < wordle_utils.MAX_GUESSES and len(possible_answers) > 1:
        time.sleep(1)
        try:
            # wait for player to make guess
            # update internal board from image
            game_img = wordle_ai_utils.get_screen(wordle_ai_utils.WORDLE_GAME_BOX_1080P)
            board = wordle_ai_utils.read_img_to_board(game_img)
            guess = board.get_guesses()[guesses]
            score = guess.get_score()
            bot.read_report(guess)
            bot.narrow_words()
            sug_next_guess = bot.calc_next_guesses(score)
            possible_answers = bot.get_remaining_words()
            print('\n')
            print(board)
            print()
            print(f'Suggested Word: {sug_next_guess}')
            print(f'Possible answers:\n{possible_answers}')
            guesses = board.get_guesses_num()
            input('Press Enter after you\'ve made your next guess...')
        except AttributeError as attr_e:
            msg = f'{wordle_utils.RED}Error: {attr_e}\n' \
             + f'likely because board was not found, or not in focus.{wordle_utils.WHITE}'
            print(msg)
            time.sleep(3)
    time.sleep(1)


def main():
    '''
    Help solve wordle from web GUI
    Does not type/choose guesses automatically
    '''
    help_solve_gui()


if __name__ == '__main__':
    main()
