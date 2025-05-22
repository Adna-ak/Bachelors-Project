"""
File:     movement_generator.py
Authors:  Özde Pilli (s5257018) and Adna Kapidžić (s5256100)
Group:    5

Description:
    This module defines a MovementGenerator class which is responsible for
    identifying stressed words and assigning appropriate gestures (beat and
    iconic) to those words based on predefined rules and dictionaries. It also
    ensures that gestures are properly spaced, formatted into frames, and
    include default joint values to prevent errors during robotic movement
    execution.
"""

import random
from typing import Dict, List
from nltk.tokenize import RegexpTokenizer
from src.robot_movements.gesture_library import DELTA_T, BEAT_GESTURES, DEFAULT_JOINT_VALUES, hello_iconic, i_iconic, you_iconic
from src.robot_movements.stress_word_analyzer import StressWordAnalyzer

SPEECH_RATE_ENGLISH = 0.340211161387632  # Estimated seconds per word
SPEECH_RATE_DUTCH = 0.31088476361070403  # Estimated seconds per word - 0.4, as it aligns better


class MovementGenerator:
    """
    This class identifies stressed words and assigns appropriate gestures based
    on predefined rules and dictionaries. It also ensures gestures are properly
    spaced and formatted into frames.
    """

    def __init__(self, text: str, language: str = "en"):
        self.text = text
        self.language = language
        self.delta_t = DELTA_T
        self.speech_rate = SPEECH_RATE_ENGLISH if language == "en" else SPEECH_RATE_DUTCH
        self.stress_word_analyzer = StressWordAnalyzer(text, language=self.language)
        self.words = RegexpTokenizer(r"\b\w+(?:'\w+)?\b").tokenize(text.lower())
        self.beat_gestures = []
        self.iconic_gestures = []
        self.frames = []

    # SIMILAR TO ASSIGNMENTS 1 AND 2
    def get_beat_gestures(self) -> List[Dict]:
        """
        Determines appropriate beat gestures for emphasized words in the text.

        Returns:
            List[Dict]: A list of dictionaries, each containing the index of
            the word in the text and the associated gesture for that word.
        """
        print("Generating beat gestures...")
        stress_words = self.stress_word_analyzer.get_stress_words()

        gesture_options = list(BEAT_GESTURES.values())
        random.shuffle(gesture_options)

        for i, (word_index, word) in enumerate(stress_words):
            beat_gesture = gesture_options[i % len(gesture_options)]
            beat_gesture_name = next(key for key, value in BEAT_GESTURES.items() if value == beat_gesture)
            print(f"Beat gesture for '{word}' at index {word_index}: {beat_gesture_name}")
            self.beat_gestures.append({"index": word_index, "gesture": beat_gesture})

        print("Exiting get_beat_gestures function...")
        return self.beat_gestures

    # SIMILAR TO ASSIGNMENTS 1 AND 2
    def get_iconic_gestures(self) -> List[Dict]:
        """
        Extracts iconic gestures from the text based on predefined word lists.

        Returns:
            List[Dict]: A list of dictionaries, each containing the index of
            the word in the text and the associated gesture for that word.

        Notes:
            The gap between consecutive gestures is controlled to ensure there
            is enough time to execute them.
        """
        print("Generating iconic gestures...")
        gap = 5  # To fine-tune movement

        for word_index, word in enumerate(self.words):
            if self.iconic_gestures and abs(word_index - self.iconic_gestures[-1]["index"]) < gap:
                continue
            if word in ["hello", "hi", "hey", "goodbye", "bye", "welcome", "hallo", "dag", "hai", "hoi", "hé", "doei", "doeg", "welkom"]:
                gesture = hello_iconic
                name = "hello_iconic"
            elif word in ["i", "me", "my", "mine", "myself", "i'm", "i'll", "i've", "ik", "mij", "mijn", "mezelf", "mijzelf"]:
                gesture = i_iconic
                name = "i_iconic"
            elif word in ["you", "your", "yours", "yourself", "you're", "you'll", "you've", "jij", "je", "jou", "jouw", "jezelf", "u", "uw", "uzelf", "jullie"]:
                gesture = you_iconic
                name = "you_iconic"
            else:
                continue

            print(f"Iconic gesture for '{word}' at index {word_index}: {name}")
            self.iconic_gestures.append({"index": word_index, "gesture": gesture})

        print("Exiting get_iconic_gestures function...")
        return self.iconic_gestures

    # SIMILAR TO ASSIGNMENTS 1 AND 2
    def get_gesture_frames(self) -> List[Dict]:
        """
        Generates the sequence of frames representing gestures for the provided
        text. This combines both beat and iconic gestures and arranges them in
        time order.

        Returns:
            List[Dict]: A list of dictionaries, each containing time and
            gesture data for the robot's movements.

        Notes:
            The gestures are filtered to ensure they do not overlap too
            closely.
        """
        print("Generating gesture frames...")
        beat_gestures = self.get_beat_gestures()
        iconic_gestures = self.get_iconic_gestures()
        speech_duration = len(self.words) * self.speech_rate * 1000  # In ms
        gap = 6  # To fine-tune movement
        current_time = None

        all_gestures = sorted(beat_gestures + iconic_gestures, key=lambda x: x["index"])

        print("All gestures have been combined and sorted by index. Starting frame generation in get_gesture_frames function...")
        for gesture in all_gestures:
            current_time = gesture["index"] * self.speech_rate * 1000  # Onset time of gesture

            # Adding the normal stand a bit closer to the next frame makes the movements smoother
            if len(self.frames) >= 2 and self.frames[-1]["time"] < current_time - 0.65 * self.delta_t:
                current_time += 0.65 * self.delta_t
                self.frames.append({"time": current_time, "data": {"body.head.pitch": 0.08, "body.head.roll": 0.0, "body.head.yaw": 0.0, "body.arms.right.upper.pitch": -0.4, "body.arms.left.upper.pitch": -0.4, "body.arms.right.lower.roll": -1.0, "body.arms.left.lower.roll": -1.0}})

            if current_time + gesture["gesture"][-1]["time"] * self.delta_t >= speech_duration:
                print(f"Skipping '{self.words[gesture['index']]}' at index {gesture['index']} (exceeds duration).")
                break

            if self.frames and abs(gesture["index"] - last_position) < gap:
                print(f"Skipping '{self.words[gesture['index']]}' at index {gesture['index']} (too close to previous gesture).")
                continue

            print(f"Adding '{self.words[gesture['index']]}' at index {gesture['index']} to frames.")
            for frame in gesture["gesture"]:
                current_time += frame["time"] * self.delta_t
                self.frames.append({"time": current_time, "data": frame["data"]})

            last_position = gesture["index"]

        if current_time is not None:
            print(f"Speech Duration: {speech_duration:.2f}ms, Movement Duration: {current_time:.2f}ms")

        print("Exiting get_gesture_frames function...")
        return self.frames

    # SIMILAR TO ASSIGNMENTS 1 AND 2
    def complete_frames(self) -> List[Dict]:
        """
        Completes the frames by ensuring that each frame has the default joint
        values filled in to prevent errors elicited in perform_movement.

        Returns:
            List[Dict]: A list of dictionaries, where each dictionary contains
            time and complete data (all default joints) for the robot's
            movement.

        Notes:
            Each frame is updated with the default joint values, and the
            gesture-specific data is merged into it.
        """
        updated_frames = []

        for frame in self.frames:
            complete_frame = {"time": frame["time"], "data": DEFAULT_JOINT_VALUES.copy()}
            complete_frame["data"].update(frame["data"])
            updated_frames.append(complete_frame)

        return updated_frames
