"""
Game Memory
"""
import math
import random
import kq2tile
import kq2grid
import kq2gui
import kq2animation

TILE_SIZE = 100, 100
CELL_SIZE = 106, 106
ANGLE_ANIMATION = [
    0.16, 0.31, 0.45, 0.58, 0.7,
    0.81, 0.91, 1.0, 1.08, 1.15,
    1.14, 1.12, 1.09, 1.05, 1
]


def random_colors(num_color):
    """
    Return given number of random paired colors.
    """
    ans = []
    while len(ans) < num_color:
        color, _ = kq2tile.random_color()
        ans.append(color)
        ans.append(color)
    random.shuffle(ans)
    return ans


def valid_click(pos, tile):
    """
    Return true if click is valid to Memory game.
    """
    animation = tile.get_animation()
    return (not animation.is_moving()
            and animation.is_front()
            and tile.has_pos(pos))


def new_tile(tile, tile_color):
    """
    Add animation to new tile.
    """
    animation = kq2animation.Flipping(0, tile_color, tile_color)
    tile.set_animation(animation)


def reset_tile(tile):
    """
    Add animation to show tile's color then hide.
    """
    animation = tile.get_animation()
    animation.set_back_color(tile.get_color())
    animation.move(math.pi)
    animation.move(0, ANGLE_ANIMATION)


def flip_tile(tile, angle, is_vel=False):
    """
    Add animation to flip tile.
    """
    animation = tile.get_animation()
    animation.move(angle, ANGLE_ANIMATION, is_vel)


class Game(kq2grid.Grid, kq2gui.Game):
    """
    Memory game.
    """
    def __init__(self, rows, cols):
        """
        Initialize a game with tiles.
        """
        kq2grid.Grid.__init__(self, rows, cols)

        self.score = 0
        self.exposed_tiles = []

        tile_color = 'White'
        for row, col in self:
            tile = kq2tile.Tile(row, col, CELL_SIZE,
                                TILE_SIZE, tile_color)
            tile.set_border_color(tile_color)
            self.set_tile(row, col, tile)
            new_tile(tile, tile_color)

    def reset(self):
        """
        Override to reset each tile's color and animation.
        """
        self.score = 0
        self.exposed_tiles = []
        self.get_gui().update_score(self.score)

        colors = random_colors(len(self))
        for row, col in self:
            tile = self.get_tile(row, col)
            tile.set_color(colors.pop())
            reset_tile(tile)

    def click(self, pos):
        """
        Click on a tile.
        """
        row, col = kq2tile.pos2cell(pos, CELL_SIZE)
        tile = self.get_tile(row, col)

        if tile and valid_click(pos, tile):
            click_on_left = pos[0] < tile.get_center()[0]
            angle = -math.pi if click_on_left else math.pi
            self.flip(tile, angle)

    def flip(self, tile, angle):
        """
        Flip a tile. Main game logic.
        """
        # if 2 tiles are already exposed, flip them back if
        # they have different colors.
        if len(self.exposed_tiles) == 2:
            tile1 = self.exposed_tiles.pop()
            tile2 = self.exposed_tiles.pop()
            if tile1.get_color() != tile2.get_color():
                flip_tile(tile1, 0)
                flip_tile(tile2, 0)

        # if 1 or 0 tile exposed, flip it to expose
        if len(self.exposed_tiles) < 2:
            flip_tile(tile, angle, is_vel=True)
            self.exposed_tiles.append(tile)

        self.score += 1
        self.get_gui().update_score(self.score)

    def draw(self, canvas):
        """
        Draw all tiles on canvas.
        """
        for row, col in self:
            self.get_tile(row, col).draw(canvas)


class GUI(kq2gui.GUI):
    """
    Memory game GUI.
    """
    def __init__(self, gui, game):
        """
        Initialize a game GUI, encapsulating the game and a real GUI,
        so that the real GUI can be easily replaced.
        """
        kq2gui.GUI.__init__(self, gui, game, 'Memory',
                            CELL_SIZE[0] * game.get_cols(),
                            CELL_SIZE[1] * game.get_rows(),
                            'Black')

        self.set_mouse_click_handler(self.click)
        self.label = self.add_label('0')
        self.start_frame()

    def click(self, pos):
        """
        Mouse click handler.
        """
        self.get_game().click(pos)

    def update_score(self, score):
        """
        Update score on GUI.
        """
        self.label.set_text(str(score))


def run(gui):
    """
    Start a game.
    """
    game = Game(3, 3)
    GUI(gui, game).new_game()
