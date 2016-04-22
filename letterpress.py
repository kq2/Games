"""
Game Letterpress
"""
import random
import urllib2
import kq2tile
import kq2grid
import kq2gui

# http://en.wikipedia.org/wiki/Letter_frequency
# LETTER_FREQUENCY, CUMULATIVE_DISTRIBUTION
# 'A': .08167, .08167
# 'B': .01492, .09659
# 'C': .02782, .12441
# 'D': .04253, .16694
# 'E': .12702, .29396
# 'F': .02228, .31624
# 'G': .02015, .33639
# 'H': .06094, .39733
# 'I': .06966, .46699
# 'J': .00153, .46852
# 'K': .00772, .47624
# 'L': .04025, .51649
# 'M': .02406, .54055
# 'N': .06749, .60804
# 'O': .07507, .68311
# 'P': .01929, .70240
# 'Q': .00095, .70335
# 'R': .05987, .76322
# 'S': .06327, .82649
# 'T': .09056, .91705
# 'U': .02758, .94463
# 'V': .00978, .95441
# 'W': .02360, .97801
# 'X': .00150, .97951
# 'Y': .01974, .99925
# 'Z': .00074, 1


# ALPHABET = [chr(num) for num in range(65, 91)]
VOWELS = ['A', 'E', 'I', 'O', 'U']
CONSONANTS = ['B', 'C', 'D', 'F', 'G', 'H', 'J',
              'K', 'L', 'M', 'N', 'P', 'Q', 'R',
              'S', 'T', 'V', 'W', 'X', 'Y', 'Z']

# normalized consonants cumulative distribution
CONSONANTS_DISTRIBUTION = [
    .02410,
    .06905,
    .13776,
    .17375,
    .20630,
    .30475,
    .30723,
    .31970,
    .38472,
    .42359,
    .53263,
    .56379,
    .56532,
    .66205,
    .76426,
    .91056,
    .92636,
    .96449,
    .96691,
    .99880,
    1
]
TILE_SIZE = 80, 80
CELL_SIZE = 80, 80
TILE_COLOR = 'rgba(246,246,246,1)', 'rgba(249,249,249,1)'
OWNER_COLOR = 'rgba(119,200,245,1)', 'rgba(247,153,141,1)'
GUARD_COLOR = 'rgba(0,162,255,1)', 'rgba(255,67,46,1)'
FONT_SIZE = 23
FONT_FACE = 'serif'
FONT_COLOR = 'BLACK'
WORD_ROWS = 3
WORDS_FILE = 'assets_scrabble_words3.txt'


def load_words(url):
    """
    Return a set of English words.
    """
    words_file = urllib2.urlopen(url)

    ans = set()
    for line in words_file.readlines():
        word = line[:-1]
        ans.add(word)
    return ans


def random_vowels(num_vowel, max_occur=2):
    """
    Return a list of random vowels.
    """
    ans = []
    occurs = {}
    while len(ans) < num_vowel:
        vowel = random.choice(VOWELS)
        if vowel not in occurs:
            occurs[vowel] = 0
        if occurs[vowel] < max_occur:
            occurs[vowel] += 1
            ans.append(vowel)
    return ans


def random_consonants(num_consonant, max_occur=3):
    """
    Return a list of random consonants based on its frequency.
    """
    ans = []
    occurs = {}
    while len(ans) < num_consonant:
        rand = random.random()
        for idx, dist in enumerate(CONSONANTS_DISTRIBUTION):
            if idx not in occurs:
                occurs[idx] = 0
            if rand < dist and occurs[idx] < max_occur:
                ans.append(CONSONANTS[idx])
                occurs[idx] += 1
                break
    return ans


def random_letters(num_vowel, num_consonant):
    """
    Return a list of random letters.
    """
    vowels = random_vowels(num_vowel)
    consonants = random_consonants(num_consonant)
    ans = vowels + consonants
    random.shuffle(ans)
    return ans


def get_num_vowel(num_letter):
    """
    Return the number of vowels.
    """
    rand = random.random()
    if rand < .2:
        return int(num_letter * 0.12)
    if rand < .7:
        return int(num_letter * 0.16)
    return int(num_letter * 0.2)


def align_items(num_item, max_item_width, max_total_width, canvas_width):
    """
    Evenly align items in the center.
    Return items's width and centers.
    """
    width = min(num_item * max_item_width, max_total_width)
    item_width = width / num_item
    first_center = canvas_width / 2 - width / 2 + item_width / 2
    centers = [first_center + idx * item_width
               for idx in range(num_item)]
    return item_width, centers


def align_picked_tiles(canvas_width, picked_tiles):
    """
    Align picked tiles to spell.
    """
    tile_width, centers = align_items(
        len(picked_tiles), CELL_SIZE[0] / 2,
        canvas_width - CELL_SIZE[0] / 2,
        canvas_width
    )
    for idx, tile in enumerate(picked_tiles):
        center = centers[idx], (WORD_ROWS - 1) * CELL_SIZE[1]
        size = tile_width, CELL_SIZE[1]
        tile.set_center(center)
        tile.set_size(size)


class Tile(kq2tile.Tile, kq2tile.TextRect):
    """
    Letterpress game tile.
    """
    def __init__(self, row, col, size, color, text,
                 font_size, font_face, font_color):
        """
        Initialize a tile with game attributes.
        """
        kq2tile.TextRect.__init__(self, (0, 0), size, color,
                                  text, font_size, font_face, font_color)
        kq2tile.Tile.__init__(self, row, col, CELL_SIZE, size, color)

        self.set_border_color('rgba(0,0,0,.02)')

        self.hovering = False
        self.selected = False
        self.guarded = False
        self.owner = None
        self.offset()

    def reset(self):
        """
        Reset tile for new game.
        """
        self.hovering = False
        self.selected = False
        self.guarded = False
        self.owner = None
        self.offset()

    def offset(self):
        """
        Update tile's position to its real position on canvas, and
        keep its original cell unchanged.
        """
        row, col = self.get_cell()
        self.set_cell(row + WORD_ROWS, col, CELL_SIZE)
        self.set_cell(row, col)
        self.set_size(TILE_SIZE)

    def hover(self):
        """
        Hover tile and set its color to transparent.
        """
        self.hovering = True
        color = self.get_color().replace(',1)', ',.618)')
        self.set_color(color)

    def land(self):
        """
        Land tile and set its color back to solid.
        """
        self.hovering = False
        color = self.get_color().replace(',.618)', ',1)')
        self.set_color(color)

    def is_selected(self):
        """
        Return true if tile is selected.
        """
        return self.selected

    def select(self):
        """
        Select tile to spell.
        """
        self.selected = True

    def un_select(self):
        """
        Un-select tile from spelling, and put tile back to grid.
        """
        self.selected = False
        self.offset()

    def is_guarded(self):
        """
        Return true if tile is guarded.
        """
        return self.guarded

    def guard(self):
        """
        Guard tile, change its color.
        """
        self.set_color(GUARD_COLOR[self.owner])
        self.guarded = True

    def un_guard(self):
        """
        Remove tile's guard, set it color back.
        """
        self.set_color(OWNER_COLOR[self.owner])
        self.guarded = False

    def get_owner(self):
        """
        Return tile's owner.
        """
        return self.owner

    def set_owner(self, owner):
        """
        Set tile's owner.
        """
        self.owner = owner


class Game(kq2grid.Grid, kq2gui.Game):
    """
    Letterpress game.
    """
    def __init__(self, rows, cols):
        """
        Initialize a letterpress game board.
        """
        kq2grid.Grid.__init__(self, rows, cols)

        self.over = False
        self.player = 0
        self.streak = 0
        self.scores = [0, 0]
        self.drag_tile = None
        self.picked_tiles = []
        self.played_words = set()
        self.words = load_words(WORDS_FILE)

        for row, col in self:
            tile = Tile(
                row, col, TILE_SIZE, '', '',
                FONT_SIZE, FONT_FACE, FONT_COLOR
            )
            self.set_tile(row, col, tile)

    def reset(self):
        """
        Reset game.
        """
        self.over = False
        self.player = 0
        self.streak = 0
        self.scores = [0, 0]
        self.drag_tile = None
        self.picked_tiles = []
        self.played_words = set()

        num_tile = len(self)
        num_vowel = get_num_vowel(num_tile)
        num_consonant = num_tile - num_vowel
        letters = random_letters(num_vowel, num_consonant)
        for row, col in self:
            tile = self.get_tile(row, col)
            tile.set_text(letters.pop())
            tile.reset()

            # guarantee adjacent tiles have different colors
            idx = (row ^ col) % 2
            tile.set_color(TILE_COLOR[idx])

        self.get_gui().update_msg('')
        self.get_gui().update_scores(self.scores)

    def switch_player(self):
        """
        Switch player.
        """
        self.player ^= 1

    def tile_at(self, pos):
        """
        Return a tile at given position.
        """
        row, col = kq2tile.pos2cell(pos, CELL_SIZE, (-WORD_ROWS, 0))

        # position is in letter gird
        if row >= 0:
            tile = self.get_tile(row, col)
            if not tile.is_selected():
                return tile
        else:
            # position is in picked tiles
            for tile in self.picked_tiles:
                if tile is self.drag_tile:
                    continue
                if tile.has_pos(pos):
                    return tile

            # no tile at this position
            return None

    def drag(self, pos):
        """
        Drag a picked tile to rearrange tile order.
        """
        if not self.drag_tile:
            tile = self.tile_at(pos)
            if tile and tile.is_selected():
                self.drag_tile = tile
                self.drag_tile.hover()

        if self.drag_tile:

            # try insert dragging tile when over selected tiles
            tile = self.tile_at(pos)
            if tile and tile.is_selected():
                idx = self.picked_tiles.index(tile)
                self.picked_tiles.remove(self.drag_tile)
                self.picked_tiles.insert(idx, self.drag_tile)
                self.get_gui().align_picked_tiles(self.picked_tiles)

            # update dragging tile's position
            size = self.drag_tile.get_size()
            self.drag_tile.set_center(pos)
            self.drag_tile.set_size(size)

    def click(self, pos):
        """
        Select or un-select a tile.
        """
        if self.over:
            return

        # if mouse dragging is released, put drag tile back
        if self.drag_tile:
            self.drag_tile.land()
            if self.drag_tile.is_selected():
                self.get_gui().align_picked_tiles(self.picked_tiles)
            else:
                self.drag_tile.un_select()
            self.drag_tile = None
            return

        # if mouse click, select the correct tile
        tile = self.tile_at(pos)
        if tile:
            if tile.is_selected():
                self.un_select(tile)
            else:
                self.select(tile)
            self.get_gui().align_picked_tiles(self.picked_tiles)

    def select(self, tile):
        """
        Select tile to spell, and update scores.
        """
        tile.select()
        self.picked_tiles.append(tile)

        if tile.is_guarded() or tile.get_owner() is self.player:
            return

        opponent = self.player ^ 1
        if tile.get_owner() is opponent:
            self.scores[opponent] -= 1
        self.scores[self.player] += 1
        self.get_gui().update_scores_pos(self.scores)

    def un_select(self, tile):
        """
        Put tile back to grid, and update scores.
        """
        tile.un_select()
        self.picked_tiles.remove(tile)

        if tile.is_guarded() or tile.get_owner() is self.player:
            return

        opponent = self.player ^ 1
        if tile.get_owner() is opponent:
            self.scores[opponent] += 1
        self.scores[self.player] -= 1
        self.get_gui().update_scores_pos(self.scores)

    def clear(self):
        """
        Put all picked tiles back to grid.
        """
        for tile in list(self.picked_tiles):
            self.un_select(tile)

    def submit(self):
        """
        Submit picked tiles to see if it's a real word.
        """
        if not self.picked_tiles:
            return

        word = ''.join(map(str, self.picked_tiles)).lower()

        if word in self.played_words:
            msg = word + ' was already played. '

        elif word in self.words:
            self.add_word(word)
            self.streak += 1
            msg = str(self.streak) + '. ' + word

        else:
            msg = word + ' is not word. '

        self.get_gui().update_msg(msg)

    def add_word(self, word):
        """
        Add a word to played words. Main game logic.
        """
        print word
        self.played_words.add(word)

        # add all "sub-words" of this word to played.
        for idx in range(len(word)):
            self.played_words.add(word[:idx + 1])

        # put each tile back to grid and try change its owner
        changed_tiles = set()
        for tile in self.picked_tiles:
            if self.change_owner(tile):
                changed_tiles.add(tile)
        self.clear()

        # add all affected neighbors to changed tiles
        for tile in changed_tiles:
            changed_tiles.update(self.neighbors(tile))

        # try change each tile's guard in changed tiles
        for tile in changed_tiles:
            self.change_guard(tile)

        self.switch_player()
        self.over = (sum(self.scores) == len(self))

    def neighbors(self, tile):
        """
        Return the neighbors of given tile in grid.
        """
        ans = set()
        for row, col in kq2tile.cell_4_neighbor(tile.get_cell()):
            if self.is_valid(row, col):
                ans.add(self.get_tile(row, col))
        return ans

    def change_owner(self, tile):
        """
        Change tile's owner to current player.
        Return true if changed.
        """
        if tile.is_guarded() or tile.get_owner() is self.player:
            return False
        tile.set_owner(self.player)
        return True

    def change_guard(self, tile):
        """
        Guard a tile if it's surrounded by same owner,
        or vice versa.
        """
        if tile.get_owner() is None:
            return

        for neighbor in self.neighbors(tile):
            if neighbor.get_owner() is not tile.get_owner():
                tile.un_guard()
                return

        tile.guard()

    def draw_scores(self, canvas):
        """
        Draw scores on canvas.
        """
        dot_pos = self.get_gui().get_dots_pos()
        scores_pos = self.get_gui().get_scores_pos()

        if not self.over:
            canvas.draw_circle(dot_pos[self.player], 1, 1,
                               GUARD_COLOR[self.player])
        for idx in range(2):
            canvas.draw_text(str(self.scores[idx]), scores_pos[idx],
                             FONT_SIZE, GUARD_COLOR[idx], FONT_FACE)

    def draw(self, canvas):
        """
        Draw all tiles on canvas.
        """
        self.draw_scores(canvas)

        # draw all tiles except drag tile
        for row, col in self:
            tile = self.get_tile(row, col)
            if tile is not self.drag_tile:
                tile.draw(canvas, self.get_gui())

        # draw drag tile on the top
        if self.drag_tile:
            self.drag_tile.draw(canvas, self.get_gui())


class GUI(kq2gui.GUI):
    """
    Letterpress game GUI.
    """
    def __init__(self, gui, game):
        """
        Initialize a game GUI, encapsulating the game and a real GUI,
        so that the real GUI can be easily replaced.
        """
        self.dots_pos = []
        self.scores_pos = []
        self.width = TILE_SIZE[0] * game.get_cols()
        self.height = TILE_SIZE[1] * (game.get_rows() + WORD_ROWS)
        kq2gui.GUI.__init__(self, gui, game, 'Letterpress',
                            self.width, self.height, 'White')

        self.add_label('')
        self.set_mouse_click_handler(self.click)
        self.set_mouse_drag_handler(self.drag)
        self.add_button('Clear', self.clear)
        self.add_button('Submit', self.submit)
        self.label = self.add_label('')
        self.start_frame()

    def get_dots_pos(self):
        """
        Return dots's positions.
        """
        return tuple(self.dots_pos)

    def get_scores_pos(self):
        """
        Return scores's positions.
        """
        return tuple(self.scores_pos)

    def update_scores_pos(self, scores):
        """
        Update scores's positions on canvas.
        """
        self.dots_pos = []
        self.scores_pos = []
        _, centers = align_items(len(scores), TILE_SIZE[0] * 2,
                                 self.width, self.width)
        for score, center in zip(scores, centers):
            text_center = center, TILE_SIZE[1] / 4 * 3
            text_size = self.get_text_size(str(score), FONT_SIZE, FONT_FACE)
            text_pos = kq2tile.text_pos(text_center, text_size)
            dot_pos = kq2tile.add(text_center, (0, text_size[1]))
            self.scores_pos.append(text_pos)
            self.dots_pos.append(dot_pos)

    def align_picked_tiles(self, picked_tiles):
        """
        Align picked tiles to spell.
        """
        if picked_tiles:
            align_picked_tiles(self.width, picked_tiles)

    def click(self, pos):
        """
        Mouse click handler.
        """
        self.get_game().click(pos)

    def drag(self, pos):
        """
        Mouse drag handler.
        """
        self.get_game().drag(pos)

    def clear(self):
        """
        Submit button handler.
        """
        self.get_game().clear()

    def submit(self):
        """
        Submit button handler.
        """
        self.get_game().submit()

    def update_msg(self, msg):
        """
        Update message on GUI.
        """
        self.label.set_text(msg)

    def update_scores(self, scores):
        """
        Update scores on GUI.
        """
        self.update_scores_pos(scores)


def run(gui):
    """
    Start a game.
    """
    game = Game(5, 5)
    GUI(gui, game).new_game()
