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


def oval_pos(width, height, center, angle):
    """
    Return a point position on an oval.
    """
    return (center[0] + math.cos(angle) * width / 2,
            center[1] + math.sin(angle) * height / 2)


def x_flip_rect(width, height, center, angle, visual_diff=4):
    """
    Return a horizontally flipping rectangle.
    """
    upper_center = (center[0], center[1] - height / 2.0)
    lower_center = (center[0], center[1] + height / 2.0)
    return [oval_pos(width, visual_diff, upper_center, angle + math.pi),
            oval_pos(width, visual_diff, upper_center, angle),
            oval_pos(width, visual_diff, lower_center, -angle),
            oval_pos(width, visual_diff, lower_center, -angle + math.pi)]


def y_flip_rect(width, height, center, angle, visual_diff=4):
    """
    Return a vertically flipping rectangle.
    """
    left_center = (center[0] - width / 2.0, center[1])
    right_center = (center[0] + width / 2.0, center[1])
    return [oval_pos(visual_diff, height, left_center, angle + math.pi / 2),
            oval_pos(visual_diff, height, left_center, angle - math.pi / 2),
            oval_pos(visual_diff, height, right_center, -angle - math.pi / 2),
            oval_pos(visual_diff, height, right_center, -angle + math.pi / 2)]


class Moving:
    """
    Moving animation.
    """
    def __init__(self):
        """
        Initialize a moving animation.
        """
        self.pos_list = []
        self.vel_list = []

    def set_pos(self, start_pos, end_pos, animation_template=None):
        """
        Set animation to move to given destination.
        """
        if animation_template:
            self.pos_list += tup_slices(start_pos, end_pos,
                                        animation_template)

    def move(self, vel, animation_template=None):
        """
        Set animation to move given velocity.
        """
        if animation_template:
            self.vel_list += tup_slices((0, 0), vel,
                                        animation_template)

    def is_moving(self):
        """
        Return true if moving.
        """
        if self.pos_list or self.vel_list:
            return True
        return False

    def update(self, item):
        """
        Update the position of given item.
        """
        if self.pos_list:
            pos = self.pos_list.pop(0)
            item.set_pos(pos)
        if self.vel_list:
            vel = self.vel_list.pop(0)
            item.move(vel)


class Flipping:
    """
    Flipping animation.
    """
    def __init__(self, angle, front_color, back_color):
        """
        Initialize a flipping animation.
        """
        self.angle = angle
        self.front_color = front_color
        self.back_color = back_color

        self.angle_list = []
        self.angle_vel_list = []

    def get_angle(self):
        """
        Return angle.
        """
        return self.angle

    def set_angle(self, angle, animation_template=None):
        """
        Change angle.
        """
        if animation_template:
            self.angle_list += slices(self.angle, angle,
                                      animation_template)
        else:
            self.angle = angle

    def flip(self, angle_vel, animation_template=None):
        """
        Change angle velocity.
        """
        if animation_template:
            self.angle_vel_list += slices(0, angle_vel,
                                          animation_template)
        else:
            self.angle += angle_vel

    def is_flipping(self):
        """
        Return true if flipping.
        """
        if self.angle_list or self.angle_vel_list:
            return True
        return False

    def is_front(self):
        """
        Return true if front side is facing up.
        """
        return 0 <= (self.angle + math.pi / 2) % (2 * math.pi) < math.pi

    def update(self, item, flip_rect_fn=None):
        """
        Update color and rectangle of given item.
        """
        # update angle
        if self.angle_list:
            angle = self.angle_list.pop(0)
            self.set_angle(angle)
        if self.angle_vel_list:
            angle_vel = self.angle_vel_list.pop(0)
            self.flip(angle_vel)

        # update color
        if self.is_front():
            item.set_color(self.front_color)
        else:
            item.set_color(self.back_color)

        # update rectangle
        if flip_rect_fn:
            flip_rect = flip_rect_fn(self.angle,
                                     item.get_size(),
                                     item.get_center())
            item.set_rect(flip_rect)
