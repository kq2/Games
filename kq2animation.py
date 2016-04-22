"""
Animations
"""
import math


def slices(start, end, ratios):
    """
    Return a list of slices based on given ratios.
    """
    diff = end - start
    return [start + diff * ratio for ratio in ratios]


def tup_slices(start_tup, end_tup, ratios):
    """
    Return a list of sliced tuples based on given ratios.
    """
    return zip(slices(start_tup[0], end_tup[0], ratios),
               slices(start_tup[1], end_tup[1], ratios))


def oval_pos(size, center, angle):
    """
    Return a point position on an oval.
    """
    return (center[0] + math.cos(angle) * size[0] / 2,
            center[1] + math.sin(angle) * size[1] / 2)


def x_flip_rect(size, center, angle, visual_diff=4):
    """
    Return a horizontally flipping rectangle.
    """
    upper_center = (center[0], center[1] - size[1] / 2.0)
    lower_center = (center[0], center[1] + size[1] / 2.0)
    size = (size[0], visual_diff)
    return [oval_pos(size, upper_center, angle + math.pi),
            oval_pos(size, upper_center, angle),
            oval_pos(size, lower_center, -angle),
            oval_pos(size, lower_center, -angle + math.pi)]


def y_flip_rect(size, center, angle, visual_diff=4):
    """
    Return a vertically flipping rectangle.
    """
    left_center = (center[0] - size[0] / 2.0, center[1])
    right_center = (center[0] + size[0] / 2.0, center[1])
    size = (visual_diff, size[1])
    return [oval_pos(size, left_center, angle + math.pi / 2),
            oval_pos(size, left_center, angle - math.pi / 2),
            oval_pos(size, right_center, -angle - math.pi / 2),
            oval_pos(size, right_center, -angle + math.pi / 2)]


class Animation:
    """
    Animation class.
    """
    def __init__(self):
        """
        Initialize a animation.
        """
        self.moves = []

    def move_to(self, start, end, animation_template=None):
        """
        Set animation move to given end.
        """
        if animation_template:
            self.moves += tup_slices(start, end, animation_template)
        else:
            self.moves = [end]

    def move_by(self, start, offset, animation_template=None):
        """
        Set animation move by given offset.
        """
        end = (start[0] + offset[0],
               start[1] + offset[1])
        self.move_to(start, end, animation_template)

    def is_moving(self):
        """
        Return true if moving.
        """
        if self.moves:
            return True
        return False

    def update(self, item):
        """
        Remove and return the current update.
        """
        if self.moves:
            return self.moves.pop(0)


class Moving(Animation):
    """
    Moving animation.
    """
    def update(self, item):
        """
        Override to update the position of given item.
        """
        if self.is_moving():
            center = Animation.update(self, item)
            item.set_center(center)


class Resizing(Animation):
    """
    Resizing animation.
    """
    def update(self, item):
        """
        Override to update the size of given item.
        """
        if self.is_moving():
            size = Animation.update(self, item)
            item.set_size(size)


class Flipping(Animation):
    """
    Flipping animation.
    """
    def __init__(self, angle, front_color, back_color):
        """
        Initialize a flipping animation.
        """
        Animation.__init__(self)

        self.angle = angle
        self.front_color = front_color
        self.back_color = back_color
        self.flip_rect_fn = x_flip_rect

    def set_front_color(self, color):
        """
        Change front color to given color.
        """
        self.front_color = color

    def set_back_color(self, color):
        """
        Change back color to given color.
        """
        self.back_color = color

    def flip_to(self, angle, animation_template=None, flip_rect_fn=None):
        """
        Flip angle to given angle.
        """
        if flip_rect_fn:
            self.flip_rect_fn = flip_rect_fn

        if animation_template:
            start = (self.angle, 0)
            end = (angle, 0)
            self.move_to(start, end, animation_template)
        else:
            self.angle = angle

    def flip_by(self, angle, animation_template=None, flip_rect_fn=None):
        """
        Flip angle by given angle.
        """
        angle = self.angle + angle
        self.flip_to(angle, animation_template, flip_rect_fn)

    def is_front(self):
        """
        Return true if front side is facing up.
        """
        return 0 <= (self.angle + math.pi / 2) % (2 * math.pi) < math.pi

    def update_color(self, item):
        """
        Update item's color.
        """
        if self.is_front():
            item.set_color(self.front_color)
            item.set_border_color(self.front_color)
        else:
            item.set_color(self.back_color)
            item.set_border_color(self.back_color)

    def update_rect(self, item):
        """
        Update item's rectangle.
        """
        rect = self.flip_rect_fn(item.get_size(),
                                 item.get_center(),
                                 self.angle)
        item.set_rect(rect)

    def update(self, item):
        """
        Override to update color and rectangle of given item.
        """
        if self.is_moving():
            self.angle = Animation.update(self, item)[0]
            self.update_color(item)
            self.update_rect(item)


class MixAnimation(Animation):
    """
    Composite animation.
    """
    def __init__(self):
        """
        Initialize a composite animation.
        """
        Animation.__init__(self)
        self.animations = {}

    def add_animation(self, ani):
        """
        Add an animation.
        """
        self.animations[type(ani)] = ani

    def get_animation(self, ani_type):
        """
        Return an animation by given type.
        """
        return self.animations[ani_type]

    def is_moving(self):
        """
        Override to return true if any is moving.
        """
        for ani in self.animations.values():
            if ani.is_moving():
                return True
        return False

    def update(self, item):
        """
        Override to update all animations.
        """
        for ani in self.animations.values():
            ani.update(item)
