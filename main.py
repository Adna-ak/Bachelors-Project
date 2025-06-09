import json
import os
from typing import Generator
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.component import Component, run
import nltk
from src.taboo_game.taboo_game import TabooGame
from prepost_test import PrePostTest

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    print("Stopwords not found, downloading...")
    nltk.download('stopwords')

PARTICIPANT_FILE = "participants.json"

# === CONFIGURE THESE HERE ===
GAME_VERSION = "experiment"   # or "control"
PARTICIPANT_NUM = "1"         # string
PARTICIPANT_NAME = "Alice Johnson"  # string

def load_participants():
    if os.path.exists(PARTICIPANT_FILE):
        with open(PARTICIPANT_FILE, "r") as f:
            return json.load(f)
    else:
        return {}

def save_participants(data):
    with open(PARTICIPANT_FILE, "w") as f:
        json.dump(data, f, indent=4)

def confirm_participant_updated():
    prompt = f"Have you updated the participant number and name in the code? (y/n): "
    print(prompt)
    answer = input().strip().lower()
    if answer != "y":
        print("Please update the participant info and re-run the program.")
        exit(1)

def confirm_overwrite():
    prompt = f"Participant number '{PARTICIPANT_NUM}' already exists in '{GAME_VERSION}'. Overwrite? (y/n): "
    print(prompt)
    answer = input().strip().lower()
    if answer != "y":
        print("Not overwriting participant. Exiting.")
        exit(1)

def update_participants_file(selected_words=None):
    participants = load_participants()
    if GAME_VERSION not in participants:
        participants[GAME_VERSION] = {}

    # Check if participant number exists in the group
    if PARTICIPANT_NUM in participants[GAME_VERSION]:
        confirm_overwrite()

    # Confirm you updated the participant info in the code
    confirm_participant_updated()

    # Save/update participant info
    participants[GAME_VERSION][PARTICIPANT_NUM] = {
        "name": PARTICIPANT_NAME,
        "selected_words": selected_words if selected_words else []
    }

    save_participants(participants)
    return participants

@inlineCallbacks
def main(session, details) -> Generator[None, None, None]:
    prepost = PrePostTest(session, words_file="words.json", images_folder="images")

    # Select and store 5 target words
    selected_words = prepost.select_words(5)
    selected_word_list = [word for word, _ in selected_words]

    # Save participant info + selected words
    participants = update_participants_file(selected_word_list)
    participant_name = participants[GAME_VERSION][PARTICIPANT_NUM]["name"]

    print(f"Starting game for participant #{PARTICIPANT_NUM}: {participant_name} in '{GAME_VERSION}' group.")
    print(f"Selected words: {selected_word_list}")

    # Run Pre-Test
    results_pre = yield prepost.conduct_test(selected_words, test_type="pre")
    prepost.save_results(results_pre, PARTICIPANT_NUM, GAME_VERSION, "pre")

    # Run Game Phase
    yield session.call("rie.dialogue.config.native_voice", use_native_voice=False)
    yield session.call("rom.optional.behavior.play", name="BlocklyStand")

    game = TabooGame(session, GAME_VERSION)
    yield game.play_taboo()

    # Run Post-Test
    results_post = yield prepost.conduct_test(selected_words, test_type="post")
    prepost.save_results(results_post, PARTICIPANT_NUM, GAME_VERSION, "post")

    print("All phases completed. Goodbye!")
    session.leave()

wamp = Component(
    transports=[{"url": "ws://wamp.robotsindeklas.nl", "serializers": ["msgpack"], "max_retries": 0}],
    realm="rie.67e3bbe8540602623a34ef14",
)

wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])
