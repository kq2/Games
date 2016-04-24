"""
Game Pentos
"""
import random
import kq2tile
import kq2grid
import kq2gui

# Polyomino's tile-coordinates and rotation center
PENTOMINO = {
    'F': (((1, 0), (2, 0), (0, 1), (1, 1), (1, 2)), (1, 1)),
    'f': (((0, 0), (1, 0), (1, 1), (2, 1), (1, 2)), (1, 1)),
    'I': (((0, 0), (1, 0), (2, 0), (3, 0), (4, 0)), (2, 0)),
    'J': (((1, 0), (1, 1), (1, 2), (1, 3), (2, 3)), (1, 2)),
    'j': (((1, 0), (1, 1), (1, 2), (1, 3), (0, 3)), (1, 2)),
    'P': (((0, 0), (1, 0), (0, 1), (1, 1), (0, 2)), (0, 1)),
    'p': (((0, 0), (1, 0), (0, 1), (1, 1), (1, 2)), (1, 1)),
    'S': (((2, 0), (3, 0), (0, 1), (1, 1), (2, 1)), (2, 1)),
    's': (((0, 0), (1, 0), (1, 1), (2, 1), (3, 1)), (1, 1)),
    'T': (((0, 0), (1, 0), (2, 0), (1, 1), (1, 2)), (1, 1)),
    'U': (((0, 0), (2, 0), (0, 1), (1, 1), (2, 1)), (1, 1)),
    'V': (((0, 0), (1, 0), (2, 0), (2, 1), (2, 2)), (1, 1)),
    'W': (((0, 0), (0, 1), (1, 1), (1, 2), (2, 2)), (1, 1)),
    'X': (((1, 0), (0, 1), (1, 1), (2, 1), (1, 2)), (1, 1)),
    'Y': (((0, 0), (0, 1), (0, 2), (0, 3), (1, 2)), (0, 2)),
    'y': (((0, 0), (0, 1), (0, 2), (0, 3), (1, 1)), (0, 1)),
    'Z': (((0, 0), (1, 0), (1, 1), (1, 2), (2, 2)), (1, 1)),
    'z': (((0, 2), (1, 2), (1, 1), (1, 0), (2, 0)), (1, 1))
}
TETROMINO = {
    'I': (((0, 0), (1, 0), (2, 0), (3, 0)), (1, 0)),
    'J': (((0, 0), (1, 0), (2, 0), (2, 1)), (1, 0)),
    'j': (((0, 0), (1, 0), (2, 0), (0, 1)), (1, 0)),
    'O': (((0, 0), (1, 0), (0, 1), (1, 1)), (1, 0)),
    'S': (((1, 0), (2, 0), (0, 1), (1, 1)), (1, 0)),
    's': (((0, 0), (1, 0), (1, 1), (2, 1)), (1, 0)),
    'T': (((0, 0), (1, 0), (2, 0), (1, 1)), (1, 0))
}
TILE_SIZE = 30, 30
START_ROWS = 6
START_GRID = (2, 4)


def random_shape(mino_map, mino_key):
    """
    Return a random polyomino shape.
    """
    try:
        return mino_map[mino_key]
    except KeyError:
        return random.choice(mino_map.values())


def new_polyomino(mino_map, mino_key=''):
    """
    Return a random new polyomino.
    """
    cells, center = random_shape(mino_map, mino_key)
    cells = kq2tile.random_rotate(cells, center)
    color, seam_color = kq2tile.random_color()

    offset = kq2tile.sub(START_GRID, center)
    tiles = []
    for cell in cells:
        row, col = kq2tile.add(cell, offset)
        tile = kq2tile.Tile(row, col, TILE_SIZE, TILE_SIZE, color)
        tiles.append(tile)

    return Polyomino(tiles, START_GRID, seam_color)


class Polyomino:
    """
    Polyomino class encapsulates a group of connected tiles.
    """
    def __init__(self, tiles, center, seam_color):
        """
        Initialize a polyomino.
        """
        self.tiles = tiles
        self.center = center
        self.seam_color = seam_color
        self.seams = self.new_seams()

    def __len__(self):
        """
        Return the number of tiles.
        """
        return len(self.tiles)

    def get_center(self):
        """
        Return rotation center.
        """
        return tuple(self.center)

    def get_cells(self):
        """
        Return occupied cells.
        """
        return [tile.get_cell() for tile in self.tiles]

    def new_seams(self):
        """
        Return all seams between any two tiles.
        """
        return kq2tile.cells_seams(self.get_cells(), TILE_SIZE)

    def move_cells(self, offset):
        """
        Return the occupied cells after move.
        """
        return [kq2tile.add(tile.get_cell(), offset)
                for tile in self.tiles]

    def rotate_cells(self):
        """
        Return the occupied cells after rotate.
        """
        return [kq2tile.rotate_cell(tile.get_cell(), self.center)
                for tile in self.tiles]

    def remove_rows(self, rows):
        """
        Return the remaining polyominoes after removing given rows.
        """
        remaining_tiles = [tile for tile in self.tiles
                           if tile.get_row() not in rows]
        return [Polyomino(tiles, self.center, self.seam_color)
                for tiles in kq2tile.connected_tiles(remaining_tiles)]

    def update(self, cells, offset):
        """
        Update position to given cells.
        """
        for tile, (row, col) in zip(self.tiles, cells):
            tile.set_cell(row, col, TILE_SIZE)
        self.center = kq2tile.add(self.center, offset)
        self.seams = self.new_seams()

    def draw(self, canvas):
        """
        Draw tiles and their seams on canvas.
        """
        for tile in self.tiles:
            tile.draw(canvas)
        for seam in self.seams:
            canvas.draw_polyline(seam, 2, self.seam_color)


class Game(kq2grid.Grid, kq2gui.Game):
    """
    Polyominoes (Tetris, Pentos, ...) game.
    """
    def __init__(self, rows, cols, mino_map):
        """
        Initialize a polyominoes game.
        """
        kq2grid.Grid.__init__(self, rows + START_ROWS, cols)
        kq2gui.Game.__init__(self)

        self.mino = None
        self.stable_minos = set()
        self.moving_minos = set()

        self.score = 0
        self.top_row = 0
        self.full_rows = set()

        self.routine = []
        self.mino_map = mino_map

    def __str__(self):
        """
        Return a string representation of all polyominoes.
        """
        board = [[' ' for _ in range(self.get_cols())]
                 for _ in range(self.get_rows())]

        cells = self.mino.get_cells()

        for mino in self.stable_minos:
            cells += mino.get_cells()

        for mino in self.moving_minos:
            cells += mino.get_cells()

        for col, row in cells:
            board[row][col] = '#'
        return '\n'.join(''.join(row) for row in board)

    def reset(self):
        """
        Override to reset all game elements.
        """
        kq2grid.Grid.reset(self)

        self.score = 0
        self.get_gui().update_score(self.score)
        self.top_row = self.get_rows()
        self.full_rows = set()

        self.new_mino()
        self.stable_minos = set()
        self.moving_minos = set()

    def set_routine(self, sequence_string):
        """
        Set the default new polyominoes sequence.
        """
        self.routine = list(sequence_string)

    def switch_mino_map(self):
        """
        Switch polyomino map and return its name.
        """
        if self.mino_map is PENTOMINO:
            self.mino_map = TETROMINO
            return 'Pentos'

        self.mino_map = PENTOMINO
        return 'Tetris'

    def new_mino(self):
        """
        Set control polyomino to a new polyomino.
        """
        if self.is_over():
            return

        mino_key = ''
        if self.routine:
            mino_key = self.routine.pop(0)
        self.mino = new_polyomino(self.mino_map, mino_key)

    def empty_row(self, row):
        """
        Empty a given row.
        """
        for col in range(self.get_cols()):
            self.pop_tile(row, col)

    def empty_rows(self, rows):
        """
        Empty given rows.
        """
        for row in rows:
            self.empty_row(row)

    def vacant(self, cells):
        """
        Return true if all given cells are empty.
        """
        for row, col in cells:
            if not self.is_empty(row, col):
                return False
        return True

    def is_full(self, row):
        """
        Return true if given row is full.
        """
        for row, col in self.get_row(row):
            if self.is_empty(row, col):
                return False
        return True

    def is_over(self):
        """
        Return true if game is over (maximum rows reached).
        """
        return self.top_row < START_ROWS

    def minos_in_row(self, row):
        """
        Return all polyominoes in given row.
        """
        ans = set()
        for row, col in self.get_row(row):
            if not self.is_empty(row, col):
                ans.add(self.get_tile(row, col))
        return ans

    def minos_in_rows(self, rows):
        """
        Return all polyominoes in given rows.
        """
        return set([mino for row in rows
                    for mino in self.minos_in_row(row)])

    def move_mino(self, mino, offset):
        """
        Try move given polyomino, return true if moved.
        """
        cells = mino.move_cells(offset)
        if self.vacant(cells):
            mino.update(cells, offset)
            return True
        return False

    def move_minos(self, minos, offset):
        """
        Try move given polyominoes, return true if any moved.
        """
        self.remove_stable_minos(minos, offset)
        if not minos:
            return False

        for mino in minos:
            self.move_mino(mino, offset)
        return True

    def remove_stable_minos(self, minos, offset):
        """
        Recursively remove all stable polyominoes from
        given set. The given set will be mutated.
        """
        removed = False
        for mino in set(minos):
            cells = mino.move_cells(offset)
            if not self.vacant(cells):
                minos.remove(mino)
                self.add_stable_mino(mino)
                removed = True
        if removed:
            self.remove_stable_minos(minos, offset)

    def add_stable_mino(self, mino):
        """
        Add a moving polyomino to stable set.
        Update game stats.
        """
        self.stable_minos.add(mino)

        for row, col in mino.get_cells():
            self.set_tile(row, col, mino)
            if self.top_row > row:
                self.top_row = row
            if self.is_full(row):
                self.full_rows.add(row)

    def remove_full_rows(self):
        """
        Remove all full rows from current game.
        Update game stats.
        """
        if self.full_rows:
            self.break_minos(self.full_rows)
            bottom_row = max(self.full_rows)
            moving_rows = range(self.top_row, bottom_row)
            for mino in self.minos_in_rows(moving_rows):
                self.stable_minos.remove(mino)
                self.moving_minos.add(mino)

            self.empty_rows(moving_rows)
            self.top_row = bottom_row + 1
            self.score += len(self.full_rows)
            self.get_gui().update_score(self.score)
            self.full_rows = set()

    def break_minos(self, rows):
        """
        Remove all full rows from affected polyominoes.
        Add remaining polyominoes to moving set.
        """
        for mino in self.minos_in_rows(rows):
            self.pop_tiles(mino.get_cells())
            self.stable_minos.remove(mino)
            new_minos = mino.remove_rows(rows)
            for new_mino in new_minos:
                self.moving_minos.add(new_mino)

    def rotate(self):
        """
        Rotate the control polyomino.
        """
        mino = self.mino
        cells = mino.rotate_cells()
        if self.vacant(cells):
            mino.update(cells, (0, 0))
            return True

        # try move left or right then rotate
        half_mino = (len(mino) + 1) / 2
        for idx in range(1, half_mino):
            for direction in [kq2tile.LEFT, kq2tile.RIGHT]:
                offset = kq2tile.mul(direction, idx)
                test_cells = [kq2tile.add(cell, offset)
                              for cell in cells]
                if self.vacant(test_cells):
                    mino.update(test_cells, offset)
                    return True

        return False

    def move(self, offset):
        """
        Move the control polyomino.
        """
        if offset is kq2tile.DOWN or offset is kq2tile.UP:
            self.y_move(offset)
        else:
            self.x_move(offset)

    def y_move(self, offset):
        """
        Move the control polyomino vertically.
        """
        if self.moving_minos:
            if not self.move_minos(self.moving_minos, offset):
                self.remove_full_rows()
        elif self.mino:
            if not self.move_mino(self.mino, offset):
                self.add_stable_mino(self.mino)
                self.remove_full_rows()
                self.new_mino()

    def x_move(self, offset):
        """
        Move the control polyomino horizontally.
        """
        self.move_mino(self.mino, offset)

    def draw(self, canvas):
        """
        Draw all polyominoes on canvas.
        """
        for mino in self.stable_minos:
            mino.draw(canvas)
        for mino in self.moving_minos:
            mino.draw(canvas)
        if self.mino:
            self.mino.draw(canvas)


class GUI(kq2gui.GUI):
    """
    Polyominoes game GUI, encapsulating the game and a real GUI,
    so that the real GUI can be easily replaced.
    """
    def __init__(self, gui, game):
        kq2gui.GUI.__init__(self, gui, game, 'Pentos',
                            TILE_SIZE[0] * game.get_cols(),
                            TILE_SIZE[1] * game.get_rows(),
                            'White')

        # set up GUI elements
        x_pos = TILE_SIZE[0] * game.get_cols()
        y_pos = TILE_SIZE[1] * START_ROWS
        self.deadline = [(0, y_pos), (x_pos, y_pos), 1, '']
        self.button_switch = self.add_button('Tetris', self.switch)
        self.button_pause = self.add_button('Pause', self.pause)
        self.label_score = self.add_label('')
        self.set_key_down_handler(self.key_down)
        self.set_key_up_handler(self.key_up)

        # set up game timers
        self.is_paused = False
        self.fast_fall = self.create_timer(40, self.move_down)
        self.slow_fall = self.create_timer(500, self.move_down)
        self.left_timer = self.create_timer(70, self.move_left)
        self.right_timer = self.create_timer(70, self.move_right)

        self.start_frame()

    def new_game(self):
        """
        Start a new game.
        """
        kq2gui.GUI.new_game(self)
        self.fast_fall.stop()
        self.left_timer.stop()
        self.right_timer.stop()

        self.slow_fall.start()
        self.is_paused = False
        self.deadline[-1] = "Green"

    def update_score(self, score):
        """
        Update game score on GUI.
        """
        self.label_score.set_text(str(score))

    def move_left(self):
        """
        Timer that moves game left.
        """
        self.get_game().move(kq2tile.LEFT)

    def move_right(self):
        """
        Timer that moves game right.
        """
        self.get_game().move(kq2tile.RIGHT)

    def move_down(self):
        """
        Timer that moves game down.
        """
        if self.get_game().is_over():
            self.pause()
            self.deadline[-1] = "Red"
        else:
            self.get_game().move(kq2tile.DOWN)

    def switch(self):
        map_name = self.get_game().switch_mino_map()
        self.button_switch.set_text(map_name)

    def pause(self):
        """
        Pause game.
        """
        if self.is_paused:
            self.is_paused = False
            self.slow_fall.start()
        else:
            self.is_paused = True
            self.slow_fall.stop()
            self.fast_fall.stop()

    def key_down(self, key):
        """
        Key down handler.
        """
        if self.game.is_over():
            return
        if key == self.key_code('up'):
            self.game.rotate()
        if key == self.key_code('down'):
            self.fast_fall.start()
            self.slow_fall.stop()
        if key == self.key_code('left'):
            self.left_timer.start()
        if key == self.key_code('right'):
            self.right_timer.start()
        if key == self.key_code('space'):
            self.pause()

    def key_up(self, key):
        """
        Key up handler.
        """
        if self.game.is_over():
            return
        if key == self.key_code('down'):
            self.fast_fall.stop()
            self.slow_fall.start()
        if key == self.key_code('left'):
            self.left_timer.stop()
        if key == self.key_code('right'):
            self.right_timer.stop()

    def draw(self, canvas):
        """
        Draw game on canvas.
        """
        kq2gui.GUI.draw(self, canvas)
        canvas.draw_line(*self.deadline)


def run(gui):
    """
    Start a game.
    """
    game = Game(15, 9, PENTOMINO)
    game.set_routine('UXU')
    GUI(gui, game).new_game()
