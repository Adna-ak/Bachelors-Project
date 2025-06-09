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
