"""
File:     taboo_game.py
Authors:  Özde Pilli (s5257018) and Adna Kapidžić (s5256100)
Group:    5

Description:
    Module for running the Taboo game where a robot guides the user through
    guessing a secret word. The game involves the robot acting as a host,
    providing hints, answering user questions, and generating songs. The game
    is designed to help young learners practice English by interacting with the
    robot and guessing the secret word based on yes/no questions and hints.
"""

from typing import Generator, Optional
import random
from twisted.internet.defer import inlineCallbacks
from src.robot_movements.say_animated import say_animated
from src.speech_processing.speech_session import SpeechRecognitionSession
from src.taboo_game.keywords_handler import KeywordsHandler
from src.taboo_game.llm_interface import LLMGameHelper


class TabooGame:
    """
    Handles the flow of the Taboo game where the user must guess a secret
    word based on hints and responses to their questions. The class manages
    the main game loop, user interactions, and communication with other modules
    for dynamic message generation, hint validation, and song creation.
    """

    def __init__(self, session, version: str = "normal"):
        self.session = session
        self.version = version
        self.keywords_handler = KeywordsHandler(session)
        self.game_helper = LLMGameHelper()
        self.speech_recognition_session = SpeechRecognitionSession(self.session)
        self.secret_word = None
        self.skip_intro = False
        self.used_secret_words = []
        self.secret_words_to_repeat = []

    @inlineCallbacks
    def offer_hint(self) -> Generator[Optional[str], None, None]:
        """
        Offers the user a hint and provides one if they accept.

        Yields:
            Generator[Optional[str], None, None]: Handles user interaction
            related to offering hints.
        """
        message = "Would you like a hint?"
        repeat_message = "Would you like a hint? Respond with only 'yes' or 'no'."
        answer = yield self.speech_recognition_session.validate_user_input(message, repeat_message, language="en")

        if self.game_helper.recognize_yes_or_no(answer) == "yes":
            if self.version == "study words":
                all_hint_properties = list(STUDY_WORDS[self.secret_word])
                hint_property = random.choice(all_hint_properties)
                hint = self.game_helper.generate_hint(self.secret_word, hint_property)
            else:
                hint = self.game_helper.generate_hint(self.secret_word)
            yield say_animated(self.session, hint, language="en")

    # SIMILAR TO ASSIGNMENTS 1 AND 2
    @inlineCallbacks
    def robot_is_host(
        self,
        max_questions_answered_no: int = 3,
        max_wrong_guesses: int = 3
    ) -> Generator[Optional[str], None, None]:
        """
        Runs the main game loop where the robot acts as the host, guiding the
        user through guessing the secret word.

        Args:
            max_questions_answered_no (int, optional): Maximum number of times
                the robot can say 'no' to a question before offering a hint.
                Defaults to 3.
            max_wrong_guesses (int, optional): Maximum number of incorrect
                guesses before offering a hint. Defaults to 3.

        Yields:
            Generator[Optional[str], None, None]: Handles user interaction for
            guessing the word and responding to questions.
        """
        questions_answered_no = 0
        total_guesses = 0
        incorrect_guesses = 0
        self.secret_word = self.get_secret_word()

        message = "I have thought of a word. Try to guess it."
        repeat_message = message

        while True:
            user_input = yield self.speech_recognition_session.validate_user_input(message, repeat_message, language="en")
            hint_given = yield self.keywords_handler.check_hint_keywords(user_input, self.secret_word)

            while hint_given == "yes":
                message = "Try to guess the word using the hint I gave you."
                user_input = yield self.speech_recognition_session.validate_user_input("", message, language="en")
                hint_given = yield self.keywords_handler.check_hint_keywords(user_input, self.secret_word)

            input_type = self.game_helper.determine_question_or_guess(user_input, self.secret_word)
            print("Sentence is:", input_type)

            if input_type == "question":
                response = self.game_helper.process_user_question(self.secret_word, user_input)
                yield say_animated(self.session, response, language="en")

                if self.game_helper.recognize_yes_or_no(response) == "no":
                    questions_answered_no += 1

                if questions_answered_no == max_questions_answered_no:
                    yield self.offer_hint()
                    questions_answered_no = 0

            else:
                # Input type is a guess
                total_guesses += 1
                result = self.game_helper.check_if_correct_guess(self.secret_word, user_input)

                if result == "correct":
                    if self.secret_word in self.secret_words_to_repeat:
                        self.secret_words_to_repeat.remove(self.secret_word)
                    message = "You got it! Well done!"
                    yield say_animated(self.session, message, language="en")
                    break

                incorrect_guesses += 1
                if incorrect_guesses == max_wrong_guesses:
                    yield self.offer_hint()
                    incorrect_guesses = 0

                elif total_guesses == 5:
                    message = "Do you want me to tell you the secret word?"
                    repeat_message = "Do you want me to tell you the secret word? Say 'yes' or 'no'."
                    tell_secret_word = yield self.speech_recognition_session.validate_user_input(message, repeat_message, language="en")

                    if self.game_helper.recognize_yes_or_no(tell_secret_word) == "yes":
                        if self.secret_word not in self.secret_words_to_repeat:
                            self.secret_words_to_repeat.append(self.secret_word)
                        message = (
                            f"The secret word is {self.secret_word}. "
                            "Let's play again."
                        )
                        yield say_animated(self.session, message, language="en")
                        break

                else:
                    message = "Not quite! Keep guessing."
                    yield say_animated(self.session, message, language="en")

            message = ""
            repeat_message = "Ask me a question or guess the word."

        yield self.play_again()

    # SIMILAR TO ASSIGNMENTS 1 AND 2
    @inlineCallbacks
    def play_taboo(self) -> Generator[Optional[str], None, None]:
        """
        Starts the Taboo game, providing an introduction and explanation if
        needed.

        Yields:
            Generator[Optional[str], None, None]: Handles the game start
            process.
        """
        if not self.skip_intro:
            welcome_message = self.game_helper.generate_welcome_message()
            explanation_message = self.game_helper.generate_explanation_message()

            yield say_animated(self.session, welcome_message, language="nl")
            yield say_animated(self.session, explanation_message, language="nl")

        yield self.robot_is_host()
