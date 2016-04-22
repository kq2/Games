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


class Tile(kq2tile.Tile, kq2tile.TextRect):
    """
    2048 game tile.
    """
    def __init__(self, row, col, val):
        """
        Initialize a tile with value.
        """
        tile_color, font_size, font_color = TILES[val]

        kq2tile.TextRect.__init__(self, (0, 0), TILE_SIZE, tile_color,
                                  str(val), font_size, FONT, font_color)
        kq2tile.Tile.__init__(self, row, col, CELL_SIZE,
                              TILE_SIZE, tile_color)
        self.val = val

        ani = kq2animation.MixAnimation()
        ani.add_animation(kq2animation.Resizing())
        ani.add_animation(kq2animation.Moving())
        self.set_animation(ani)

    def __add__(self, other):
        """
        Add other tile, return a new tile with sum of both values.
        """
        return Tile(self.get_row(), self.get_col(),
                    self.get_val() + other.get_val())

    def __eq__(self, other):
        """
        Returns true if other tile has same value.
        """
        return self.get_val() == other.get_val()

    def get_val(self):
        """
        Returns tile's value.
        """
        return self.val

    def resize(self, size, animation_template):
        """
        Set resizing animation.
        """
        ani = self.get_animation().get_animation(kq2animation.Resizing)
        ani.move_to((0, 0), size, animation_template)

    def slide(self, cell, animation_template):
        """
        Set moving animation.
        """
        row, col = cell
        center = kq2tile.cell_center(row, col, CELL_SIZE)
        ani = self.get_animation().get_animation(kq2animation.Moving)
        ani.move_to(self.get_center(), center, animation_template)

    def is_moving(self):
        """
        Return true if tile is moving.
        """
        ani = self.get_animation().get_animation(kq2animation.Moving)
        return ani.is_moving()


class Game(kq2grid.Grid, kq2gui.Game):
    """
    2048 game.
    """
    def __init__(self, rows, cols):
        """
        Initialize a 2048 game board.
        """
        kq2grid.Grid.__init__(self, rows, cols)

        self.iter_order = {
            UP: [[(row, col) for row in range(rows)]
                 for col in range(cols)],
            DOWN: [[(row, col) for row in range(rows - 1, -1, -1)]
                   for col in range(cols)],
            LEFT: [[(row, col) for col in range(cols)]
                   for row in range(rows)],
            RIGHT: [[(row, col) for col in range(cols - 1, -1, -1)]
                    for row in range(rows)]
        }

        self.score = 0
        self.moving_tiles = set()   # tiles that are moving
        self.drawing_tiles = set()  # tiles that are drawing
        self.holding_tiles = set()  # tiles that will be drawn after moving
        self.merging_tiles = set()  # tiles that will be removed after moving

    def __str__(self):
        """
        Return a text representation of board.
        """
        ans = '\n'
        for row in range(self.get_rows()):
            for col in range(self.get_cols()):
                tile = self.get_tile(row, col)
                ans += '%5d' % tile.get_val() if tile else '    .'
            ans += '\n'
        return ans

    def reset(self):
        """
        Override to reset all game elements.
        """
        kq2grid.Grid.reset(self)

        self.score = 0
        self.moving_tiles = set()
        self.drawing_tiles = set()
        self.holding_tiles = set()
        self.merging_tiles = set()

        for _ in range(2):
            self.new_tile()
        self.draw_holding_tiles()

    def new_tile(self):
        """
        Randomly add a new tile onto board.
        """
        empty_cells = self.empty_cells()
        if empty_cells:
            row, col = random.choice(empty_cells)
            val = 2 if random.random() < .9 else 4
            tile = Tile(row, col, val)
            tile.resize(TILE_SIZE, APPEAR_ANIMATION)
            self.set_tile(row, col, tile)
            self.holding_tiles.add(tile)
            self.score += 1
            self.get_gui().update_score(self.score)
            print self

    def move(self, direction):
        """
        Move (merge) all tiles to one direction.
        """
        moved = False
        for line in self.iter_order[direction]:
            if self.merge(line):
                moved = True
        if moved:
            self.new_tile()

    def merge(self, cells):
        """
        Merge one line of tiles, front to back.
        Main game logic.
        """
        moved = False
        tiles = self.pop_tiles(cells)
        idx = 0
        for tile in tiles:
            row, col = cells[idx]
            prev_tile = self.get_tile(row, col)
            if not prev_tile:
                self.set_tile(row, col, tile)
            elif prev_tile == tile:
                new_tile = self.merge_tiles(prev_tile, tile)
                self.set_tile(row, col, new_tile)
                idx += 1
            else:
                idx += 1
                row, col = cells[idx]
                self.set_tile(row, col, tile)

            if (row, col) != tile.get_cell():
                self.moving_tiles.add(tile)
                tile.slide((row, col), SLIDE_ANIMATION)
                tile.set_cell(row, col)
                moved = True
        return moved

    def merge_tiles(self, tile1, tile2):
        """
        Return a combined new tile.
        """
        new_tile = tile1 + tile2
        new_tile.resize(TILE_SIZE, MERGE_ANIMATION)
        self.merging_tiles.add(tile1)
        self.merging_tiles.add(tile2)
        self.holding_tiles.add(new_tile)
        return new_tile

    def draw_holding_tiles(self):
        """
        Draw hidden new tiles.
        """
        self.drawing_tiles.update(self.holding_tiles)
        self.holding_tiles = set()

    def remove_merging_tiles(self):
        """
        Remove merged tiles from drawing.
        """
        self.drawing_tiles.difference_update(self.merging_tiles)
        self.merging_tiles = set()

    def is_moving(self):
        """
        Return true is board is moving.
        """
        if self.moving_tiles:
            return True
        return False

    def update(self):
        """
        Update moving, merging and holding tiles.
        """
        for tile in set(self.moving_tiles):
            if not tile.is_moving():
                self.moving_tiles.remove(tile)
            if not self.moving_tiles:
                self.remove_merging_tiles()
                self.draw_holding_tiles()

    def draw(self, canvas):
        """
        Draw this game on canvas.
        """
        self.update()
        for tile in self.drawing_tiles:
            tile.draw(canvas, self.get_gui())


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
        if self.get_game().is_moving():
            return

        for key_name, direction in self.keys.items():
            if key == self.key_code(key_name):
                self.get_game().move(direction)
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
