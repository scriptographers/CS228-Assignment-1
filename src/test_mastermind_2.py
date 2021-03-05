#!/usr/bin/env python

# == Author : Bruce Bolick == with mild clean-up done by Ganesh ==
# == extended by Oscar Marshall - u0747574

# Mastermind is NP-complete with n pegs per row and 2 colors.
#
# That is, a given a partially played game and the scoring so far,
# whether there exists a secret key such that the partially played game
# has this scoring  is the decision problem.
#
# Note that instead of the red scoring peg (right peg color, right place), often
# a black scoring peg is used, with the same meaning. Here, we stick with
# "red". In the scoring table, you will see  "r" and "w".
#
# From Wikipedia:
# ---
# Given a set of guesses and the number of red and white pegs
# scored for each guess, is there at least one secret pattern that
# generates those exact scores? (If not, the codemaker must have
# incorrectly scored at least one guess.)

# This alpha version of the game only considers red pegs.
# (where the right digit is in the right location.) It still wins most
# of the time.
#
# The aim of your project is twofold (see handout for details):
#
#
# Add constraint generation corresponding to whites.
#
# Generalize the game
#
# (1) for arbitrary sizes, as defined by these constants:
#     Npegs, Ncolors, MaxGuesses
#
# (2) incorporating both the red and white constraints
#
# (3) using the itertools package of Python. This package
#     provides the permutations and combinations functions.
#
# Extras that will fetch you extra-credits:
#
# - Allowing the user also to play, in addition to the computer playing itself
# - Ideally, any step must be playable by the user or the computer
# - If the person's play is NOT a smart move, the computer ought to explain why
#   this is so
#   (e.g. in direct opposition to the internal computer-generated constraints)
#
# ==

import random
from itertools import *
from z3 import *


# Game Parameters
NCOLS = 6
NPEGS = 4
NMOVES = 8


# Build and play the game
#
def play_once(colors, pegs, turns, secret, player, automated):
    """Builds a solver, and plays one round with the simple strategy:
    that of adding red-specific constraints.
    """

    # The matrix solution represents the computer's solution
    solution = [Int("s_%s" % (peg + 1)) for peg in range(pegs)]

    # Define solver and initial constraint
    # each cell contains a value in {1, ..., 6}
    solver = Solver()

    # == First, add default constraints for each position ==
    # == Only the allowed colors 1..6 may be placed ==
    # ==
    solver.add([And(1 <= solution[peg], solution[peg] <= colors)
                for peg in range(pegs)])
    #!!!!!solver.add(range_constraint)

    # list of guesses
    # prime first guess with 1,1,2,2
    board = [list(repeat(0, pegs)) for turn in range(turns)]

    scores = []

    win_turn = -1

    highest_color = 0

    highest_occurance = [0 for color in range(colors)]

    # == This is the main loop ==
    # It runs through turns 1 through 8
    # If a solution is not found, it exits
    # If found, the user may see the constraints as well
    # ==
    for turn in range(turns):
        # == red and white counts are accumulated in here
        # == after each turn
        red_pegs = 0
        white_pegs = 0

        if not automated:
            display_board(pegs, turns, secret, board, turn, scores,
                          player == False)
        if not automated and not player:
            raw_input()

        r = []
        if player:
            guess = ""
            while len(guess) == 0:
                print("Please type your guess (0 = solver decision):")
                guess = raw_input()
                if len(guess) != pegs:
                    guess = ""
                    continue
                r = []
                for peg in guess:
                    try:
                        peg_color = int(peg)
                        if peg_color < 0 or peg_color > colors:
                            guess = ""
                            continue
                        r.append(peg_color)
                    except:
                        guess = ""
                        continue
                solver.push()
                solver.add([solution[peg] == r[peg] for peg in range(pegs)
                            if r[peg] > 0])

        # Add a constraint so colors other than the highest color can only be
        # used twice.
        temporary_constraint = False
        solver.push()
        constraint = []
        if player:
            constrained_pegs = [peg for peg in range(pegs) if r[peg] == 0]
        else:
            constrained_pegs = range(pegs)
        if highest_color < colors and len(constrained_pegs) > 0:
            max_of_new = 1
            remaining = len(constrained_pegs)
            current_color = highest_color
            while remaining > 0:
                remaining -= max_of_new
                current_color += 1
                if (current_color == colors + 1):
                    constraint = []
                    max_of_new += 1
                    if max_of_new == pegs:
                        break
                    remaining = pegs - max_of_new
                    if remaining < 0:
                        remaining = 0
                    current_color = highest_color + 1
                sub_constraint = []
                for combination in list(combinations(constrained_pegs,
                                                     max_of_new)):
                    color_constraint = [solution[peg] != current_color
                                        for peg in constrained_pegs
                                        if peg not in combination]
                    if len(color_constraint) > 0:
                        sub_constraint.append(And(color_constraint))
                if len(sub_constraint) > 1:
                    constraint.append(Or(sub_constraint))
                if len(sub_constraint) == 1:
                    constraint.append(sub_constraint)
            # Make sure the solver doesn't guess any color higher than the
            # current color
            constraint.append(And([solution[peg] <= current_color
                                   for peg in constrained_pegs]))
            # Make sure that 4 exists => 3 exists if highest color is 2
            constraint.append(Or([Not(Or([solution[peg] == color
                                          for peg in constrained_pegs]))
                                  if color != highest_color + 1
                                  else Or([solution[peg] == color
                                           for peg in constrained_pegs])
                                  for color
                                  in range(current_color,
                                           highest_color, -1)]))
            # Make sure that a single color's occurances doesn't grow by more
            # than 1 from their highest occurance this game.
            if turn > 0:
                for color in range(colors):
                    occurances = 0
                    for peg in board[turn - 1]:
                        if peg == color + 1:
                            occurances += 1
                    if occurances > highest_occurance[color]:
                        highest_occurance[color] = occurances
                    if highest_occurance[color] == len(constrained_pegs) - 1 \
                            or highest_occurance[color] == 0:
                        continue
                    occurances = highest_occurance[color]
                    sub_constraint = [And([solution[peg] != color + 1
                                           for peg in constrained_pegs
                                           if peg not in combination])
                                      for combination
                                      in list(combinations(constrained_pegs,
                                                           occurances + 1))]
                    if len(sub_constraint) > 1:
                        constraint.append(Or(sub_constraint))
                    if len(sub_constraint) == 1:
                        constraint.append(sub_constraint)

            solver.add(constraint)

        # Use smt solver
        if solver.check() == sat:
            r = [int(solver.model().evaluate(solution[peg]).as_string())
                 for peg in range(pegs)]
        else:
            solver.pop()
            solver.pop()
            solver.push()
            solver.add(constraint)
            solver.push()
            solver.check()
            for peg in range(pegs):
                if r[peg] == 0:
                    r[peg] == int(solver.model().evaluate(solution[peg])
                                  .as_string())

        # Remove temporary constraint
        solver.pop()

        # Remove the player guess constraint if a player is playing
        if player:
            solver.pop()

        # == Put the guess on the board
        for peg in range(pegs):
            board[turn][peg] = r[peg]

        # Set new highest value
        for peg in board[turn]:
            if peg > highest_color:
                highest_color = peg

        # Deep copy of this turn and secret because we will be altering as we
        # check
        this_turn = board[turn][:]
        this_secret = secret[:]

        # Check for red match. 0 and -1 prevent duplicate reds/whites
        for peg in range(pegs):
            if(int(this_secret[peg]) == int(this_turn[peg])):
                red_pegs += 1
                this_turn[peg] = 0
                this_secret[peg] = -1

        # check for white match. 'x' and 'y' prevent dups
        for turn_peg in range(pegs):
            for secret_peg in range(pegs):
                if(this_turn[turn_peg] == this_secret[secret_peg]):
                    white_pegs += 1
                    this_turn[turn_peg] = 0
                    this_secret[secret_peg] = -1
                    break

        scores.append([red_pegs, white_pegs])

        if red_pegs == pegs:
            win_turn = turn
            if not automated:
                display_board(pegs, turns, secret, board, turn, scores, True)
            break

        # --- GENERATE CONSTRAINTS AND ADD TO SOLVER ---
        solver.add(generate_constraint(red_pegs, white_pegs, solution, board,
                                       turn, pegs))

        # === end of for turn in range(turns) ===

    # === exit point after break, or upon loss (completion of turn 8) ===
    if not automated:
        display_board(pegs, turns, secret, board, turn, scores, True)

        display_constraints(solver)

    return win_turn + 1


# Generates constraints for each game-board situation
def generate_constraint(red_pegs, white_pegs, solution, board, turn, pegs):
    result = []
    for red_combination in list(combinations(range(pegs), red_pegs)):
        result_red = [solution[peg] == board[turn][peg]
                      if peg in red_combination
                      else solution[peg] != board[turn][peg]
                      for peg in range(pegs)]
        sub_result = []
        for white_combination in list(
            combinations([peg for peg in range(pegs)
                          if peg not in red_combination], white_pegs)):
            for white_permutation in list(
                permutations([peg for peg in range(pegs)
                              if peg not in red_combination], white_pegs)):
                if reduce(lambda x, y: x or y,
                          map(lambda peg:
                              board[turn][white_combination[peg]]
                              == board[turn][white_permutation[peg]],
                              range(white_pegs)), False):
                    continue
                result_white = [solution[white_permutation[peg]]
                                == board[turn][white_combination[peg]]
                                for peg in range(white_pegs)]
                sub_sub_result = []
                for blank_combination in list(
                    combinations([peg for peg in range(pegs)
                                  if peg not in red_combination
                                  and peg not in white_combination],
                                 pegs - red_pegs - white_pegs)):
                    result_blank = []
                    for peg in blank_combination:
                        for sub_peg in range(pegs):
                            if sub_peg in red_combination and board[turn][sub_peg] == board[turn][peg] \
                                    or sub_peg in white_permutation and board[turn][white_combination[white_permutation.index(sub_peg)]] == board[turn][peg]:
                                continue
                            result_blank += [solution[sub_peg] != board[turn][peg]]
                    if len(result_blank) > 0:
                        sub_sub_result.append(And(result_blank))
                if len(sub_sub_result) > 1:
                    sub_result.append(And(result_white + [Or(sub_sub_result)]))
                else:
                    sub_result.append(And(result_white + sub_sub_result))
        if len(sub_result) == 0:
            continue
        if len(sub_result) > 1:
            result.append(And(result_red + [Or(sub_result)]))
        else:
            result.append(And(result_red + sub_result))
    return simplify(Or(result)) if len(result) > 1 else simplify(And(result))


def display_board(pegs, turns, secret, board, current_turn, scores, reveal):
    print
    if len(scores) == current_turn + 1 and scores[current_turn][0] == pegs:
        print("Congratulations, you won!")

    if reveal:
        print(reduce(lambda x, y: x + y,
                     [str(secret[peg]) for peg in range(pegs)]) +
              " is the secret.")

    for complement_turn in range(turns):
        turn = (turns - 1) - complement_turn
        turn_string = ""
        for peg in range(pegs):
            turn_string += str(board[turn][peg])
        if turn < current_turn \
                or turn == current_turn and len(scores) == current_turn + 1:
            turn_string += " : " + \
                           reduce(lambda x, y: x + y,
                                  list(chain(repeat("r", scores[turn][0]),
                                             repeat("w", scores[turn][1]))), "")
        print(turn_string)


def display_constraints(solver):
    print("Press <ENTER> to see constraints")
    raw_input()
    print(solver)

# --- main ---


def main(argv=None):
    automated = False
    player = False
    colors = NCOLS
    pegs = NPEGS
    turns = NMOVES

    if raw_input("Use default settings?: ") not in ["y", "Y"]:
        if raw_input("Would you like to play?: ") in ["y", "Y"]:
            player = True

        colors = 0
        while colors < 1:
            colors = raw_input("How many colors?: ")
            try:
                colors = int(colors)
            except:
                colors = 0

        pegs = 0
        while pegs < 1:
            pegs = raw_input("How many pegs?: ")
            try:
                pegs = int(pegs)
            except:
                pegs = 0

        turns = 0
        while turns < 1:
            turns = raw_input("How many turns?: ")
            try:
                turns = int(turns)
            except:
                turns = 0

        if player == False \
                and raw_input("Test all possible games against the solver?: ") \
                in ["y", "Y"]:
            automated = True

        if automated:
            win_turns = [0 for turn in range(turns)]
            lost = 0
            for secret in product([color for color in range(1, colors + 1)], repeat=pegs):
                print(list(secret))
                win_turn = play_once(colors, pegs, turns, list(secret), player,
                                     automated)
                if win_turn > 0:
                    win_turns[win_turn - 1] += 1
                    print("Win: " + str(win_turn))
                else:
                    lost += 1
                    print("Loss")
                print("Current Totals: " + str(win_turns))
            for win_turn in range(turns):
                print(str(win_turn + 1) + ": " + str(win_turns[win_turn]))
            print("Lost: " + str(lost))
            return
    while (True):
        # The list secret is the actual secret code.
        secret = [random.randint(1, NCOLS) for peg in range(NPEGS)]
        win_turn = play_once(colors, pegs, turns, secret, player, automated)
        if win_turn == 0:
            print("You lost.")
        else:
            print("You won in " + str(win_turn) + " turns.")
        if raw_input("Play again? [Y/N]: ") not in ["y", "Y"]:
            break


if __name__ == "__main__":
    sys.exit(main())

# == end of file ==
