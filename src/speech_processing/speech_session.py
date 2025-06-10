"""
File:     speech_session.py
Authors:  Özde Pilli (s5257018) and Adna Kapidžić (s5256100)
Group:    5

Description:
    This module defines the SpeechRecognitionSession class, responsible for
    handling speech recognition, user interaction, and providing feedback.
    It ensures continuous prompting until valid speech is detected.
"""

import os
from typing import Generator, Optional
from twisted.internet.defer import inlineCallbacks
from src.speech_processing.speech_to_text import SpeechToText
from src.robot_movements.say_animated import say_animated
from src.utils import generate_message_using_llm
from src.language_feedback.language_assistant import LanguageAssistant
from src.taboo_game.keywords_handler import KeywordsHandler


class SpeechRecognitionSession:
    """
    Handles speech recognition within a session, including prompting the user
    for input, detecting prolonged silence, and responding accordingly.
    """

    def __init__(self, session, version):
        self.session = session

        if version not in {"experiment", "control"}:
            raise ValueError(f"Invalid version: {version}. Must be 'experiment' or 'control'.")

        self.get_feedback = (version == "experiment")
        self.processor = SpeechToText()
        self.keywords_handler = KeywordsHandler(session)
        self.praise_streak = 0

    @inlineCallbacks
    def validate_user_input(
        self, prompt_message: str, silence_message: str, language: str = "en"
    ) -> Generator[Optional[str], None, str]:
        yield say_animated(self.session, prompt_message, language)

        if self.get_feedback:
            self.language_assistant = LanguageAssistant(self.session)

        while True:
            user_input = yield self.recognize_speech()

            if user_input:
                if self.get_feedback:
                    percent_english = self.language_assistant.calculate_language_usage(user_input)
                    if percent_english >= 70:  # Keeping in mind that this is for kids, 70% is okay
                        if self.praise_streak == 2:
                            self.praise_streak = 0
                        if self.praise_streak == 0:
                            feedback_message = generate_message_using_llm(
                                "The child attempted to speak English."
                                "The child is a 7-8-year-old Dutch speaker learning English. "
                                "Since they are doing well, provide a short, positive praise message in English. "
                                "Generate only one sentence."
                            )
                            yield say_animated(self.session, feedback_message, language="en")
                        self.praise_streak += 1
                    else:
                        self.praise_streak = 0
                    
                        feedback_message = generate_message_using_llm(
                            "The child attempted to speak English, but there's room for improvement. "
                            "They are a 7-8-year-old Dutch speaker learning English. "
                            "Encourage them, let them know they can improve, and mention you will help them. "
                            "Keep your response short, simple, and supportive, in English."
                            "Generate only one sentence."
                        )
                        yield say_animated(self.session, feedback_message, language="en")

                        example_sentence = self.language_assistant.get_example_phrase(user_input)
                        user_input = yield self.validate_repeated_input(example_sentence)

                return user_input

            yield say_animated(self.session, silence_message, language)

    @inlineCallbacks
    def validate_repeated_input(self, example_sentence: str) -> Generator[Optional[str], None, str]:
        """
        Prompts the user to repeat a given sentence and waits for their input.
        If the input is detected, it returns the repeated sentence. If no
        input is detected after several attempts, the function continues
        prompting the user to repeat the sentence until it is recognized.

        Args:
            example_sentence (str): The sentence that the user is asked to
            repeat.

        Returns:
            Optional[str]: The sentence that the user has repeated.

        Yields:
            Generator[Optional[str], None, str]: Yields a string with the
            recognized sentence when detected.
        """
        yield say_animated(self.session, f"Now, try saying: '{example_sentence}'.", language="en")

        while True:
            repeated_input = yield self.recognize_speech()

            if repeated_input:
                return repeated_input

            silence_message = f"I couldn't hear you. Please try saying: '{example_sentence}'."
            yield say_animated(self.session, silence_message, language="en")

    @inlineCallbacks
    def recognize_speech(self) -> Generator[None, None, Optional[str]]:
        recorded_audio_path = yield self.processor.record_audio()

        if recorded_audio_path:
            transcription_result = yield self.processor.process_audio(recorded_audio_path)
            if transcription_result:
                print("Transcription:", transcription_result)
                if os.path.exists(recorded_audio_path):
                    os.remove(recorded_audio_path)
                return transcription_result
            
            if os.path.exists(recorded_audio_path):
                os.remove(recorded_audio_path)

        return None
