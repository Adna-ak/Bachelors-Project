import os
import wave
import time
from typing import Any, Dict, Generator, Optional, Tuple
import pyaudio
import numpy as np
from openai import OpenAI
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
from src.speech_processing.mic_util import MicUtil


API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("OPENAI_API_KEY is not set. Please set it in your environment variables.")

client = OpenAI(api_key=API_KEY)


class SpeechToText:
    def __init__(self,
                 silence_threshold: int = 2500,
                 sample_rate: int = 44100,
                 channels: int = 1,
                 chunk_size: int = 1024,
                 device_index: int | None = None):
        self.silence_threshold = silence_threshold  # Depends on how noisy the room is
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.device_index = device_index
        self.mic_util = MicUtil()

    def choose_mic(self) -> Dict[str, int | str]:
        """
        Selects the microphone device based on the provided index.

        Returns:
            Dict[str, int | str]: The microphone device info.
        """
        return self.mic_util.choose_mic_device(self.device_index)

    def setup_audio_stream(self, mic_info: Dict[str, int | str]) -> Tuple[pyaudio.PyAudio, pyaudio.Stream]:
        """
        Sets up the audio stream for recording.

        Args:
            mic_info (Dict[str, int | str]): Information about the selected
            microphone.

        Returns:
            Tuple[pyaudio.PyAudio, pyaudio.Stream]: A tuple containing the
            audio interface (PyAudio) and the audio stream for recording.
        """
        audio_interface = pyaudio.PyAudio()

        if self.channels > mic_info['input_channels']:
            print(
                f"Requested {self.channels} channels, but the mic supports only {mic_info['input_channels']} channels. "
                f"Using {mic_info['input_channels']} channels instead."
            )
            self.channels = mic_info['input_channels']

        stream = audio_interface.open(format=pyaudio.paInt16, channels=self.channels, rate=self.sample_rate, input=True,
                                      input_device_index=mic_info['index'], frames_per_buffer=self.chunk_size)
        return audio_interface, stream

    def save_audio(self, frames: list, output_filename: str) -> Optional[str]:
        """
        Saves the recorded frames to an audio file.

        Args:
            frames (list): The audio frames to be saved.
            output_filename (str): The name of the output file to save the
                audio.

        Returns:
            Optional[str]: The path to the saved audio file, or None if the
            file is empty.
        """
        audio_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), output_filename)
        with wave.open(audio_path, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
            wf.setframerate(self.sample_rate)
            wf.writeframes(b''.join(frames))

        if os.path.getsize(audio_path) == 0:
            print("No audio was recorded. Skipping transcription.")
            return None

        print(f"Audio recorded and saved to {audio_path}")
        return audio_path

    def record_audio(self, output_filename: str = "recorded_speech.wav") -> Optional[str]:
        """
        Records audio from the microphone and saves it to a file.

        Args:
            output_filename (str): The name of the output file to save the
            audio.

        Returns:
            Optional[str]: The path to the saved audio file, or None if no
            audio was recorded.
        """
        mic_info = self.choose_mic()
        audio_interface, stream = self.setup_audio_stream(mic_info)

        frames = []
        start_time = time.time()
        last_sound_time = start_time

        while True:
            print("I am recording")
            data = stream.read(self.chunk_size)
            frames.append(data)

            audio_data = np.frombuffer(data, dtype=np.int16)
            amplitude = np.max(np.abs(audio_data))

            if amplitude > self.silence_threshold:
                print("Speech detected.")
                last_sound_time = time.time()
            elif time.time() - last_sound_time > 5:  # Kids might speak slower, especially when trying to speak English
                print("No speech detected, stopping recording.")
                break

        stream.stop_stream()
        stream.close()
        audio_interface.terminate()

        audio_path = self.save_audio(frames, output_filename)
        return audio_path

    def trim_silence(self, audio_path: str, silence_thresh: int = -40, min_silence_len: int = 500) -> Optional[str]:
        """
        Removes silent segments from the beginning and end of an audio file.
        Without this function, the Whisper transcription transcribes random
        words to silence.

        Args:
            audio_path (str): Path to the WAV audio file that needs silence
                trimming.
            silence_thresh (int, optional): The volume threshold (in dBFS)
                below which audio is considered silence. Defaults to -40 dBFS.
            min_silence_len (int, optional): The minimum duration
                (in milliseconds) of silence to be considered for trimming.
                Defaults to 500 ms.

        Returns:
            Optional[str]: The path to the trimmed audio file if successful,
            otherwise None if no speech is detected.
        """
        audio = AudioSegment.from_wav(audio_path)
        non_silent_chunks = detect_nonsilent(audio, min_silence_len=min_silence_len, silence_thresh=silence_thresh)

        if not non_silent_chunks:
            return None

        start_trim = non_silent_chunks[0][0]
        end_trim = non_silent_chunks[-1][1]

        trimmed_audio = audio[start_trim:end_trim]
        trimmed_audio.export(audio_path, format="wav")
        return audio_path

    def process_audio(self, audio_path: str, version: str) -> Generator[Dict[str, Any], None, Dict[str, Any]]:
        trimmed_audio_path = self.trim_silence(audio_path)
        result = {}

        if trimmed_audio_path is None:
            return result

        try:
            with open(audio_path, "rb") as audio_file:
                kwargs = {
                    "model": "gpt-4o-transcribe",
                    "file": audio_file,
                    "response_format": "text",
                    "prompt": (
                        "The following conversation is of a 12 year old Dutch child trying to learn English."
                    ),
                }

                if version == "control":
                    kwargs["language"] = "en"

                transcript = client.audio.transcriptions.create(**kwargs)

            if transcript:
                result = transcript
            else:
                print("Transcription failed.")

        except Exception as e:
            print("Error during audio processing:", e)

        return result
