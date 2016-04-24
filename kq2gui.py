"""
GUI
"""


class Game:
    """
    A game that can talk to GUI.
    """
    def __init__(self):
        """
        Initialize game.
        """
        self.gui = None

    def set_gui(self, gui):
        """
        Set game's GUI.
        """
        self.gui = gui

    def get_gui(self):
        """
        Return game's GUI.
        """
        return self.gui


class GUI:
    """
    This GUI encapsulates SimpleGUI and a game.
    """
    def __init__(self, gui, game, game_name, width, height, canvas_color):
        """
        Initialize frame and basic event handlers.
        """
        self.gui = gui
        self.game = game
        self.game.set_gui(self)
        self.frame = gui.create_frame(game_name, width, height)
        self.frame.add_button("New Game", self.new_game)
        self.frame.set_canvas_background(canvas_color)
        self.frame.set_draw_handler(self.draw)

    def get_game(self):
        """
        Return the game of GUI.
        """
        return self.game

    def get_text_size(self, text, font_size, font_face):
        """
        Return the size of given text on canvas.
        """
        width = self.frame.get_canvas_textwidth(text, font_size, font_face)
        height = int(font_size * 0.618)
        return width, height

    def new_game(self):
        """
        Button handler. Reset game.
        """
        self.game.reset()

    def key_code(self, key):
        """
        Return the key code of key.
        """
        return self.gui.KEY_MAP[key]

    def create_timer(self, interval, timer_handler):
        """
        Create and return a timer handler.
        """
        return self.gui.create_timer(interval, timer_handler)

    def add_label(self, text, width=None):
        """
        Create and return a button handler.
        """
        if width:
            return self.frame.add_label(text, width)
        return self.frame.add_label(text)

    def add_button(self, text, button_handler, width=None):
        """
        Create and return a button handler.
        """
        if width:
            return self.frame.add_button(text, button_handler, width)
        return self.frame.add_button(text, button_handler)

    def set_key_down_handler(self, key_handler):
        """
        Set key down handler.
        """
        self.frame.set_keydown_handler(key_handler)

    def set_key_up_handler(self, key_handler):
        """
        Set key up handler.
        """
        self.frame.set_keyup_handler(key_handler)

    def set_mouse_click_handler(self, mouse_handler):
        """
        Set mouse click handler.
        """
        self.frame.set_mouseclick_handler(mouse_handler)

    def set_mouse_drag_handler(self, mouse_handler):
        """
        Set mouse drag handler.
        """
        self.frame.set_mousedrag_handler(mouse_handler)

    def start_frame(self):
        """
        Start the frame.
        """
        self.frame.start()

    def draw(self, canvas):
        """
        Update and draws game on canvas.
        """
        self.game.draw(canvas)
