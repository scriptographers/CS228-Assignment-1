from z3 import And, Or, Not, PbGe, PbEq, Bool, Solver, sat, is_true
import itertools

k = 0
n = 0
vs = []
move = []
s = Solver()
guess_list = []
response_list = []


def sum_to_one(ls):
    A = Or(ls)
    atmost_one_list = []
    for pair in itertools.combinations(ls, 2):
        atmost_one_list.append(Or(Not(pair[0]), Not(pair[1])))
    return And(A, And(atmost_one_list))


def initialize(n_, k_):
    global k, n, vs, move, s, guess_list, response_list
    k = k_
    n = n_
    vs = [[Bool("e_{}_{}".format(i, j)) for j in range(n)] for i in range(k)]
    base_cons = []
    for i in range(k):
        base_cons.append(sum_to_one(vs[i]))
    s.add(And(base_cons))


def put_first_player_response(red, white):
    add_a_guess_solution(move, red, white)


def get_second_player_move():
    global k, n, vs, move, s, guess_list, response_list
    if len(guess_list) == 0:
        # start with random guess
        move = [0] * k
    else:
        move = get_a_solution()

    guess_list.append(move)
    return move


def get_a_solution():
    global k, n, vs, move, s, guess_list, response_list
    sol = [0] * k
    if s.check() == sat:
        m = s.model()
        # print("model: ", m)
        for i in range(k):
            for j in range(n):
                val = m[vs[i][j]]
                if is_true(val):
                    sol[i] = j

        print("yopj", sol)
        move = sol
        return sol
    else:
        print("some thing bad happened! no more moves!\n")
        raise Exception('Failed!')


def add_a_guess_solution(guess, reds, whites):
    global k, n, vs, move, s, guess_list, response_list

    cons = PbEq([(vs[i][guess[i]], 1) for i in range(k)], reds)

    guess_cons = white_cond(guess, whites)

    s.add(And(guess_cons, cons))


def white_cond(ls, whites):
    global k, n, vs, move, s, guess_list, response_list
    l = []
    for i in range(len(ls)):
        B = False
        for j in range(k):
            B = Or(B, vs[j][ls[i]])
        l.append(B)

    cond = PbGe([(l[i], 1) for i in range(len(l))], whites)
    return cond
