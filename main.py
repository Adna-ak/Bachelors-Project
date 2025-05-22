"""
File:     main.py
Authors:  Özde Pilli (s5257018) and Adna Kapidžić (s5256100)
Group:    5

Description:
    Main entry point for running the Taboo game with a robot host.
"""

from typing import Generator
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.component import Component, run
import nltk
from src.taboo_game.taboo_game import TabooGame

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    print("Stopwords not found, downloading...")
    nltk.download('stopwords')


@inlineCallbacks
def main(session, details) -> Generator[None, None, None]:
    """
    Sets the session configuration and initiates the Taboo game.

    Args:
        session: Session object used to communicate with the user.
        details: Additional session details or configuration options.

    Yields:
        Generator[None, None, None]: Handles the game flow and interactions.
    """
    yield session.call("rie.dialogue.config.native_voice", use_native_voice=False)
    yield session.call("rom.optional.behavior.play", name="BlocklyStand")

    game_version = "study words"  # Can be "study words", "study topics", or "normal"
    if game_version not in {"study words", "study topics", "normal"}:
        print(f"Invalid game version '{game_version}', using 'normal' instead.")
        game_version = "normal"

    game = TabooGame(session, game_version)
    yield game.play_taboo()

    session.leave()


wamp = Component(

    transports=[{"url": "ws://wamp.robotsindeklas.nl", "serializers": ["msgpack"], "max_retries": 0}],
    realm="rie.67e3bbe8540602623a34ef14",

)

wamp.on_join(main)


if __name__ == "__main__":
    run([wamp])
