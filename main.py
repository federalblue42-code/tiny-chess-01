import json
import os
import sys
import urllib.error
import urllib.request

ENV_URL = os.environ.get("MAKEFUN_ENV_URL") or sys.exit("MAKEFUN_ENV_URL is not set")
VALUE = {"p": 1, "n": 3, "b": 3, "r": 5, "q": 9, "k": 1000}

def post(path, body):
    req = urllib.request.Request(
        ENV_URL + path,
        data=json.dumps(body).encode(),
        headers={"content-type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req) as res:
            return json.load(res)
    except urllib.error.HTTPError as e:
        sys.exit(f"{path}: HTTP {e.code}")

def board_of(fen):
    board = {}
    for i, row in enumerate(fen.split()[0].split("/")):
        file = 0
        for c in row:
            if c.isdigit():
                file += int(c)
            else:
                board["abcdefgh"[file] + str(8 - i)] = c
                file += 1
    return board

def choose(fen, legal):
    board = board_of(fen)
    def rank(move):
        mover = board.get(move[:2], "p").lower()
        victim = board.get(move[2:4])
        taken = VALUE.get(victim.lower(), 0) if victim else 0
        promo = VALUE.get(move[4].lower(), 0) if len(move) == 5 else 0
        # center control bonus
        dest = move[2:4]
        center_bonus = 1 if dest in ["d4", "d5", "e4", "e5"] else 0
        return (-taken * 10 - promo * 5 - center_bonus, move)
    return min(legal, key=rank)

while True:
    g = post("/game", {})
    if g["status"] == "done":
        break
    while g["status"] == "your_move":
        g = post("/move", {"game": g["game"], "move": choose(g["fen"], g["legal_moves"])})
    print(f"game {g.get('game')}: {g.get('outcome')} by {g.get('reason')}", file=sys.stderr)
