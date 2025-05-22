"""
File:     language_assistant.py
Authors:  Özde Pilli (s5257018) and Adna Kapidžić (s5256100)
Group:    5

Description:
    Handles language evaluation and feedback for speech input. Determines
    English usage percentage and provides appropriate (feedback) response.

    Note:
        - English word lists are from https://github.com/dwyl/english-words?tab=readme-ov-file
"""

from typing import List
import os
import re
import string
from src.utils import generate_message_using_llm


class LanguageAssistant:
    """
    Assists with evaluating user input and providing feedback.
    """

    def __init__(self, session, english_word_files: List | None = None):
        self.session = session

        if english_word_files is None:
            base_path = os.path.dirname(os.path.realpath(__file__))
            english_word_files = [
                os.path.join(base_path, "english_word_lists/words_alpha.txt"),
                os.path.join(base_path, "english_word_lists/words.txt"),
            ]

        self.english_words = self.load_words(english_word_files)

    def load_words(self, word_files: List[str]) -> set:
        """
        Loads words from multiple text files into a set.

        Args:
            word_files (List[str]): A list of file paths (strings) from which
            words will be loaded.

        Returns:
            set: A set of words from all the files. Duplicates are
            automatically removed since a set is used.

        Raises:
            FileNotFoundError: If any of the specified files cannot be found.
        """
        words = set()
        for file in word_files:
            try:
                with open(file, encoding="utf-8") as f:
                    words.update(f.read().splitlines())
            except FileNotFoundError:
                print(f"Error: File {file} not found.")
                raise
        return words

    def calculate_language_usage(self, text: str) -> float:
        """
        Calculates the percentage of English words in a given text.

        Args:
            text (str): User input text.

        Returns:
            float: Percentage of words in English.
        """
        words_in_text = [re.sub(f'^[{string.punctuation}]+|[{string.punctuation}]+$', '', word) for word in text.lower().split()]
        english_count = sum(1 for word in words_in_text if word in self.english_words)
        return (english_count / len(words_in_text)) * 100 if words_in_text else 0

    def get_example_phrase(self, user_input: str) -> str:
        """
        Generates a corrected example sentence for the user based on their
        input.

        Args:
            user_input (str): The spoken input from the user.

        Returns:
            str: A corrected sentence.
        """
        prompt = (
            f"Rephrase the non-English words in this text {user_input} so that a correct English text is formed, "
            "keeping the already English words as much as possible intact, and keeping the language simple. "
            "Only return the improved text."
        )
        return generate_message_using_llm(prompt)
