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


def list_slices(start_list, end_list, ratios):
    """
    Return a list of sliced lists based on given ratios.
    """
    return zip(*(slices(start, end, ratios)
                 for start, end in zip(start_list, end_list)))


def list_add(list1, list2):
    """
    Return a list of sums of elements.
    """
    return [sum(val) for val in zip(list1, list2)]


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
    One-dimension animation class.
    """
    def __init__(self):
        """
        Initialize an 1-dimension animation.
        """
        self.stop = 0
        self.moves = []

    def get_stop(self):
        """
        Return stop.
        """
        return self.stop

    def set_stop(self, stop):
        """
        Set stop.
        """
        self.stop = stop

    def move(self, stop, frames_template=None, is_vel=False):
        """
        Add moves to given stop.
        """
        if is_vel:
            stop += self.stop
        if not frames_template:
            frames_template = [1]

        self.moves += slices(self.stop, stop, frames_template)
        self.stop = stop

    def is_moving(self):
        """
        Return true if moving.
        """
        if self.moves:
            return True
        return False

    def update(self, item):
        """
        Remove and return the current move.
        """
        if self.moves:
            return self.moves.pop(0)


class NAnimation(Animation):
    """
    Multi-dimension animation class.
    """
    def __init__(self, num_dimension=2):
        """
        Initialize an n-dimension animation.
        """
        Animation.__init__(self)
        self.set_stop([0] * num_dimension)

    def move(self, stop, frames_template=None, is_vel=False):
        """
        Override to handle high dimension.
        """
        if is_vel:
            stop = list_add(self.stop, stop)
        if not frames_template:
            frames_template = [1]

        self.moves += list_slices(self.stop, stop, frames_template)
        self.stop = stop


class Moving(NAnimation):
    """
    Moving animation.
    """
    def update(self, item):
        """
        Override to update the position of given item.
        """
        if self.is_moving():
            move = Animation.update(self, item)
            item.set_center(move)


class Resizing(NAnimation):
    """
    Resizing animation.
    """
    def update(self, item):
        """
        Override to update the size of given item.
        """
        if self.is_moving():
            move = Animation.update(self, item)
            item.set_size(move)


class Flipping(Animation):
    """
    Flipping animation.
    """
    def __init__(self, angle, front_color, back_color):
        """
        Initialize a flipping animation.
        """
        Animation.__init__(self)
        self.set_stop(angle)

        self.angle = angle
        self.front_color = front_color
        self.back_color = back_color
        self.flip_fn = x_flip_rect

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

    def set_flip_fn(self, flip_fn):
        """
        Set flip computation function.
        """
        self.flip_fn = flip_fn

    def is_front(self):
        """
        Return true if front side is facing up.
        """
        return (0 <= (self.angle + math.pi / 2) % (2 * math.pi)
                < math.pi)

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
        rect = self.flip_fn(item.get_size(),
                            item.get_center(),
                            self.angle)
        item.set_rect(rect)

    def update(self, item):
        """
        Override to update color and rectangle of given item.
        """
        if self.is_moving():
            self.angle = Animation.update(self, item)
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
        Return an animation of given type.
        """
        return self.animations[ani_type]

    def remove_animation(self, ani_type):
        """
        Remove and return an animation by given type.
        """
        return self.animations.pop(ani_type)

    def get_stop(self, ani_type=None):
        """
        Override to return stop of given type.
        """
        if ani_type:
            return self.get_animation(ani_type).get_stop()

    def set_stop(self, stop, ani_type=None):
        """
        Override to set stop of given type.
        """
        if ani_type:
            return self.get_animation(ani_type).set_stop(stop)

    def move(self, stop, frames_template=None, is_vel=False, ani_type=None):
        """
        Override to update animation of given type.
        """
        if ani_type:
            self.get_animation(ani_type).move(stop, frames_template, is_vel)

    def is_moving(self, ani_type=None):
        """
        Override to return true if any is moving.
        """
        if ani_type:
            return self.get_animation(ani_type).is_moving()

        for ani in self.animations.values():
            if ani.is_moving():
                return True
        return False

    def update(self, item, ani_type=None):
        """
        Override to update all animations.
        """
        if ani_type:
            self.get_animation(ani_type).update(item)
        else:
            for ani in self.animations.values():
                ani.update(item)
