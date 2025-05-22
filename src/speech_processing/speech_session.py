"""
File:     speech_session.py
Authors:  Özde Pilli (s5257018) and Adna Kapidžić (s5256100)
Group:    5

Description:
    This module defines the SpeechRecognitionSession class, responsible for
    handling speech recognition, user interaction, and providing feedback.
    It ensures continuous prompting until valid speech is detected.
"""

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

    def __init__(self, session):
        self.session = session
        self.processor = SpeechToText(device_index=1)  # Index for Sennheiser microphone (on my laptop), which we tested
        self.keywords_handler = KeywordsHandler(session)
        self.praise_streak = 0

    # SIMILAR TO ASSIGNMENTS 1 AND 2
    @inlineCallbacks
    def check_silence(self, silence_count: int, max_silence_count: int = 3) -> Generator[Optional[str], None, int]:
        """
        Checks if the user has been silent for a certain number of consecutive
        attempts. If silence is detected, it will prompt the user with a
        question asking if they are still present. If there is no response,
        the game will end.

        Args:
            silence_count (int): Number of consecutive silent attempts.
            max_silence_count (int, optional): Threshold for silence detection.
                Defaults to 3.

        Returns:
            int: Updated silence count.

        Yields:
            Generator[Optional[str], None, int]: Handles speech recognition and
            speaking prompts.
        """
        if silence_count == max_silence_count:
            message = "Hallo, ben je er nog?"
            yield say_animated(self.session, message, language="nl")
            user_input = yield self.recognize_speech()

            if user_input is None:
                message = (
                    "Ik zal ervanuitgaan dat je er niet meer bent. Ik zal het spel beëindigen. "
                    "Ik vond het leuk om met je te spelen, tot de volgende keer!"
                )
                yield say_animated(self.session, message, language="nl")
                self.session.leave()

            silence_count = 0
            message = "Oh leuk, je bent er nog!"
            yield say_animated(self.session, message, language="nl")

        return silence_count

    @inlineCallbacks
    def validate_user_input(
        self, prompt_message: str, silence_message: str, language: str = "en", get_feedback: bool = True
    ) -> Generator[Optional[str], None, str]:
        """
        Continuously prompts the user for input until valid speech is detected.
        Evaluates English usage and provides feedback.

        Args:
            prompt_message (str): Initial message prompting the user for input.
            silence_message (str): Message repeated if no input is detected.
            language (str): The language of the speech (default is English).
            get_feedback (bool): Whether to evaluate and give feedback on the
                user input. Defaults to True.

        Returns:
            str: Validated user input.

        Yields:
            Generator[Optional[str], None, str]: Yields the recognized user
            input when detected.
        """
        silence_count = 0
        yield say_animated(self.session, prompt_message, language)

        if get_feedback:
            self.language_assistant = LanguageAssistant(self.session)

        while True:
            user_input = yield self.recognize_speech()

            if user_input:
                yield self.keywords_handler.check_quit_keywords(user_input)
                # Still gives feedback after detecting quit keyword, idk why
                if get_feedback:
                    percent_english = self.language_assistant.calculate_language_usage(user_input)
                    print("Percentage of English:", percent_english)
                    if percent_english >= 70:  # Keeping in mind that this is for kids, 70% is okay
                        if self.praise_streak == 3:
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

            silence_count += 1
            silence_count = yield self.check_silence(silence_count)
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
        silence_count = 0
        yield say_animated(self.session, f"Now, try saying: '{example_sentence}'.", language="en")

        while True:
            repeated_input = yield self.recognize_speech()

            if repeated_input:
                return repeated_input

            silence_count += 1
            silence_count = yield self.check_silence(silence_count)
            silence_message = f"I couldn't hear you. Please try saying: '{example_sentence}'."
            yield say_animated(self.session, silence_message, language="en")

    @inlineCallbacks
    def recognize_speech(self) -> Generator[None, None, Optional[str]]:
        """
        Records audio from the user, processes the speech input, and returns
        the transcribed text if successful.

        Returns:
            Optional[str]: The transcribed text from the recorded speech, or
            None if no valid transcription is available.

        Yields:
            Generator[None, None, Optional[str]]: Yields the result
            asynchronously after processing the audio.
        """
        recorded_audio_path = yield self.processor.record_audio()

        if recorded_audio_path:
            transcription_result = yield self.processor.process_audio(self.session, recorded_audio_path)
            if transcription_result and 'text' in transcription_result:
                print("Transcription:", transcription_result['text'])
                return transcription_result['text']
        return None
