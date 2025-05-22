"""
File:     say_animated.py
Authors:  Özde Pilli (s5257018) and Adna Kapidžić (s5256100)
Group:    5

Description:
    This module defines the say_animated function, which simulates an animated
    speech and gesture sequence for a robot. The robot will speak the provided
    text and perform gestures based on the content of the text. It utilizes
    predefined gesture generators and performs movement synchronously with the
    speech output. The sequence ensures that the gestures are appropriately
    timed with the spoken text, providing a more natural animation.
"""

from typing import Generator
from twisted.internet.defer import DeferredList, inlineCallbacks
from autobahn.twisted.util import sleep
from alpha_mini_rug import perform_movement
from src.robot_movements.movement_generator import MovementGenerator


@inlineCallbacks
def say_animated(session, text: str, language: str = "en") -> Generator[None, None, None]:
    """
    Simulates an animated speech and gesture sequence for the robot. The robot
    will speak the text and perform gestures simultaneously.

    Args:
        session: The session object for interacting with the robot.
        text (str): The text to be spoken and acted out by the robot.
        language (str): The language of the speech (default is English).

    Returns:
        Generator[None, None, None]: A coroutine generator which, when
        yielded, performs the speech and gesture sequence.
    """
    print("Entering say_animated function...")
    print(f"Input text: '{text}'")

    if language not in ["en", "nl"]:
        raise ValueError(f"Unsupported language: {language}. Only 'en' (English) and 'nl' (Dutch) are supported.")

    yield session.call("rie.dialogue.config.language", lang=language)

    gesture_generator = MovementGenerator(text, language)
    frames = gesture_generator.get_gesture_frames()

    if not frames:
        print("No movement frames generated. Skipping movements.")
        yield session.call("rie.dialogue.say", text=text)
        yield sleep(2)
        return

    frames = gesture_generator.complete_frames()
    speech = session.call("rie.dialogue.say", text=text)
    movements = perform_movement(session, frames, mode="linear", sync=False, force=False)

    yield DeferredList([speech, movements])
    yield session.call("rom.optional.behavior.play", name="BlocklyStand")
    yield sleep(2)
    print("Exiting say_animated function...")
