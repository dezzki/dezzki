from collections import defaultdict
from urllib.parse import urlencode
import os
import re

import chess
import yaml

with open('data/settings.yaml', 'r') as settings_file:
    settings = yaml.load(settings_file, Loader=yaml.FullLoader)


def create_link(text, link):
    return f"[{text}]({link})"

def create_issue_link(source, dest_list):
    issue_link = settings['issues']['link'].format(
        repo=os.environ["GITHUB_REPOSITORY"],
        params=urlencode(settings['issues']['move'], safe="{}"))

    ret = [create_link(dest, issue_link.format(source=source, dest=dest)) for dest in sorted(dest_list)]
    return ", ".join(ret)

def new_game_issue_link():
    return settings['issues']['link'].format(
        repo=os.environ["GITHUB_REPOSITORY"],
        params=urlencode(settings['issues']['new_game']))

def start_game_button():
    return '\n**[♟ Start New Game](' + new_game_issue_link() + ')**\n'

def generate_winners():
    with open("data/winners.txt", 'r') as file:
        lines = [line.rstrip() for line in file.readlines() if line.strip()]

    if not lines:
        return '\n_No games finished yet._\n'

    markdown = "\n| Result | Players |\n"
    markdown += "| :----: | :------ |\n"

    for line in lines:
        outcome, sep, players = line.partition('|')
        links = ', '.join(
            create_link(p.strip(), "https://github.com/" + p.strip().lstrip('@'))
            for p in players.split(',') if p.strip()
        )
        markdown += "| {} | {} |\n".format(outcome, links)

    return markdown + "\n"

def generate_last_moves():
    markdown = "\n"
    markdown += "| Move | Author |\n"
    markdown += "| :--: | :----- |\n"

    counter = 0

    with open("data/last_moves.txt", 'r') as file:
        for line in file.readlines():
            parts = line.rstrip().split(':')

            if not ":" in line:
                continue

            if counter >= settings['misc']['max_last_moves']:
                break

            counter += 1

            match_obj = re.search('([A-H][1-8])([A-H][1-8])', line, re.I)
            if match_obj is not None:
                source = match_obj.group(1).upper()
                dest   = match_obj.group(2).upper()

                markdown += "| `" + source + "` to `" + dest + "` | " + create_link(parts[1], "https://github.com/" + parts[1].lstrip()[1:]) + " |\n"
            else:
                markdown += "| `" + parts[0] + "` | " + create_link(parts[1], "https://github.com/" + parts[1].lstrip()[1:]) + " |\n"

    return markdown + "\n"

def generate_moves_list(board):
    # Create dictionary and fill it
    moves_dict = defaultdict(set)

    for move in board.legal_moves:
        source = chess.SQUARE_NAMES[move.from_square].upper()
        dest   = chess.SQUARE_NAMES[move.to_square].upper()

        moves_dict[source].add(dest)

    # Write everything in Markdown format
    markdown = ""

    if board.is_game_over():
        issue_link = settings['issues']['link'].format(
            repo=os.environ["GITHUB_REPOSITORY"],
            params=urlencode(settings['issues']['new_game']))

        return "**GAME IS OVER!** " + create_link("Click here", issue_link) + " to start a new game :D\n"

    if board.is_check():
        markdown += "**CHECK!** Choose your move wisely!\n"

    markdown += "|  FROM  | TO (Just click a link!) |\n"
    markdown += "| :----: | :---------------------- |\n"

    for source,dest in sorted(moves_dict.items()):
        markdown += "| **" + source + "** | " + create_issue_link(source, dest) + " |\n"

    return markdown

def board_to_markdown(board):
    board_list = [[item for item in line.split(' ')] for line in str(board).split('\n')]
    markdown = ""

    piece_names = {
        "r": "rook", "n": "knight", "b": "bishop", "q": "queen", "k": "king", "p": "pawn",
        "R": "rook", "N": "knight", "B": "bishop", "Q": "queen", "K": "king", "P": "pawn",
    }
    piece_color = {
        "r": "black", "n": "black", "b": "black", "q": "black", "k": "black", "p": "black",
        "R": "gold", "N": "gold", "B": "gold", "Q": "gold", "K": "gold", "P": "gold",
    }

    black_turn = board.turn == chess.BLACK

    # Write header in Markdown format
    if black_turn:
        markdown += "|   | H | G | F | E | D | C | B | A |   |\n"
    else:
        markdown += "|   | A | B | C | D | E | F | G | H |   |\n"
    markdown += "|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|\n"

    # Get Rows
    rows = range(1, 9)
    if black_turn:
        rows = reversed(rows)

    # Write board
    for row in rows:
        markdown += "| **" + str(9 - row) + "** | "
        columns = board_list[row - 1]
        if black_turn:
            columns = reversed(columns)

        for col_idx, elem in enumerate(columns):
            file_idx = (7 - col_idx) if black_turn else col_idx
            rank_idx = 8 - row
            square = "dark" if (file_idx + rank_idx) % 2 == 0 else "light"

            if elem == ".":
                src = "img/{}.svg".format(square)
            else:
                src = "img/{}/{}-{}.svg".format(piece_color.get(elem, "black"), piece_names.get(elem, "pawn"), square)

            markdown += '<img src="{}" width=48px> | '.format(src)

        markdown += "**" + str(9 - row) + "** |\n"

    # Write footer in Markdown format
    if black_turn:
        markdown += "|   | **H** | **G** | **F** | **E** | **D** | **C** | **B** | **A** |   |\n"
    else:
        markdown += "|   | **A** | **B** | **C** | **D** | **E** | **F** | **G** | **H** |   |\n"

    return markdown
