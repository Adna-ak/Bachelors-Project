"""
File:     keywords_handler.py
Authors:  Özde Pilli (s5257018) and Adna Kapidžić (s5256100)
Group:    5

Description:
    This module contains the KeywordsHandler class, which is responsible for
    handling user inputs related to quitting the game and requesting hints. It
    interacts with an LLM and uses the LLMGameHelper to generate hints and
    determine whether the user wants to quit the game.
"""

from typing import Generator, Optional
from twisted.internet.defer import inlineCallbacks
from src.robot_movements.say_animated import say_animated
from src.utils import generate_message_using_llm
from src.taboo_game.llm_interface import LLMGameHelper


class KeywordsHandler:
    """
    Handles user input related to quitting the game and requesting hints during
    the gameplay. This class interacts with the LLMGameHelper to generate
    responses based on the user's input.
    """

    def __init__(self, session):
        self.session = session
        self.game_helper = LLMGameHelper()

    @inlineCallbacks
    def check_quit_keywords(self, user_input: str) -> Generator[Optional[str], None, None]:
        """
        Checks if the user wants to quit the game by analyzing their input.

        Args:
            user_input (str): User's input to analyze.

        Yields:
            Generator[Optional[str], None, None]: Handles interactions related
            to quitting the game.
        """
        from src.speech_processing.speech_session import SpeechRecognitionSession  # Delayed import
        speech_recognition = SpeechRecognitionSession(self.session)

        prompt = (
            f"The user said: '{user_input}'. Determine if they want to quit the game by recognizing quit/stop words "
            "like 'bye', 'goodbye', 'stop', 'stoppen', 'doei', 'tot ziens', et cetera. Respond with only 'yes' or 'no'."
        )
        response = generate_message_using_llm(prompt)

        if response == "yes":
            message = "Weet je zeker dat je het spel wilt stoppen?"
            repeat_message = "Weet je zeker dat je het spel wilt stoppen? Antwoord alleen met 'ja' of 'nee'."
            stop_playing = yield speech_recognition.validate_user_input(message, repeat_message, language="nl", get_feedback=False)

            if self.game_helper.recognize_yes_or_no(stop_playing) == "no":
                return

            message = "Ik vond het leuk om met je te spelen, tot de volgende keer!"
            yield say_animated(self.session, message, language="nl")
            self.session.leave()

    # SIMILAR TO ASSIGNMENTS 1 AND 2
    @inlineCallbacks
    def check_hint_keywords(self, user_input: str, secret_word: str) -> Generator[Optional[str], None, None]:
        """
        Checks if the user is requesting a hint and provides one if needed.

        Args:
            user_input (str): User's input to analyze.
            secret_word (str): Secret word used to generate a hint.

        Yields:
            Generator[Optional[str], None, None]: Handles interactions related
            to hint requests.
        """
        prompt = (
            f"The user said: '{user_input}'. Determine if they are asking for a hint "
            "by recognizing 'hint', 'help', et cetera. Respond with only 'yes' or 'no'."
        )
        response = generate_message_using_llm(prompt)

        if response == "yes":
            message = "I will give you a hint!"
            yield say_animated(self.session, message, language="en")
            hint = self.game_helper.generate_hint(secret_word)
            yield say_animated(self.session, hint, language="en")

        return response
