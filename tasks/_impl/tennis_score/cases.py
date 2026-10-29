from tasks.gen.render import Raises

FUNCTION = "tennis_score"
# G("AAB") is the points of three games won by A, A and B, each to love.
EXTRA_PRELUDE = '''

def G(winners):
    return [w for w in winners for _ in range(4)]

TO_6_6 = G("AAAAABBBBBAB")
'''

VISIBLE = [
    ("start", "tennis_score([])", ("in progress", "0-0 0-0")),
    ("points", 'tennis_score(["A", "A", "B"])', ("in progress", "0-0 30-15")),
    ("deuce", 'tennis_score(["A", "B"] * 3)', ("in progress", "0-0 deuce")),
    ("first_game", 'tennis_score(["B"] * 4 + ["A"])', ("in progress", "0-1 15-0")),
    ("straight_sets", 'tennis_score(["A"] * 48)', ("A won", "6-0 6-0")),
]

HIDDEN_EDGE_VAL = [
    ("tuple_input", 'tennis_score(("A", "A"))', ("in progress", "0-0 30-0")),
    ("point_after_match", 'tennis_score(["A"] * 49)', Raises("ValueError")),
    ("bad_item_after_match", 'tennis_score(["A"] * 48 + ["C"])', Raises("ValueError")),
    ("invalid_winner", 'tennis_score(["A", "C"])', Raises("ValueError")),
    ("lowercase_winner", 'tennis_score(["a"])', Raises("ValueError")),
    ("int_winner", "tennis_score([1])", Raises("ValueError")),
    ("str_input", 'tennis_score("AAB")', Raises("TypeError")),
    ("none_input", "tennis_score(None)", Raises("TypeError")),
]

HIDDEN_EDGE_LOGIC = [
    ("love_fifteen", 'tennis_score(["B"])', ("in progress", "0-0 0-15")),
    ("forty_love", 'tennis_score(list("AAA"))', ("in progress", "0-0 40-0")),
    ("forty_thirty", 'tennis_score(list("AABBA"))', ("in progress", "0-0 40-30")),
    ("advantage_a", 'tennis_score(list("ABABABA"))', ("in progress", "0-0 advantage A")),
    ("advantage_b", 'tennis_score(list("ABABABB"))', ("in progress", "0-0 advantage B")),
    ("back_to_deuce", 'tennis_score(list("ABABABAB"))', ("in progress", "0-0 deuce")),
    ("game_after_advantage", 'tennis_score(list("ABABABAA"))', ("in progress", "1-0 0-0")),
    ("set_6_4", 'tennis_score(G("AAAAABBBBA"))', ("in progress", "6-4 0-0 0-0")),
    ("set_at_6_5", 'tennis_score(G("AAAAABBBBBA"))', ("in progress", "6-5 0-0")),
    ("set_7_5", 'tennis_score(G("AAAAABBBBBAA"))', ("in progress", "7-5 0-0 0-0")),
    ("tiebreak_start", "tennis_score(TO_6_6)", ("in progress", "6-6 tiebreak 0-0")),
    ("tiebreak_points", 'tennis_score(TO_6_6 + list("AAB"))', ("in progress", "6-6 tiebreak 2-1")),
    ("tiebreak_needs_two", 'tennis_score(TO_6_6 + list("AB" * 6) + ["A"])', ("in progress", "6-6 tiebreak 7-6")),
    ("tiebreak_to_love", 'tennis_score(TO_6_6 + ["A"] * 7)', ("in progress", "7-6(0) 0-0 0-0")),
    ("tiebreak_b_extended", 'tennis_score(TO_6_6 + list("AB" * 6) + ["B", "B"])', ("in progress", "6-7(6) 0-0 0-0")),
    ("tiebreak_long", 'tennis_score(TO_6_6 + list("AB" * 10) + ["A", "A"])', ("in progress", "7-6(10) 0-0 0-0")),
    ("tiebreak_second_set", 'tennis_score(G("A" * 6) + TO_6_6 + ["B"] * 7)', ("in progress", "6-0 6-7(0) 0-0 0-0")),
    ("second_set_point", 'tennis_score(G("A" * 6) + ["A"])', ("in progress", "6-0 0-0 15-0")),
    ("third_set_no_tiebreak", 'tennis_score(G("A" * 6 + "B" * 6) + TO_6_6)', ("in progress", "6-0 0-6 6-6 0-0")),
    ("third_set_deuce_at_6_6", 'tennis_score(G("A" * 6 + "B" * 6) + TO_6_6 + list("ABABAB"))',
     ("in progress", "6-0 0-6 6-6 deuce")),
    ("third_set_7_6", 'tennis_score(G("A" * 6 + "B" * 6) + TO_6_6 + G("A"))', ("in progress", "6-0 0-6 7-6 0-0")),
    ("third_set_8_6", 'tennis_score(G("A" * 6 + "B" * 6) + TO_6_6 + G("AA"))', ("A won", "6-0 0-6 8-6")),
    ("third_set_long", 'tennis_score(G("B" * 6 + "A" * 6) + TO_6_6 + G("AB" * 4 + "BB"))', ("B won", "0-6 6-0 10-12")),
    ("b_straight_sets", 'tennis_score(["B"] * 48)', ("B won", "0-6 0-6")),
    ("tiebreak_sets_win", 'tennis_score(TO_6_6 + ["A"] * 7 + TO_6_6 + list("BA" * 5) + ["A", "A"])',
     ("A won", "7-6(0) 7-6(5)")),
]

LARGE = []
LARGE_TIME_LIMIT = None


def random_exprs(rng, reference):
    exprs = []
    for _ in range(25):
        p_a = rng.choice([0.35, 0.5, 0.65])
        target = rng.randint(0, 300)
        winners = []
        while len(winners) < target and reference(winners)[0] == "in progress":
            winners.append("A" if rng.random() < p_a else "B")
        if reference(winners)[0] != "in progress" and rng.random() < 0.15:
            winners.append(rng.choice("AB"))
        exprs.append(f"tennis_score(list({''.join(winners)!r}))")
    return exprs
