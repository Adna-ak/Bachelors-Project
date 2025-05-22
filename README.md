# Enhancing Second Language Learning in Children through Music-Integrated Robot Interaction

This project modifies the original WOW game by using the Alpha Mini robot as a consistent host to reinforce second language learning in children. The game features simplified language, a language feedback system, multilingual speech recognition via Whisper, all designed to engage young learners in a fun, educational environment.


## Prerequisites
Before proceeding, ensure you have:
- **Python 3.6+** installed (check with `python --version`)


## Create a Virtual Environment
Create a virtual environment and activate it.
1. `python -m venv .venv`
2. `.\.venv\Scripts\activate` (Windows) **or** `source .venv/bin/activate` (macOS/Linux)

### Requirements
- Install requirements.txt: `pip install -r requirements.txt`


## Setup Instructions for Whisper and Suno

1. **Whisper Setup**
   - Follow the instructions in the [Whisper GitHub repository](https://github.com/openai/whisper) to install the necessary dependencies and `ffmpeg` if needed.

2. **Microphone Index**
   - Check and adjust the microphone index for audio recording. 
   - You can modify the index in the `speech_session.py` file, specifically in line 29, if necessary.


## Directory Structure
```
Bachelors-Project
├── .venv
├── src
│   └── language_feedback
│   └── robot_movements
│   └── speech_processing
│   └── taboo_game
│   └── __init__.py
│   └── utils.py
|   main.py
|   README.md
└── requirements.txt
```


## API Key
### Get API Key from OpenAI
To get the same results as we got, you should get an API key from OpenAI for **GPT-3.5** if you have not already:
1. Create an **OpenAI account** (if you have not already).
2. Log into your OpenAI account.
3. Access the **API keys section**.
4. Go to the top-right corner of the page and click on your profile icon.
5. Select API from the dropdown or go directly to [OpenAI platform](https://platform.openai.com/account/api-keys).
6. In the API keys section, click on the `Create new secret key` button. Your new API key will be generated and displayed.
7. Once the key is generated, make sure to **copy it immediately** and store it securely, as it will not be shown again for security reasons.

### Set API Key in Environment Variables
- `set OPENAI_API_KEY=your-api-key-here` (Windows) **or** `export OPENAI_API_KEY="your-api-key-here"` (macOS/Linux)


## Running the Code With Robot
1. Change the Realm: Open `Assignment_3/main.py` and change the realm **(line 52)** so that it corresponds to the currently used robot.
2. Run `Assignment_3/main.py`.


## Extra Information
- Make sure to only speak when `I am recording` appears in the terminal.
- There will appear some **intermediate print statements** to follow the progress of the code execution.
- After speaking, the robot might **do nothing** for a short moment while preparing an answer and the corresponding movement(s).
- The robot will **guide** you through the game. Feel free to **experiment** with words like `goodbye` or with **silences**.
- At the end of a game trial, the robot will ask whether you want to **play again**.
