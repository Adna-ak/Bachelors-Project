from src.utils import generate_message_using_llm


class LLMGameHelper:
    def __init__(self):
        self.standard_prompt_addition = (
            "Use simple and clear language that a 12-year-old native Dutch speaker "
            "learning English as a second language can understand. "
            "Approach them like a friend."
        )

    def recognize_yes_or_no(self, user_input: str) -> str:
        """
        Determines if the user's response is 'yes' or 'no'.

        Args:
            user_input (str): User's input.

        Returns:
            str: Either 'yes' or 'no' based on the input.
        """
        prompt = (
            f"The user has said the following: '{user_input}'. Your task is to determine whether "
            "they said 'yes' or 'no'. Respond with only 'yes' or 'no' based on the input. "
            "If unclear, return the most likely option."
        )
        return generate_message_using_llm(prompt)

    def process_user_question(self, secret_word: str, question: str) -> str:
        """
        Processes the user's question and returns a short answer, explaining
        whether the question is related to the secret word without revealing
        the secret word.

        Args:
            secret_word (str): Secret word in the game.
            question (str): User's question.

        Returns:
            str: Short answer explaining if the question is related to the secret
            word without revealing it.
        """
        prompt = (
            f"The user has asked the following question: '{question}' about the secret word: '{secret_word}'. "
            "Answer to their question with a short response. "
            "Do not mention the secret word, including any abbreviations or parts of the word. "
            "Your explanation should help the user understand more about the secret word without telling them what it is. "
            "Generate max 15 words."
        )
        # Even though we specified to not mention the secret word, the LLM might still do it in some cases
        return generate_message_using_llm(prompt + " " + self.standard_prompt_addition)

    def generate_hint(self, secret_word: str) -> str:
        prompt = (
            f"The user is struggling to guess the secret word, which is {secret_word}. "
            "Generate a helpful hint without revealing the secret word, "
            "including abbreviations or any part of the word. "
            "Keep the hint to one or two sentences and in English."
        )
        return generate_message_using_llm(prompt + " " + self.standard_prompt_addition)

    def determine_question_or_guess(self, user_input: str, secret_word: str) -> str:
        """
        Determines if the user's input is a question or a guess about the
        secret word.

        Args:
            user_input (str): User's input.
            secret_word (str): Secret word in the game.

        Returns:
            str: 'question' or 'guess' based on the user's input.
        """
        prompt = (
            f"The user has said: '{user_input}'. Determine if this is a yes/no question about the secret word "
            f"or a guess of the secret word: {secret_word}. A guess could start with 'I think...', 'The word is...' "
            "A question usually starts with a verb. Respond with only 'question' or 'guess'."
        )
        return generate_message_using_llm(prompt)

    def check_if_correct_guess(self, secret_word: str, guess: str) -> str:
        """
        Checks if the player's guess matches the secret word and returns a
        response.

        Args:
            secret_word (str): Secret word in the game.
            guess (str): Word guessed by the player.

        Returns:
            str: Either 'correct' or 'incorrect'.
        """
        prompt = (
            f"The user guessed: '{guess}'. The correct secret word is: '{secret_word}'. "
            "Respond with only 'correct' or 'incorrect'."
        )
        return generate_message_using_llm(prompt)

    def generate_secret_word_explanation(self, secret_word: str) -> str:
        """
        Generates a short one-sentence explanation of the secret word.
        """
        prompt = (
            f"Explain the word '{secret_word}' in one short sentence."
        )
        return generate_message_using_llm(prompt + " " + self.standard_prompt_addition)
