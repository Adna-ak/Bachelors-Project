"""
File:     english_speech_rate.py
Authors:  Özde Pilli (s5257018) and Adna Kapidžić (s5256100)
Group:    5

Description:
    I wrote down the explanation messages from our video takes and their times
    to calculate the speech rate.
"""

TEXT_1 = "Alright. Imagine you are in a word guessing party. One player, you, tries to guess the word that the other player, host, is thinking of, but the host can't say the word directly. Use your detective skills to ask yes or no questions to uncover the secret word. Let's see how many words you can guess correctly before saying goodbye or stop. Let's start the fun word adventure."
num_words_1 = len(TEXT_1.split())
TIME_1 = 24  # seconds
speech_rate_1 = TIME_1 / num_words_1

TEXT_2 = "Ready to have some fun with the WOW game? I'll think of a secret word and you'll guess it by asking yes or no questions. I can only say yes, no, or give you short hints without using any taboo words. Let's get started and see how many words you can guess."
num_words_2 = len(TEXT_2.split())
TIME_2 = 16  # seconds
speech_rate_2 = TIME_2 / num_words_2

TEXT_3 = "Let's play the WOW game. I will think of a word and you'll try to guess it by asking yes or no questions. I can only say yes, no, or give short hints. Be careful not to use any taboo words when guessing. Ready? Let's have some fun guessing words."
num_words_3 = len(TEXT_3.split())
TIME_3 = 18  # seconds
speech_rate_3 = TIME_3 / num_words_3

average_speech_rate = (speech_rate_1 + speech_rate_2 + speech_rate_3) / 3  # = 0.340211161387632
print("Average speech rate (seconds per word):", average_speech_rate)
