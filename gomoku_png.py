import os, sys
from PIL import Image, ImageDraw
from ast import literal_eval

crop = None
flip = False

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

def get_path(filename):
    return os.path.join(__location__, filename)

def go(n, moves, filename, crop):
    width = 29
    left_border = 30
    top_border = 10
    right_border = 0
    bottom_border = 0
    letters = 'ABCDEFGHIJKLMNOPQRS'
    background_colour = (10, 180, 10)

    image = Image.new('RGB', (left_border + n * width + right_border, top_border + n * width + bottom_border), background_colour)
    draw = ImageDraw.Draw(image)

    stone_radius = 13
    stone_size = (stone_radius * 2, stone_radius * 2)
    white_stone = Image.open(get_path("white_stone.png"))
    white_stone = white_stone.resize(stone_size, Image.ANTIALIAS)
    black_stone = Image.open(get_path("black_stone.png"))
    black_stone = black_stone.resize(stone_size, Image.ANTIALIAS)

    def xcoord(x):
        return left_border + width * x

    def ycoord(y):
        return top_border + width * y

    def coords(x1, y1, x2, y2):
        return (xcoord(x1), ycoord(y1), xcoord(x2), ycoord(y2))

    # Draw lines and add coordinates.
    for i in range(n):
        m = width * i
        draw.line(coords(0, i, n-1, i), fill=128)
        draw.line(coords(i, 0, i, n-1), fill=128)

        t = letters[i]
        w, h = draw.textsize(t)
        draw.text((xcoord(i) - w/2 + 1, ycoord(n - 1) + h/2), t, "black")

        t = str(n - i)
        w, h = draw.textsize(t)
        draw.text((xcoord(0) - w - 3, ycoord(i) - h/2), t, "black")

    if n == 19:
        # Draw small circles at key positions to make it easier to count coordinates.
        r = 2
        for x in [3, 9, 15]:
            for y in [3, 9, 15]:
                draw.ellipse((xcoord(x) - r, ycoord(y) - r, xcoord(x) + r, ycoord(y) + r), fill="black")

    turn = 0
    colors = [(0, 50, 50), (190, 190, 190)]
    last_turn = len(moves.split())

    def text(x, y, t, fill=None):
        w, h = draw.textsize(t)
        draw.text((xcoord(x) - w/2, ycoord(y) - h/2), t, fill)

    # Draw the pieces.
    for move in moves.split():
	shape = None
        if '*' in move:
            move, shape = move.split('*') 
        x = letters.index(move[0].upper())
        y = n - int(move[1:])
        if flip:
            y = n - y - 1
        r = stone_radius
        xy = (xcoord(x) - r, ycoord(y) - r, xcoord(x) + r, ycoord(y) + r)
        if shape:
            color = 'green' if shape == 'g' else 'red'
            draw.ellipse(xy, outline = color)
        else:
	    stone = black_stone if turn % 2 == 0 else white_stone
            image.paste(stone, xy, stone)
            turn += 1
            text_color = "white" if turn % 2 == 1 else "black"
            move_color = text_color if turn < last_turn else "#ff6666"
            text(x, y, str(turn), fill=move_color)

    if crop:
        c = coords(*crop)
        c = (c[0] - width/2, c[1] - width/2, c[2] + width/2, c[3] + width/2)  
        image = image.crop(c)

    # Save the image to a file.
    image.save(filename, "PNG")

if __name__ == '__main__':
    if len(sys.argv) == 1:
        n = 19
        moves = "j10 k11 k13 j9"
        filename = "image.png"
        crop = (5, 5, 13, 13)
    else:
        n = int(sys.argv[1])
        moves = sys.argv[2]
        filename = sys.argv[3]
        if len(sys.argv) > 4:
            crop = literal_eval(sys.argv[4])

    go(n, moves, filename, crop)
