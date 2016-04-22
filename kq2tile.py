"""
Tile
"""
import math
import random

UP = (-1, 0)
DOWN = (1, 0)
LEFT = (0, -1)
RIGHT = (0, 1)


def add(tup1, tup2):
    """
    Return the sum of two tuples.
    """
    return (tup1[0] + tup2[0],
            tup1[1] + tup2[1])


def sub(tup1, tup2):
    """
    Return the difference of two tuples.
    """
    return (tup1[0] - tup2[0],
            tup1[1] - tup2[1])


def mul(tup, num):
    """
    Return the product of a tuple and a number.
    """
    return (tup[0] * num,
            tup[1] * num)


def div(tup, num):
    """
    Return the quotient of a tuple and a number.
    """
    return (tup[0] / num,
            tup[1] / num)


def corner2center(corner, size):
    """
    Return center position from upper left corner.
    """
    return add(corner, div(size, 2))


def center2corner(center, size):
    """
    Return upper left corner position from center.
    """
    return sub(center, div(size, 2))


def corner_rect(corner, size):
    """
    Return a rectangle from upper left corner.
    """
    return ((corner[0], corner[1]),
            (corner[0] + size[0], corner[1]),
            (corner[0] + size[0], corner[1] + size[1]),
            (corner[0], corner[1] + size[1]))


def center_rect(center, size):
    """
    Return a rectangle from center.
    """
    corner = center2corner(center, size)
    return corner_rect(corner, size)


def text_pos(text_center, text_size):
    """
    Return the lower left corner of text.
    """
    return (text_center[0] - text_size[0] / 2,
            text_center[1] + text_size[1] / 2)


def cell_corner(row, col, cell_size):
    """
    Return the upper left corner of a tile.
    """
    return (col * cell_size[0],
            row * cell_size[1])


def cell_center(row, col, cell_size):
    """
    Return the center of a tile.
    """
    corner = cell_corner(row, col, cell_size)
    return corner2center(corner, cell_size)


def cell_4_neighbor(cell):
    """
    Return a cell's four neighbors.
    """
    return [add(cell, offset) for offset in
            (UP, DOWN, LEFT, RIGHT)]


def pos2cell(pos, cell_size, cell_offset=(0, 0)):
    """
    Return a cell from given position.
    """
    pos = (pos[0] + cell_offset[0] * cell_size[0],
           pos[1] + cell_offset[1] * cell_size[1])
    return (pos[1] // cell_size[1],
            pos[0] // cell_size[0])


def rotate(point, center, angle):
    """
    Return a rotated point.
    """
    angle = math.radians(angle)
    vec = sub(point, center)
    vec = (vec[0] * math.cos(angle) - vec[1] * math.sin(angle),
           vec[0] * math.sin(angle) + vec[1] * math.cos(angle))
    return add(center, vec)


def rotate_cell(cell, center, clockwise=True):
    """
    Return a rotated cell.
    """
    if clockwise:
        row, col = rotate(cell, center, -90)
    else:
        row, col = rotate(cell, center, 90)
    return int(round(row)), int(round(col))


def rotate_cells(cells, center, clockwise=True):
    """
    Return rotated cells.
    """
    return [rotate_cell(cell, center, clockwise)
            for cell in cells]


def random_rotate(cells, center):
    """
    Return randomly rotated cells.
    """
    num_rotate = random.randrange(4)
    for _ in range(num_rotate):
        cells = rotate_cells(cells, center)
    return cells


def random_color():
    """
    Return a random color pair.
    """
    mix_color = (255, 255, 255)
    r = (random.randrange(256) + mix_color[0]) / 2
    g = (random.randrange(256) + mix_color[1]) / 2
    b = (random.randrange(256) + mix_color[2]) / 2
    return ('rgba(%d, %d, %d, %f)' % (r, g, b, 1),
            'rgba(%d, %d, %d, %f)' % (r, g, b, .94))


def cell_cell_seam(cell1, cell2, cell_size):
    """
    Return the seam line between two cells.
    """
    row1, col1 = cell1
    row2, col2 = cell2
    if row1 == row2 and abs(col1 - col2) == 1:
        pos_x = max(col1, col2) * cell_size[0]
        return ((pos_x, (row1 + 0.97) * cell_size[1]),
                (pos_x, (row1 + 0.03) * cell_size[1]))
    if col1 == col2 and abs(row1 - row2) == 1:
        pos_y = max(row1, row2) * cell_size[1]
        return (((col1 + 0.97) * cell_size[0], pos_y),
                ((col1 + 0.03) * cell_size[0], pos_y))


def cell_cells_seams(cell, cells, size):
    """
    Return the seam lines between one cell and other cells.
    """
    cells = set(cells)
    return [cell_cell_seam(cell, neighbor, size)
            for neighbor in cell_4_neighbor(cell)
            if neighbor in cells]


def cells_seams(cells, cell_size):
    """
    Return all seam lines between any two cells.
    """
    # base case
    if len(cells) < 2:
        return []

    # recursion
    cell = cells[0]
    cells = cells[1:]
    return (cell_cells_seams(cell, cells, cell_size)
            + cells_seams(cells, cell_size))


def connected_cells(cells):
    """
    Return all connected cells.
    """
    ans = []
    copy = set(cells)

    # BFS
    while copy:
        start = copy.pop()
        connected = set([start])
        stack = [start]
        while stack:
            cell = stack.pop(0)
            for neighbor in cell_4_neighbor(cell):
                if neighbor in copy:
                    connected.add(neighbor)
                    stack.append(neighbor)
                    copy.remove(neighbor)
        ans.append(connected)

    return ans


def connected_tiles(tiles):
    """
    Return all connected tiles.
    """
    tile_map = dict((tile.get_cell(), tile) for tile in tiles)
    return [[tile_map[cell] for cell in cells]
            for cells in connected_cells(tile_map.keys())]


class Rect:
    """
    Rectangle with color.
    """
    def __init__(self, pos, size, color):
        """
        Initialize a rectangle with color.
        """
        self.pos = pos  # upper left corner
        self.size = size
        self.color = color

        self.border_width = 2
        self.border_color = 'Black'
        self.rect = corner_rect(pos, size)
        self.center = corner2center(pos, size)
        self.animation = None

    def get_pos(self):
        """
        Return the upper left corner (position).
        """
        return tuple(self.pos)

    def set_pos(self, pos):
        """
        Change the upper left corner (position).
        """
        self.pos = pos
        self.rect = corner_rect(pos, self.size)
        self.center = corner2center(pos, self.size)

    def get_size(self):
        """
        Return size.
        """
        return tuple(self.size)

    def set_size(self, size):
        """
        Change size.
        """
        self.size = size
        self.rect = corner_rect(self.pos, size)

    def get_color(self):
        """
        Return color.
        """
        return self.color

    def set_color(self, color):
        """
        Change color.
        """
        self.color = color

    def set_border_width(self, width):
        """
        Change border width.
        """
        self.border_width = width

    def set_border_color(self, color):
        """
        Change border color.
        """
        self.border_color = color

    def get_rect(self):
        """
        Return rectangle.
        """
        return tuple(self.rect)

    def set_rect(self, rect):
        """
        Change rectangle.
        """
        self.rect = rect

    def get_animation(self):
        """
        Return update strategy.
        """
        return self.animation

    def set_animation(self, animation):
        """
        Change update strategy.
        """
        self.animation = animation

    def get_center(self):
        """
        Return center.
        """
        return tuple(self.center)

    def has_pos(self, pos):
        """
        Return true if given position is inside rectangle.
        """
        diff = sub(pos, self.pos)
        return (0 <= diff[0] < self.size[0]
                and 0 <= diff[1] < self.size[1])

    def move(self, vel):
        """
        Change position by velocity.
        """
        pos = add(self.pos, vel)
        self.set_pos(pos)

    def update(self):
        """
        Update by self's animation.
        """
        if self.animation:
            self.animation.update(self)

    def draw(self, canvas):
        """
        Draw rectangle on canvas.
        """
        self.update()
        canvas.draw_polygon(self.rect,
                            self.border_width,
                            self.border_color,
                            self.color)


class TextRect(Rect):
    """
    Rectangle with text in center.
    """
    def __init__(self, pos, size, color,
                 text, font_size, font_face, font_color):
        """
        Initialize a rectangle with text.
        """
        Rect.__init__(self, pos, size, color)
        self.text = text
        self.font_size = font_size
        self.font_face = font_face
        self.font_color = font_color

    def __str__(self):
        """
        Return text.
        """
        return self.text

    def set_text(self, text):
        """
        Change text.
        """
        self.text = text

    def draw_text(self, canvas, gui):
        """
        Draw text in the center.
        """
        if gui:
            text_size = gui.get_text_size(self.text,
                                          self.font_size,
                                          self.font_face)
            pos = text_pos(self.get_center(), text_size)
        else:
            pos = self.get_rect()[-1]
        canvas.draw_text(self.text, pos,
                         self.font_size,
                         self.font_color,
                         self.font_face)

    def draw(self, canvas, gui=None):
        """
        Override to draw both rectangle and text.
        """
        Rect.draw(self, canvas)
        self.draw_text(canvas, gui)


class Tile(Rect):
    """
    Tile in grid.
    """
    def __init__(self, row, col, cell_size, tile_size, color):
        """
        Initialize a tile at the center of a cell.
        """
        self.row = row
        self.col = col

        center = cell_center(row, col, cell_size)
        corner = center2corner(center, tile_size)
        Rect.__init__(self, corner, tile_size, color)

    def get_row(self):
        """
        Return row in grid.
        """
        return self.row

    def get_col(self):
        """
        Return column in grid.
        """
        return self.col

    def get_cell(self):
        """
        Return cell in grid.
        """
        return self.row, self.col

    def set_cell(self, row, col, cell_size=None):
        """
        Change cell in grid and try update position.
        """
        if cell_size:
            vel = ((col - self.col) * cell_size[0],
                   (row - self.row) * cell_size[1])
            self.move(vel)
        self.row = row
        self.col = col
