def tennis_score(points):
    """Score a best-of-3-sets tennis match from the sequence of point winners.

    `points` is a list or tuple of point winners, in order. Each item must be exactly the
    str "A" or the str "B".

    Errors:
        TypeError if points is not a list or tuple (a str is not accepted).
        ValueError if an item is not exactly "A" or "B", or if any point comes after the
        match has been won. Items are checked in order as the points are played.

    Rules
        Game: a player wins a game on reaching at least 4 points with at least 2 more
        points than the opponent.
        Set: a player wins a set on reaching at least 6 games with at least 2 more games
        than the opponent. In sets 1 and 2, when the games reach 6-6 the next game is a
        tiebreak: its winner is the first player to reach at least 7 tiebreak points with
        at least 2 more than the opponent, and that player wins the set 7-6.
        Set 3 has no tiebreak: games continue until a player is 2 games ahead (for example
        8-6 or 12-10).
        Match: the first player to win 2 sets wins the match.

    Returns (state, score):
        state is "A won", "B won" or "in progress".
        score is a str of parts separated by single spaces. Every pair of numbers is
        written as A's number, "-", B's number.
          - One part per completed set: its games, e.g. "6-4". A set decided by a tiebreak
            also shows the set loser's tiebreak points in parentheses: "7-6(5)" means A
            won the tiebreak 7-5; "6-7(10)" means B won it 12-10.
          - If the match is in progress, two more parts follow: the current set's games
            (e.g. "0-0" at the start of a set, "6-6" before a tiebreak), then the current
            game's points:
              - In a normal game, each player's points are named 0, 15, 30, 40 for 0, 1, 2,
                3 points, e.g. "0-0", "30-15" or "40-0". When both players have at least 3
                points, the game is instead "deuce" if they are level, or "advantage A" /
                "advantage B" for the player one point ahead.
              - In a tiebreak (from the moment the set reaches 6-6), the game is
                "tiebreak " followed by the plain point counts, e.g. "tiebreak 0-0" or
                "tiebreak 5-3".
        Examples: [] gives ("in progress", "0-0 0-0"); A winning the first set 6-4 and
        then the first point of set 2 gives ("in progress", "6-4 0-0 15-0"); a finished
        match lists only its sets, e.g. ("A won", "6-4 7-6(3)").
    """
    raise NotImplementedError
