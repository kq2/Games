"""
Game 2048
"""
import random
import kq2tile
import kq2grid
import kq2gui
import kq2animation

# 2048 tiles (tile color, font size, font color)
TILES = {
    2: ('#EEE4DA', 54, 'Black'),
    4: ('#EDE0C8', 54, 'Black'),
    8: ('#F2B179', 54, 'White'),
    16: ('#F59563', 48, 'White'),
    32: ('#F67C60', 48, 'White'),
    64: ('#F65E3B', 48, 'White'),
    128: ('#EDCF72', 42, 'White'),
    256: ('#EDCC62', 42, 'White'),
    512: ('#EDC851', 42, 'White'),
    1024: ('#EDC746', 36, 'White'),
    2048: ('#EDC22E', 36, 'White'),
    4096: ('#85C0FD', 36, 'White'),
    8192: ('#CD4F95', 36, 'White')
}
TILE_SIZE = 100, 100
CELL_SIZE = 100, 100
FONT = 'monospace'
APPEAR_ANIMATION = (.72, .82, .9, .96, 1)
MERGE_ANIMATION = (1, 1.03, 1.04, 1.03, 1)
SLIDE_ANIMATION = (.29, .53, .72, .86, .95, .99, 1)
UP = 1
DOWN = 2
LEFT = 3
RIGHT = 4
OFFSETS = {UP: (1, 0),
           DOWN: (-1, 0),
           LEFT: (0, 1),
           RIGHT: (0, -1)}


class Tile(kq2tile.Tile, kq2tile.TextRect):
    """
    2048 game tile.
    """
    def __init__(self, row, col, val):
        """
        Initialize a tile with value and animation.
        """
        tile_color, font_size, font_color = TILES[val]

        kq2tile.TextRect.__init__(self, (0, 0), TILE_SIZE, tile_color,
                                  str(val), font_size, FONT, font_color)
        kq2tile.Tile.__init__(self, row, col, CELL_SIZE,
                              TILE_SIZE, tile_color)
        self.val = val

    def __add__(self, other):
        """
        Add another tile, return a new tile with sum of both values.
        """
        return Tile(self.get_row(), self.get_col(),
                    self.get_val() + other.get_val())

    def __eq__(self, other):
        """
        Return true if other tile has same value.
        """
        return self.get_val() == other.get_val()

    def get_val(self):
        """
        Return tile's value.
        """
        return self.val


class Game(kq2grid.Grid, kq2gui.Game):
    """
    2048 game.
    """
    def __init__(self, rows, cols):
        """
        Initialize a 2048 game board.
        """
        kq2grid.Grid.__init__(self, rows, cols)

        self.init_cells = {
            UP: self.get_row(0),
            DOWN: self.get_row(rows - 1),
            LEFT: self.get_col(0),
            RIGHT: self.get_col(cols - 1)
        }

        self.num_tile = 0
        self.moved = False
        self.animation = AnimationManager()

    def __str__(self):
        """
        Return a text representation of board.
        """
        ans = '\n'
        for row in range(self.get_rows()):
            for col in range(self.get_cols()):
                tile = self.get_tile(row, col)
                ans += (str(tile) if tile else '.').rjust(5)
            ans += '\n'
        return ans

    def reset(self):
        """
        Override to reset all game elements.
        """
        kq2grid.Grid.reset(self)

        self.moved = False
        self.num_tile = 0
        self.get_gui().update_score(self.num_tile)
        self.animation.reset()

        for _ in range(2):
            self.new_tile()

    def new_tile(self):
        """
        Randomly add a new tile onto board.
        """
        empty_cells = self.empty_cells()
        if empty_cells:
            row, col = random.choice(empty_cells)
            val = 2 if random.random() < .9 else 4
            tile = Tile(row, col, val)
            self.set_tile(row, col, tile)
            self.num_tile += 1
            self.get_gui().update_score(self.num_tile)
            self.animation.new_tile(tile)
            print self

    def get_line(self, init_cell, offset):
        """
        Return a line of cells.
        """
        ans = []
        cell = init_cell
        while self.is_valid(*cell):
            ans.append(cell)
            cell = kq2tile.add(cell, offset)
        return ans

    def move(self, direction):
        """
        Move (merge) all tiles to one direction.
        """
        if self.animation.is_moving():
            return

        self.moved = False
        for init_cell in self.init_cells[direction]:
            self.merge(self.get_line(init_cell, OFFSETS[direction]))
        if self.moved:
            self.new_tile()

    def merge(self, cells):
        """
        Merge one line of tiles, front to back.
        Main game logic.
        """
        tiles = self.pop_tiles(cells)
        idx = 0
        for tile in tiles:
            row, col = cells[idx]
            prev_tile = self.get_tile(row, col)
            if not prev_tile:
                self.set_tile(row, col, tile)
            elif prev_tile == tile:
                new_tile = prev_tile + tile
                self.set_tile(row, col, new_tile)
                self.animation.merge(prev_tile, tile, new_tile)
                idx += 1
            else:
                idx += 1
                row, col = cells[idx]
                self.set_tile(row, col, tile)

            if (row, col) != tile.get_cell():
                self.animation.move_tile(row, col, tile)
                tile.set_cell(row, col)
                self.moved = True

    def draw(self, canvas):
        """
        Draw this game on canvas.
        """
        self.animation.draw(canvas, self.get_gui())


class AnimationManager:
    """
    2048 game animation manager.
    """
    def __init__(self):
        """
        Initialize all animation elements.
        """
        self.drawing_tiles = set()  # tiles that are drawing
        self.moving_tiles = set()  # tiles that are moving
        self.hiding_tiles = set()  # tiles that will be drawn after moving
        self.merging_tiles = []  # tiles that will be removed after moving

    def reset(self):
        """
        Reset all animation elements.
        """
        self.drawing_tiles = set()
        self.moving_tiles = set()
        self.hiding_tiles = set()
        self.merging_tiles = []

    def new_tile(self, tile, animation=APPEAR_ANIMATION):
        """
        Add animation to new tile.
        """
        size_ani = kq2animation.Resizing()
        move_ani = kq2animation.Moving()
        mix_ani = kq2animation.MixAnimation()

        # add the resizing animation when tile appears
        size_ani.move(TILE_SIZE, animation)

        # set the move animation's initial position
        move_ani.set_stop(tile.get_center())

        mix_ani.add_animation(size_ani)
        mix_ani.add_animation(move_ani)
        tile.set_animation(mix_ani)
        self.hiding_tiles.add(tile)

    def move_tile(self, row, col, tile):
        """
        Add move animation to tile.
        """
        ani = tile.get_animation()
        pos = kq2tile.cell_center(row, col, CELL_SIZE)
        ani.move(pos, SLIDE_ANIMATION, ani_type=kq2animation.Moving)
        self.moving_tiles.add(tile)

    def merge(self, tile1, tile2, merged_tile):
        """
        Add appear animation to the new merged tile.
        """
        self.new_tile(merged_tile, MERGE_ANIMATION)
        for tile in (tile1, tile2):
            self.drawing_tiles.remove(tile)
            self.merging_tiles.append(tile)

    def is_moving(self):
        """
        Return true if there is a moving tile
        """
        if self.moving_tiles:
            return True
        return False

    def update(self):
        """
        Update all animation elements.
        """
        for tile in set(self.moving_tiles):
            if not tile.get_animation().is_moving():
                self.moving_tiles.remove(tile)
        if not self.moving_tiles and self.hiding_tiles:
            self.drawing_tiles.update(self.hiding_tiles)
            self.hiding_tiles = set()
            self.merging_tiles = []

    def draw(self, canvas, gui):
        """
        Draw animation.
        """
        self.update()
        for tile in self.drawing_tiles:
            tile.draw(canvas, gui)

        # For any merging pair, draw second tile above first tile.
        for tile in self.merging_tiles:
            tile.draw(canvas, gui)


class GUI(kq2gui.GUI):
    """
    2048 game GUI.
    """
    def __init__(self, gui, game):
        """
        Initialize a game GUI, encapsulating the game and a real GUI,
        so that the real GUI can be easily replaced.
        """
        kq2gui.GUI.__init__(self, gui, game, '2048',
                            CELL_SIZE[0] * game.get_cols(),
                            CELL_SIZE[1] * game.get_rows(),
                            '#F4F1EE')

        self.keys = {'up': UP, 'down': DOWN,
                     'left': LEFT, 'right': RIGHT}
        self.label = self.add_label('')
        self.set_key_down_handler(self.key_down)
        self.start_frame()

    def key_down(self, key):
        """
        key-down handler
        """
        game = self.get_game()
        for key_name, direction in self.keys.items():
            if key == self.key_code(key_name):
                game.move(direction)
                break

    def update_score(self, score):
        """
        Update score on GUI.
        """
        self.label.set_text(str(score))


def run(gui):
    """
    Start a 2048 game.
    """
    game = Game(4, 4)
    GUI(gui, game).new_game()
