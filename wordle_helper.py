'''
Help a user solve a wordle from web GUI without doing it for them.
'''
import wordle
import wordle_ai_utils
import wordle_ai
import time

def help_solve_gui():
    '''
    Helps a user solve a wordle from web GUI without doing it for them.
    '''
    bot = wordle_ai.WordleAI(None)
    score = 0
    time.sleep(1)
    guesses = 0
    possible_answers = [[], []]
    print(f'Recommended first guess: {bot.get_starting_word()}')
    input('Press Enter after you\'ve made your first guess...')
    while score < 100 and guesses < wordle.MAX_GUESSES and len(possible_answers) > 1:
        try:
            # wait for player to make guess
            # update internal board from image
            game_img = wordle_ai_utils.get_screen(wordle_ai_utils.WORDLE_GAME_BOX_1080P)
            board = wordle_ai_utils.read_img_to_board(game_img)
            guess = board.get_guesses()[guesses]
            score = guess.get_score()
            bot.read_report(guess)
            bot.narrow_words()
            sug_next_guess = bot.get_sug_next_guesses()
            possible_answers = bot.get_remaining_words()
            print('\n')
            print(board)
            print()
            print(f'Suggested Word: {sug_next_guess}')
            print(f'Possible answers:\n{possible_answers}')
            guesses = board.get_guesses_num()
            input('Press Enter after you\'ve made your next guess...')
        except AttributeError as e:
            print(f'{wordle.RED}Error: {e}\nlikely because board was not found, or not in focus.{wordle.WHITE}')
            time.sleep(3)
    time.sleep(1)


def main():
    help_solve_gui()


if __name__ == '__main__':
    main()