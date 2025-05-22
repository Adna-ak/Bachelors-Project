"""
File:     speech_to_text.py
Author:  Adna Kapidžić (s5256100)
Group:    5

Description:
    This module handles the conversion of speech to text using OpenAI's
    Whisper model. It records audio from a microphone, processes the recorded
    audio, and returns a transcription.

    You can even use an external microphone to make the STT more accurate,
    even though the difference is minimal if your device microphone is
    working properly and there is not too much background noise. However,
    we did not test the effect with speech from kids.

    We tested this with the Sennheiser microphone that can be found in the
    robotics lab, it will show up like this in the microphones list;
    Microfoon (Sennheiser Profile). There are 4 of these in the list, but the
    first one works best and does not trigger errors. Check on your device
    what index the mic is on that you want to use.
"""

import os
import wave
import time
from typing import Any, Dict, Generator, Optional, Tuple
import pyaudio
import whisper  # From https://github.com/openai/whisper
import numpy as np
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
from twisted.internet.threads import deferToThread
from twisted.internet.defer import inlineCallbacks, DeferredList
# from src.speech_processing.mic_util import MicUtil
from typing import Dict, List
import pyaudio


class MicUtil:
    """
    This class provides methods to list available microphones and choose a
    specific microphone based on a given index or the first available
    microphone.
    """

    def __init__(self):
        self.p = pyaudio.PyAudio()

    def list_available_mics(self) -> List[Dict[str, int | str]]:
        """
        This function scans all audio input devices and returns a list of
        dictionaries where each dictionary contains details (index, name,
        input channels) of a microphone.

        Raises:
            ValueError: If no microphones are found on the system.

        Returns:
            List[Dict[str, int | str]]: A list of dictionaries storing
            information about the available microphones.
        """
        device_count = self.p.get_device_count()
        # get_device_count() lists all available audio devices on your system,
        # including both input devices (microphones) and output devices (speakers/headphones)
        available_mics = []

        for i in range(device_count):
            device_info = self.p.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                # Output devices (such as speakers) have maxInputChannels == 0, and thus will be ignored
                available_mics.append({
                    'index': i,
                    'name': device_info['name'],
                    'input_channels': device_info['maxInputChannels']
                })

        if not available_mics:
            raise ValueError("No microphone available.")

        print("Available Microphone(s):")
        for mic in available_mics:
            print(f"Index: {mic['index']}, Name: {mic['name']}, Channels: {mic['input_channels']}")

        return available_mics

    def choose_mic_device(self, device_index: int | None = None) -> Dict[str, int | str]:
        """
        Chooses a microphone device based on the given index or selects the
        first available microphone if no index is specified.

        Args:
            device_index (int | None, optional): The index of the microphone to
            choose. If None, the first available microphone will be selected.
            Defaults to None.

        Returns:
            Dict[str, int | str]: A dictionary storing information about the
            chosen microphone.
        """
        available_mics = self.list_available_mics()

        if device_index is not None:
            for mic in available_mics:
                if mic['index'] == device_index:
                    print(f"Chosen microphone: {mic['name']} (Index: {mic['index']})")
                    return mic

        print(f"Chosen microphone: {available_mics[0]['name']} (Index: {available_mics[0]['index']})")
        return available_mics[0]

class SpeechToText:
    """
    A class that handles speech-to-text conversion using OpenAI's Whisper
    model. It records audio from the microphone, processes the audio, and
    returns transcriptions.
    """
    _shared_model = None

    def __init__(
            self, silence_threshold: int = 4000,
            model_size: str = "large", sample_rate: int = 44100,
            channels: int = 1, chunk_size: int = 1024,
            device_index: int | None = None
    ):
        self.silence_threshold = silence_threshold  # Depends on how noisy the room is
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.device_index = device_index

        if SpeechToText._shared_model is None:
            print("Whisper model loading...")
            SpeechToText._shared_model = whisper.load_model(model_size)
            print("Whisper model loaded successfully!")

        self.model = SpeechToText._shared_model
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

    def process_audio(self, audio_path: str) -> Dict[str, Any]:
        """
        Processes the recorded audio and transcribes it using the Whisper model.

        Args:
            audio_path (str): The path to the audio file to be processed.

        Returns:
            Dict[str, Any]: The transcription result as a dictionary.
        """
        trimmed_audio_path = self.trim_silence(audio_path)
        result = {}

        if trimmed_audio_path is None:
            print("No speech detected after trimming silence.")
            return result

        try:
            print("Transcribing...")
            result = self.model.transcribe(trimmed_audio_path)
        except Exception as e:
            print("Error during transcription:", e)

        return result

if __name__ == "__main__":
    def main():
        stt = SpeechToText(device_index=None)
        audio_path = stt.record_audio()

        if audio_path:
            trimmed_audio_path = stt.trim_silence(audio_path)
            if trimmed_audio_path:
                print("Transcribing...")
                result = stt.model.transcribe(trimmed_audio_path)
                print("Transcription:")
                print(result.get('text', '[No transcription found]'))
            else:
                print("No speech detected in the recording.")
        else:
            print("No audio was recorded.")

    main()
