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


class Moving:
    """
    Moving animation.
    """
    def __init__(self):
        """
        Initialize a moving animation.
        """
        self.pos_list = []

    def set_pos(self, start_pos, end_pos, animation_template=None):
        """
        Set animation to move to given destination.
        """
        if animation_template:
            self.pos_list += tup_slices(start_pos, end_pos,
                                        animation_template)
        else:
            self.pos_list = [end_pos]

    def move(self, start_pos, vel, animation_template=None):
        """
        Set animation to move given velocity.
        """
        end_pos = (start_pos[0] + vel[0],
                   start_pos[1] + vel[1])
        self.set_pos(start_pos, end_pos, animation_template)

    def is_moving(self):
        """
        Return true if moving.
        """
        if self.pos_list:
            return True
        return False

    def update(self, item):
        """
        Update the position of given item.
        """
        if self.pos_list:
            pos = self.pos_list.pop(0)
            item.set_pos(pos)


class Flipping:
    """
    Flipping animation.
    """
    def __init__(self, angle, front_color, back_color, flip_rect_fn):
        """
        Initialize a flipping animation.
        """
        self.angle = angle
        self.front_color = front_color
        self.back_color = back_color
        self.flip_rect_fn = flip_rect_fn

        self.angle_list = []

    def get_angle(self):
        """
        Return angle.
        """
        return self.angle

    def set_angle(self, angle, animation_template=None):
        """
        Change angle to given angle.
        """
        if animation_template:
            self.angle_list += slices(self.angle, angle,
                                      animation_template)
        else:
            self.angle = angle

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

    def flip(self, angle_vel, animation_template=None):
        """
        Change angle by given angle velocity.
        """
        self.set_angle(self.angle + angle_vel, animation_template)

    def is_flipping(self):
        """
        Return true if flipping.
        """
        if self.angle_list:
            return True
        return False

    def is_front(self):
        """
        Return true if front side is facing up.
        """
        return 0 <= (self.angle + math.pi / 2) % (2 * math.pi) < math.pi

    def update_color(self, tile):
        """
        Update tile's color.
        """
        if self.is_front():
            tile.set_color(self.front_color)
            tile.set_border_color(self.front_color)
        else:
            tile.set_color(self.back_color)
            tile.set_border_color(self.back_color)

    def update_rect(self, item):
        """
        Update tile's rectangle.
        """
        flip_rect = self.flip_rect_fn(
            item.get_size(), item.get_center(), self.angle
        )
        item.set_rect(flip_rect)

    def update(self, item):
        """
        Update color and rectangle of given item.
        """
        if self.angle_list:
            angle = self.angle_list.pop(0)
            self.set_angle(angle)
            self.update_color(item)
            self.update_rect(item)
