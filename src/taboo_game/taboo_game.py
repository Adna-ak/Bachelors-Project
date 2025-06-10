import time
from typing import Generator, Optional
from twisted.internet.defer import inlineCallbacks, returnValue
from src.robot_movements.say_animated import say_animated
from src.speech_processing.speech_session import SpeechRecognitionSession
from src.taboo_game.keywords_handler import KeywordsHandler
from src.taboo_game.llm_interface import LLMGameHelper


class TabooGame:
    def __init__(self, session, version):
        self.session = session
        self.version = version
        self.keywords_handler = KeywordsHandler(session)
        self.game_helper = LLMGameHelper()
        self.speech_recognition_session = SpeechRecognitionSession(self.session, self.version)
        self.secret_word = None

    @inlineCallbacks
    def offer_hint(self) -> None | Generator[Optional[str], None, None]:
        if self.version != "experiment":
            return

        message = "Would you like a hint?"
        repeat_message = "Would you like a hint? Respond with only 'yes' or 'no'."
        answer = yield self.speech_recognition_session.validate_user_input(message, repeat_message, language="en")

        if self.game_helper.recognize_yes_or_no(answer) == "yes":
            self.round_data["hints_given"] += 1
            hint = self.game_helper.generate_hint(self.secret_word)
            yield say_animated(self.session, hint, language="en")

    @inlineCallbacks
    def robot_is_host(
        self,
        max_questions_answered_no: int = 3,
        max_wrong_guesses: int = 3
    ) -> Generator[Optional[str], None, None]:
        questions_answered_no = 0
        incorrect_guesses = 0

        message = "I have thought of a word. Try to guess it."
        repeat_message = message

        start_time = time.time()
        time_limit_seconds = 2 * 60  # 2 minutes

        self.round_data = {
            "guesses": 0,
            "incorrect_guesses": 0,
            "guessed_word": False,
            "questions": 0,
            "questions_answered_no": 0,
            "hints_given": 0,
            "gave_up": False
        }

        while True:
            if time.time() - start_time >= time_limit_seconds:
                word_explanation = self.game_helper.generate_secret_word_explanation(self.secret_word)
                message = f"Time's up! The secret word is {self.secret_word}. {word_explanation}"
                yield say_animated(self.session, message, language="en")
                break

            user_input = yield self.speech_recognition_session.validate_user_input(message, repeat_message, language="en")

            if self.version == "experiment":
                hint_given = yield self.keywords_handler.check_hint_keywords(user_input, self.secret_word)
                while hint_given == "yes":
                    self.round_data["hints_given"] += 1
                    message = "Try to guess the word using the hint I gave you."
                    user_input = yield self.speech_recognition_session.validate_user_input("", message, language="en")
                    hint_given = yield self.keywords_handler.check_hint_keywords(user_input, self.secret_word)

            input_type = self.game_helper.determine_question_or_guess(user_input, self.secret_word)

            if input_type == "question":
                self.round_data["questions"] += 1
                response = self.game_helper.process_user_question(self.secret_word, user_input)
                yield say_animated(self.session, response, language="en")

                if self.version == "experiment":
                    if self.game_helper.recognize_yes_or_no(response) == "no":
                        self.round_data["questions_answered_no"] += 1
                        questions_answered_no += 1

                    if questions_answered_no == max_questions_answered_no:
                        yield self.offer_hint()
                        questions_answered_no = 0

            else:
                # Input type is a guess
                self.round_data["guesses"] += 1
                result = self.game_helper.check_if_correct_guess(self.secret_word, user_input)

                if result == "correct":
                    self.round_data["guessed_word"] = True
                    message = "You got it! Well done!"
                    yield say_animated(self.session, message, language="en")
                    break

                incorrect_guesses += 1
                self.round_data["incorrect_guesses"] += 1

                if self.version == "experiment":
                    if incorrect_guesses == max_wrong_guesses:
                        yield self.offer_hint()
                        incorrect_guesses = 0

                elif incorrect_guesses == 4:
                    message = "Do you want me to tell you the secret word?"
                    repeat_message = "Do you want me to tell you the secret word? Say 'yes' or 'no'."
                    tell_secret_word = yield self.speech_recognition_session.validate_user_input(message, repeat_message, language="en")

                    if self.game_helper.recognize_yes_or_no(tell_secret_word) == "yes":
                        self.round_data["gave_up"] = True
                        word_explanation = self.game_helper.generate_secret_word_explanation(self.secret_word)
                        message = f"The secret word is {self.secret_word}. {word_explanation}"
                        yield say_animated(self.session, message, language="en")
                        break

                else:
                    message = "Not quite! Keep guessing."
                    yield say_animated(self.session, message, language="en")

            message = ""
            repeat_message = "Ask me a question or guess the word."

        returnValue(self.round_data)
