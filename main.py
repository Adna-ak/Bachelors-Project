import json
import os
from typing import Generator
from twisted.internet.defer import inlineCallbacks
from twisted.internet import reactor, task
from autobahn.twisted.component import Component, run
import nltk
import random
from prepost_test import PrePostTest
from src.taboo_game.taboo_game import TabooGame
from src.robot_movements.say_animated import say_animated

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

def wait(seconds):
    return task.deferLater(reactor, seconds, lambda: None)

@inlineCallbacks
def main(session, details) -> Generator[None, None, None]:
    yield session.call("rie.dialogue.config.native_voice", use_native_voice=False)
    yield session.call("rom.optional.behavior.play", name="BlocklyStand")

    prepost = PrePostTest(session, words_file="words.json", images_folder="images")
    game = TabooGame(session, GAME_VERSION)

    # Select and store 5 target words
    selected_words = prepost.select_words(5)
    selected_word_list = [word for word, _ in selected_words]

    # Save participant info + selected words
    participants = update_participants_file(selected_word_list)

    # Introductory message
    prompt = (
        ""
    )
    yield say_animated(session, prompt, language="nl")

    # Pre-test explanation
    prompt = (
        "Ik zal nu telkens een woord per ronde opnoemen in het Engels en jij "
        "zal het bijbehorende plaatje aan moeten klikken. Er zijn 5 rondes."
    )
    yield say_animated(session, prompt, language="nl")

    prompt = (
        "Put your laptop in front of the participant. "
        "Press any key to continue with the pre-test."
    )
    print(prompt)
    _ = input().strip().lower()

    # Pre-test
    results_pre = yield prepost.conduct_test(selected_words, test_type="pre")
    prepost.save_results(results_pre, PARTICIPANT_NUM, GAME_VERSION, "pre")

    prompt = (
        "Move your laptop out of the participant's view. "
        "Press any key to continue with the experiment."
    )
    print(prompt)
    _ = input().strip().lower()

    # Explanation about 1 minute waiting time
    prompt = (
        "We zullen nu een minuut wachten voordat we verdergaan met het "
        "experiment. Ik zal elke tien seconden naar je zwaaien."
    )
    yield say_animated(session, prompt, language="nl")

    # Repeat BlocklyWaveRightArm every 10 seconds for 1 minute
    for _ in range(6):
        yield session.call("rom.optional.behavior.play", name="BlocklyWaveRightArm")
        yield wait(10)

    # Game explanation
    prompt = (
        "We zullen nu het spel spelen waarin jij het woord moet raden dat ik "
        "in gedachten heb. Er zijn vijf rondes."
    )
    yield say_animated(session, prompt, language="nl")

    prompt = ("Let's play another round!")
    random.shuffle(selected_word_list)

    # WOW game, 5 rounds
    for i, word in enumerate(selected_word_list):
        if i != 0:
            yield say_animated(session, prompt, language="en")
        game.secret_word = word
        yield game.robot_is_host()

    # Explanation about 1 minute waiting time
    prompt = (
        "We zullen nu een minuut wachten voordat we verdergaan met de laatste "
        "test. Ik zal elke tien seconden naar je zwaaien."
    )
    yield say_animated(session, prompt, language="nl")

    # Repeat BlocklyWaveRightArm every 10 seconds for 1 minute
    for _ in range(6):
        yield session.call("rom.optional.behavior.play", name="BlocklyWaveRightArm")
        yield wait(10)

    # Post-test explanation
    prompt = (
        "Ik zal nu telkens een woord per ronde opnoemen in het Engels en jij "
        "zal het bijbehorende plaatje aan moeten klikken. Er zijn 5 rondes."
    )
    yield say_animated(session, prompt, language="nl")

    prompt = (
        "Put your laptop in front of the participant. "
        "Press any key to continue with the post-test."
    )
    print(prompt)
    _ = input().strip().lower()

    # Post-test
    results_post = yield prepost.conduct_test(selected_words, test_type="post")
    prepost.save_results(results_post, PARTICIPANT_NUM, GAME_VERSION, "post")

    prompt = (
        "Move your laptop out of the participant's view. "
        "Press any key to continue with the experiment."
    )
    print(prompt)
    _ = input().strip().lower()

    # End message and explanation about evaluation form
    prompt = (
        "Het experiment is nu afgelopen. Bedankt voor je deelname! Je hebt "
        "het geweldig gedaan! Je zult nu een kort formulier moeten invullen "
        "om mij en het spel te beoordelen."
    )
    yield say_animated(session, prompt, language="nl")

    prompt = (
        "Did the participant fill out the evaluation form? "
        "Did you check whether the participant wrote their name on the form? "
        "Press any key to continue."
    )
    print(prompt)
    _ = input().strip().lower()

    print("==================END OF EXPERIMENT==================")
    session.leave()

wamp = Component(
    transports=[{"url": "ws://wamp.robotsindeklas.nl", "serializers": ["msgpack"], "max_retries": 0}],
    realm="rie.67e3bbe8540602623a34ef14",
)

wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])
