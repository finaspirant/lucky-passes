"""Reference solution for tennis_score. The spec is the docstring in stub.py."""

NAMES = ["0", "15", "30", "40"]


def game_text(a, b, tiebreak):
    if tiebreak:
        return f"tiebreak {a}-{b}"
    if a >= 3 and b >= 3:
        return "deuce" if a == b else "advantage A" if a > b else "advantage B"
    return f"{NAMES[a]}-{NAMES[b]}"


def tennis_score(points):
    if not isinstance(points, (list, tuple)):
        raise TypeError("points must be a list or tuple")
    sets_won = {"A": 0, "B": 0}
    finished = []
    games = {"A": 0, "B": 0}
    score = {"A": 0, "B": 0}
    for point in points:
        if not isinstance(point, str) or point not in ("A", "B"):
            raise ValueError(f"invalid point winner: {point!r}")
        if max(sets_won.values()) == 2:
            raise ValueError("point after the match was won")
        other = "B" if point == "A" else "A"
        tiebreak = len(finished) < 2 and games["A"] == games["B"] == 6
        score[point] += 1
        target = 7 if tiebreak else 4
        if score[point] < target or score[point] - score[other] < 2:
            continue
        games[point] += 1
        loser_points = score[other]
        score = {"A": 0, "B": 0}
        if not tiebreak and (games[point] < 6 or games[point] - games[other] < 2):
            continue
        text = f"{games['A']}-{games['B']}" + (f"({loser_points})" if tiebreak else "")
        finished.append(text)
        sets_won[point] += 1
        games = {"A": 0, "B": 0}

    parts = list(finished)
    if sets_won["A"] == 2:
        return "A won", " ".join(parts)
    if sets_won["B"] == 2:
        return "B won", " ".join(parts)
    tiebreak = len(finished) < 2 and games["A"] == games["B"] == 6
    parts.append(f"{games['A']}-{games['B']}")
    parts.append(game_text(score["A"], score["B"], tiebreak))
    return "in progress", " ".join(parts)
