"""
File:     stress_word_analyzer.py
Authors:  Özde Pilli (s5257018) and Adna Kapidžić (s5256100)
Group:    5

Description:
    This module provides functionality to analyze and identify stress words in
    a given text. It utilizes both an LLM-based approach and part-of-speech
    (POS) tagging to determine which words should be emphasized with small
    (beat) gestures.
"""

from typing import List, Tuple
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
import spacy
from src.utils import generate_message_using_llm


class StressWordAnalyzer:
    """
    This class uses both an LLM-based approach and part-of-speech (POS)
    tagging to determine which words should be emphasized with small gestures.
    It ensures spacing rules are followed and prioritizes iconic gestures.
    """

    def __init__(self, text: str, language: str = "en"):
        self.text = text
        self.language = language
        self.words = RegexpTokenizer(r"\b\w+(?:'\w+)?\b").tokenize(text.lower())
        self.stop_words_en = set(stopwords.words('english'))
        self.stop_words_nl = set(stopwords.words('dutch'))
        self.stop_words = self.stop_words_en.union(self.stop_words_nl)

    # SIMILAR TO ASSIGNMENTS 1 AND 2
    def get_llm_stress_words(self) -> List[Tuple[int, str]]:
        """
        Identifies important words in the text using an LLM that should be
        emphasized with small gestures (arm or head movement).

        Returns:
            List[Tuple[int, str]]: A list of tuples, each containing the index
            of the word in the text and the corresponding word.
        """
        print("Entering get_llm_stress_words function...")
        prompt = (
            f"Identify the MOST IMPORTANT words that should be emphasized with a small arm or head movement in this text: {self.text}. "
            f"Select at most 1 word per 9 words. Focus on words that carry key meaning or emotion. "
            f"Do NOT emphasize common nouns, generic verbs, or function words. "
            f"Return only a comma-separated list of their positions in the text starting from 0."
        )
        response = generate_message_using_llm(prompt)
        response = RegexpTokenizer(r"\b\w+(?:'\w+)?\b").tokenize(response.lower().split('\n')[0])
        # Cleaning up the response: removing unwanted characters like punctuation and filtering out emojis
        # And if LLM's response includes additional lines (e.g., "1, 2\n hi, i'm"), it is handled here
        print(f"LLM response: {response}")

        try:
            stress_word_positions = [int(pos) for pos in response]
        except ValueError:
            print("Response contains words instead of positions, extracting word indices...")
            # In case LLM returns list of words (happens sometimes even though we specified it not to)

            stress_word_positions = []
            for word in response:
                for i, w in enumerate(self.words):
                    if w == word:
                        stress_word_positions.append(i)
                        break

        valid_positions = [index for index in stress_word_positions if 0 <= index < len(self.words)]
        stress_words = [(index, self.words[index]) for index in valid_positions]
        stress_words.sort(key=lambda x: x[0])

        print(f"Identified stress words: {stress_words}")
        print("Exiting get_llm_stress_words function...")
        return stress_words

    def get_pos_tag_stress_words(self) -> List[Tuple[int, str]]:
        """
        Identifies important stress words in the text based on part-of-speech
        (POS) tagging. It processes each word in the text, tags it with its
        POS tag, and checks if it is a noun, verb, adjective, or adverb.
        If the word is not a stop word, it is considered a stress word.

        Returns:
            List[Tuple[int, str]]: A list of tuples containing the index and
            the corresponding stress word.
        """
        print("Entering get_pos_tag_stress_words function...")

        if self.language == "nl":
            nlp_model = spacy.load("nl_core_news_sm")
        else:
            nlp_model = spacy.load("en_core_web_sm")

        stress_words = []

        for index, word in enumerate(self.words):
            doc = nlp_model(word)
            token = doc[0]  # This model causes inaccuracies for contractions, but our previous approach was not suitable for Dutch text

            if token.pos_ in ('NOUN', 'VERB', 'ADJ', 'ADV') and token.text.lower() not in self.stop_words:
                print(f"Adding word '{token.text}' at index {index} as a stress word.")
                stress_words.append((index, token.text))

        print(f"Identified stress words: {stress_words}")
        print("Exiting get_pos_tag_stress_words function...")
        return stress_words

    # SIMILAR TO ASSIGNMENTS 1 AND 2
    def get_stress_words(self) -> List[Tuple[int, str]]:
        """
        Identifies important words in a text using both LLM-based analysis and
        part-of-speech (POS) tagging. The function alternates between selecting
        a stress word chosen by the LLM or by POS tagging. It also ensures that
        iconic gestures get priority, so if an iconic word is detected too
        close to a selected stress word, the stress word will be deselected.

        Returns:
            List[Tuple[int, str]]: A list of tuples, each containing the index
            of the word in the text and the corresponding word.

        Notes:
            People usually emphasize nouns, verbs, adverbs, and adjectives with
            small head and/or arm movements. However, we also emphasize
            meaningful or emotional words, which depend on personal experience.
            As there is no rule for when we emphasize words with small
            movements, we decided to introduce some randomness by incorporating
            the LLM in addition to POS tagging.
        """
        print("Entering get_stress_words function...")

        stress_words_llm = self.get_llm_stress_words()
        stress_words_pos = self.get_pos_tag_stress_words()

        stress_words = []
        gap = 7  # To fine-tune movement
        llm_index = 0
        pos_index = 0
        use_llm = False
        last_position = None

        iconic_words = ["hello", "hi", "hey", "goodbye", "bye", "welcome",
                        "hallo", "dag", "hai", "hoi", "hé", "doei", "doeg", "welkom",
                        "i", "me", "my", "mine", "myself", "i'm", "i'll", "i've",
                        "ik", "mij", "mijn", "mezelf", "mijzelf",
                        "you", "your", "yours", "yourself", "you're", "you'll", "you've",
                        "jij", "je", "jou", "jouw", "jezelf", "u", "uw", "uzelf", "jullie"]

        print("Entering loop in get_stress_words function...")
        while llm_index < len(stress_words_llm) or pos_index < len(stress_words_pos):
            if use_llm and llm_index < len(stress_words_llm):
                llm_word_index, llm_word = stress_words_llm[llm_index]
                if llm_word.lower() in iconic_words:
                    last_position = llm_word_index
                    llm_index += 1
                    if stress_words and abs(llm_index - stress_words[-1][0]) < gap:
                        removed_word = stress_words.pop()
                        print(f"Removed '{removed_word[1]}' at index {removed_word[0]} due to proximity to iconic word '{llm_word}' at index {llm_word_index}, which takes priority.")
                    continue
                if last_position is not None and abs(llm_word_index - last_position) < gap:
                    print(f"Skipping LLM word '{llm_word}' at index {llm_word_index} due to gap rule.")
                    llm_index += 1
                    continue
                print(f"Selected LLM stress word '{llm_word}' at index {llm_word_index}")
                stress_words.append((llm_word_index, llm_word))
                last_position = llm_word_index
                llm_index += 1
                use_llm = False

            elif not use_llm and pos_index < len(stress_words_pos):
                pos_word_index, pos_word = stress_words_pos[pos_index]
                if pos_word.lower() in iconic_words:
                    last_position = pos_word_index
                    pos_index += 1
                    if stress_words and abs(pos_index - stress_words[-1][0]) < gap:
                        removed_word = stress_words.pop()
                        print(f"Removed '{removed_word[1]}' at index {removed_word[0]} due to proximity to iconic word '{pos_word}' at index {pos_word_index}, which takes priority.")
                    continue
                if last_position is not None and abs(pos_word_index - last_position) < gap:
                    print(f"Skipping POS word '{pos_word}' at index {pos_word_index} due to gap rule.")
                    pos_index += 1
                    continue
                print(f"Selected POS stress word '{pos_word}' at index {pos_word_index}")
                stress_words.append((pos_word_index, pos_word))
                last_position = pos_word_index
                pos_index += 1
                use_llm = True

            if llm_index == len(stress_words_llm):
                use_llm = False

            if pos_index == len(stress_words_pos):
                use_llm = True

        seen = set()
        stress_words = [item for item in stress_words if item not in seen and not seen.add(item)]
        stress_words.sort(key=lambda x: x[0])

        print("Final stress words identified:", stress_words)
        print("Exiting get_stress_words function...")
        return stress_words
