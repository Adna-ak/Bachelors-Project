"""
File:     gesture_library.py
Authors:  Özde Pilli (s5257018) and Adna Kapidžić (s5256100)
Group:    5

Description:
    This module defines a collection of gesture sequences and movement data
    for use in robotics (Alpha Mini). The gestures are represented as a list
    of time-stamped joint angles, specifying movements for different parts of
    the body (such as head, upper arms, and lower arms). The module includes
    iconic gestures as well as beat gestures.
"""

from typing import List, Dict

DELTA_T = 500  # Base movement duration in milliseconds: to quickly change movement pace for all movements, so they stay proportional to e.o.

# Head goes up and down with both arms going up a bit beyond normal stand and then a bit lower than normal stand. Lower arms go a little in and out.
# Every gesture ends in the normal stand
head_nod_with_arms = [
    {"time": 0.45, "data": {"body.head.pitch": -0.08, "body.arms.right.upper.pitch": -0.47, "body.arms.left.upper.pitch": -0.47, "body.arms.right.lower.roll": -0.9, "body.arms.left.lower.roll": -0.9}},
    {"time": 1.1, "data": {"body.head.pitch": 0.08, "body.arms.right.upper.pitch": -0.35, "body.arms.left.upper.pitch": -0.35, "body.arms.right.lower.roll": -1.1, "body.arms.left.lower.roll": -1.1}},
    {"time": 1.75, "data": {"body.head.pitch": 0.08, "body.arms.right.upper.pitch": -0.4, "body.arms.left.upper.pitch": -0.4, "body.arms.right.lower.roll": -1.0, "body.arms.left.lower.roll": -1.0}}
]

# head.roll is for moving head to shoulder (slanting). body.head.roll 0.1 moves head a bit to right shoulder
# Both arms go up beyond normal stand. Lower arms go in and out.
head_tilt_with_arms = [
    {"time": 0.45, "data": {"body.head.roll": 0.1, "body.arms.left.upper.pitch": -0.45, "body.arms.right.upper.pitch": -0.47, "body.arms.right.lower.roll": -0.9, "body.arms.left.lower.roll": -0.9}},
    {"time": 1.1, "data": {"body.head.roll": 0.1, "body.arms.left.upper.pitch": -0.35, "body.arms.right.upper.pitch": -0.35, "body.arms.right.lower.roll": -1.2, "body.arms.left.lower.roll": -1.2}},
    {"time": 1.75, "data": {"body.head.roll": 0.0, "body.arms.left.upper.pitch": -0.4, "body.arms.right.upper.pitch": -0.4, "body.arms.right.lower.roll": -1.0, "body.arms.left.lower.roll": -1.0}}
]

# Head goes from middle to right (0.4). Both arms are a little higher than normal stand. Lower arms go in and out.
# For lower arms (range: -1.74 to 0.000650): The higher the minus value, the more the lower arms go in.
head_to_right_with_arms = [
    {"time": 0.45, "data": {"body.head.yaw": 0.3, "body.arms.right.lower.roll": -1.0, "body.arms.left.lower.roll": -1.0, "body.arms.right.upper.pitch": -0.5, "body.arms.left.upper.pitch": -0.5}},
    {"time": 1.1, "data": {"body.head.yaw": 0.3, "body.arms.right.lower.roll": -1.2, "body.arms.left.lower.roll": -1.2, "body.arms.right.upper.pitch": -0.5, "body.arms.left.upper.pitch": -0.5}},
    {"time": 1.75, "data": {"body.head.yaw": 0.0, "body.arms.right.lower.roll": -1.0, "body.arms.left.lower.roll": -1.0, "body.arms.right.upper.pitch": -0.4, "body.arms.left.upper.pitch": -0.4}}
]

# Head goes from middle to left (-0.4). Both arms are a little higher than normal stand. Lower arms go in and out.
head_to_left_with_arms = [
    {"time": 0.45, "data": {"body.head.yaw": -0.3, "body.arms.right.lower.roll": -1.0, "body.arms.left.lower.roll": -1.0, "body.arms.right.upper.pitch": -0.5, "body.arms.left.upper.pitch": -0.5}},
    {"time": 1.1, "data": {"body.head.yaw": -0.3, "body.arms.right.lower.roll": -1.2, "body.arms.left.lower.roll": -1.2, "body.arms.right.upper.pitch": -0.5, "body.arms.left.upper.pitch": -0.5}},
    {"time": 1.75, "data": {"body.head.yaw": 0.0, "body.arms.right.lower.roll": -1.0, "body.arms.left.lower.roll": -1.0, "body.arms.right.upper.pitch": -0.4, "body.arms.left.upper.pitch": -0.4}}
]

# Both arms go up beyond belly button with lower arms going a bit out.
arms_up_and_out = [
    {"time": 0.45, "data": {"body.arms.left.upper.pitch": -0.57, "body.arms.right.upper.pitch": -0.57, "body.arms.right.lower.roll": -1.0, "body.arms.left.lower.roll": -1.0}},
    {"time": 1.1, "data": {"body.arms.left.upper.pitch": -0.45, "body.arms.right.upper.pitch": -0.45, "body.arms.right.lower.roll": -1.15, "body.arms.left.lower.roll": -1.15}},
    {"time": 1.75, "data": {"body.arms.left.upper.pitch": -0.4, "body.arms.right.upper.pitch": -0.4, "body.arms.right.lower.roll": -1.0, "body.arms.left.lower.roll": -1.0}}
]

# Both arms go up beyond belly button, head goes down a bit (body.head.pitch 0.15)
head_up_arms_up = [
    {"time": 0.45, "data": {"body.arms.left.upper.pitch": -0.57, "body.arms.right.upper.pitch": -0.57, "body.head.pitch": -0.08}},
    {"time": 1.1, "data": {"body.arms.left.upper.pitch": -0.35, "body.arms.right.upper.pitch": -0.35, "body.head.pitch": -0.08}},
    {"time": 1.75, "data": {"body.arms.left.upper.pitch": -0.4, "body.arms.right.upper.pitch": -0.4, "body.head.pitch": 0.08}}
]

# Both lower arms go a bit out and the head goes a bit down into a deeper nod compared to normal stand
lower_arms_out = [
    {"time": 0.45, "data": {"body.arms.right.lower.roll": -0.8, "body.arms.left.lower.roll": -0.8, "body.head.pitch": 0.16}},
    {"time": 1.1, "data": {"body.arms.right.lower.roll": -1.0, "body.arms.left.lower.roll": -1.0, "body.head.pitch": 0.08}}
]

# Iconic gesture for "hello", "hi", "hey", "goodbye", "bye", and "welcome"
# Wave with left arm
hello_iconic = [
    {"time": 1.1, "data": {"body.arms.left.upper.pitch": -2, "body.head.roll": -0.15, "body.arms.left.lower.roll": -1.2}},
    {"time": 1.65, "data": {"body.arms.left.upper.pitch": -2, "body.head.roll": 0.0, "body.arms.left.lower.roll": -0.7}},
    {"time": 2.2, "data": {"body.arms.left.upper.pitch": -0.4, "body.head.roll": 0.0, "body.arms.left.lower.roll": -1.0}}
]

# Iconic gesture for "i", "me", "my", "mine", "myself", "i'm", "i'll", and "i've"
# Pointing at itself with left arm
i_iconic = [
    {"time": 1.0, "data": {"body.arms.left.upper.pitch": -0.7, "body.arms.left.lower.roll": -1.74, "body.head.pitch": 0.174}},
    {"time": 1.65, "data": {"body.arms.left.upper.pitch": -0.4, "body.arms.left.lower.roll": -1.0, "body.head.pitch": 0.08}}
]

# Iconic gesture for "you", "your", "yours", "yourself", "you're", "you'll", and "you've"
# Pointing at user with left arm
you_iconic = [
    {"time": 0.7, "data": {"body.head.pitch": 0.14, "body.arms.left.upper.pitch": -0.9, "body.arms.left.lower.roll": -0.5}},
    {"time": 1.4, "data": {"body.head.pitch": 0.14, "body.arms.left.upper.pitch": -1.3, "body.arms.left.lower.roll": -0.5}},
    {"time": 2.05, "data": {"body.head.pitch": 0.08, "body.arms.left.upper.pitch": -0.4, "body.arms.left.lower.roll": -1.0}}
]

BEAT_GESTURES: Dict[str, List[Dict[str, float]]] = {
    "nod with arms": head_nod_with_arms,
    "head tilt with arms": head_tilt_with_arms,
    "head to right with arms": head_to_right_with_arms,
    "head to left with arms": head_to_left_with_arms,
    "arms up and out": arms_up_and_out,
    "head up and arms up": head_up_arms_up,
    "lower arms out": lower_arms_out
}

# Normal stand values
DEFAULT_JOINT_VALUES: Dict[str, float] = {
    "body.head.yaw": 0.0,
    "body.head.roll": 0.0,
    "body.head.pitch": 0.08,
    "body.arms.right.upper.pitch": -0.4,
    "body.arms.right.lower.roll": -1.0,
    "body.arms.left.upper.pitch": -0.4,
    "body.arms.left.lower.roll": -1.0,
}
