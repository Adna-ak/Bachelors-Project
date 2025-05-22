"""
File:     utils.py
Authors:  Özde Pilli (s5257018) and Adna Kapidžić (s5256100)
Group:    5

Description:
    This module provides functionality to generate messages using OpenAI's
    GPT-3.5. It takes a prompt as input and returns a generated response in
    lowercase, ensuring that no inappropriate or offensive content is included.
    The script checks for profanity using Sightengine and regenerates the
    response if needed. The API key must be set in the environment variables
    for the script to work.
"""

import os
import json
import openai
import requests
from langdetect import detect

API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("OPENAI_API_KEY is not set. Please set it in your environment variables.")

client = openai.Client(api_key=API_KEY)


def check_profanity(text: str, lang: str, timeout: int = 10) -> dict:
    """
    Checks the given text for profanity using the Sightengine API.
    This approach is based on the Sightengine Profanity Detection API, which
    can identify offensive language, including hate speech, offensive words,
    and inappropriate content.

    For more details on the API and its rules, visit:
    https://sightengine.com/docs/profanity-detection-hate-offensive-text-moderation

    Args:
        text (str): The text to check for profanity.
        lang (str): The language of the text.
        timeout (int): Timeout for the request in seconds. Default is 10
            seconds.

    Returns:
        dict: The API response in JSON format, containing information on
        detected profanity.
    """
    data = {'text': text, 'mode': 'rules', 'lang': lang}
    headers = {'Authorization': API_KEY}

    try:
        r = requests.post('https://api.sightengine.com/1.0/text/check.json', data=data, headers=headers, timeout=timeout)
        return json.loads(r.text)
    except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
        print(f"Request failed: {e}")
        return {}


def generate_message_using_llm(original_prompt: str) -> str:
    """
    Generates a message based on a given prompt using OpenAI's GPT-3.5 and
    ensures no profanity is included. Also ensures the language is safe
    and appropriate for children.

    Args:
        original_prompt (str): The initial prompt to send to the OpenAI API.

    Returns:
        str: A generated response from the OpenAI API, in lowercase, with no
        profanity.

    Raises:
        RuntimeError: If the LLM response is empty.
    """
    prompt = original_prompt
    avoided_words = []
    system_prompt = (
        "You are a friendly, educational robot speaking to children aged 7-8. "
        "Keep your language fun, safe, simple, and never use any inappropriate or scary content."
    )

    while True:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )

        if not completion.choices:
            raise RuntimeError("LLM response is empty.")

        response = completion.choices[0].message.content.strip()
        language = detect(response)
        profanity = check_profanity(response, lang=language if language in ["en", "nl"] else "en")

        if profanity and profanity.get("profanity", {}).get("matches"):
            print("Profanity detected. Regenerating the message...")
            matches = profanity["profanity"]["matches"]
            new_words = [match["match"] for match in matches if match["match"] not in avoided_words]

            if new_words:
                avoided_words.extend(new_words)
                avoided_words_str = ", ".join(avoided_words)
                prompt = original_prompt + f" Do not use the word(s): '{avoided_words_str}'."

        else:
            return response.lower()
