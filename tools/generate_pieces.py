import os

LIGHT_SQUARE = "#E7DCC6"
DARK_SQUARE = "#6B4E8E"
WHITE_FILL = "#F7F0DE"
BLACK_FILL = "#D4AF37"
OUTLINE = "#2B1E3A"

SIZE = 16

PIECES = {
    "pawn": [
        "................",
        "................",
        ".......##.......",
        "......####......",
        "......####......",
        ".......##.......",
        "......####......",
        ".....######.....",
        ".....######.....",
        "......####......",
        ".....######.....",
        "....########....",
        "....########....",
        "...##########...",
        "...##########...",
        "................",
    ],
    "rook": [
        "................",
        "................",
        "...##..##..##...",
        "...##..##..##...",
        "...##########...",
        "....########....",
        "....########....",
        "....########....",
        "....########....",
        "....########....",
        "....########....",
        "....########....",
        "....########....",
        "...##########...",
        "...##########...",
        "................",
    ],
    "knight": [
        "................",
        "......####......",
        ".....######.....",
        ".....######.....",
        ".....###.##.....",
        "....##...##.....",
        "....##....##....",
        "...###....##....",
        "...###....###...",
        "...############.",
        "...###########..",
        "...##########...",
        "....########....",
        ".....######.....",
        ".....####.......",
        "................",
    ],
    "bishop": [
        "................",
        "................",
        ".......##.......",
        "......####......",
        "......####......",
        ".....######.....",
        ".....######.....",
        ".....######.....",
        "....########....",
        "....########....",
        "....##....##....",
        "....##....##....",
        "....########....",
        "...##########...",
        "...##########...",
        "................",
    ],
    "queen": [
        "................",
        "................",
        "..##....##......",
        "..##....##......",
        "..########......",
        "...######.......",
        "...######.......",
        "...######.......",
        "...######.......",
        "...######.......",
        "...######.......",
        "...########.....",
        "..##########....",
        "..##########....",
        "................",
        "................",
    ],
    "king": [
        "................",
        "................",
        "......##.##.....",
        "......##.##.....",
        "......####......",
        ".......##.......",
        "......####......",
        "......####......",
        "......####......",
        "......####......",
        "......####......",
        ".....######.....",
        "....########....",
        "...##########...",
        "...##########...",
        "................",
    ],
}


def filled_cells(grid):
    for y, row in enumerate(grid):
        assert len(row) == SIZE, "row {} has length {}".format(y, len(row))
    cells = set()
    for y, row in enumerate(grid):
        for x, ch in enumerate(row):
            if ch == "#":
                cells.add((x, y))
    return cells


def outline_cells(filled):
    outline = set()
    for (x, y) in filled:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if (nx, ny) not in filled and 0 <= nx < SIZE and 0 <= ny < SIZE:
                outline.add((nx, ny))
    return outline


def rect(x, y, color):
    return '<rect x="{}" y="{}" width="1" height="1" fill="{}"/>'.format(x, y, color)


def svg_wrap(body):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" '
            'shape-rendering="crispEdges">' + body + '</svg>')


def square_svg(color):
    return svg_wrap('<rect width="16" height="16" fill="{}"/>'.format(color))


def start_game_svg():
    w, h = 400, 80
    rx = 18
    parts = []
    parts.append('<rect x="3" y="3" width="{}" height="{}" rx="{}" fill="{}"/>'.format(w - 6, h - 6, rx, OUTLINE))
    parts.append('<rect x="7" y="7" width="{}" height="{}" rx="{}" fill="{}"/>'.format(w - 14, h - 14, rx - 4, DARK_SQUARE))
    parts.append('<rect x="7" y="7" width="{}" height="{}" rx="{}" fill="none" stroke="{}" stroke-width="3"/>'.format(w - 14, h - 14, rx - 4, BLACK_FILL))
    parts.append('<text x="{}" y="{}" text-anchor="middle" dominant-baseline="central" '
                 'font-family="monospace" font-size="30" font-weight="bold" fill="{}" '
                 'letter-spacing="3" shape-rendering="auto">&#9823; START NEW GAME</text>'.format(w // 2, h // 2, BLACK_FILL))
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {} {}" '
            'shape-rendering="crispEdges">'.format(w, h) + ''.join(parts) + '</svg>')


def piece_svg(grid, fill, square_color):
    filled = filled_cells(grid)
    outline = outline_cells(filled)
    body = '<rect width="16" height="16" fill="{}"/>'.format(square_color)
    for (x, y) in sorted(outline, key=lambda p: (p[1], p[0])):
        body += rect(x, y, OUTLINE)
    for (x, y) in sorted(filled, key=lambda p: (p[1], p[0])):
        body += rect(x, y, fill)
    return svg_wrap(body)


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print("wrote", path)


def main():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "img"))

    write(os.path.join(root, "light.svg"), square_svg(LIGHT_SQUARE))
    write(os.path.join(root, "dark.svg"), square_svg(DARK_SQUARE))
    write(os.path.join(root, "start-game.svg"), start_game_svg())

    for piece, grid in PIECES.items():
        for side, fill in (("white", WHITE_FILL), ("black", BLACK_FILL)):
            for sq, color in (("light", LIGHT_SQUARE), ("dark", DARK_SQUARE)):
                path = os.path.join(root, side, "{}-{}.svg".format(piece, sq))
                write(path, piece_svg(grid, fill, color))


if __name__ == "__main__":
    main()
