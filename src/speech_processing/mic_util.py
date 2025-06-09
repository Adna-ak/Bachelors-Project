"""
File:     mic_util.py
Authors:  Özde Pilli (s5257018) and Adna Kapidžić (s5256100)
Group:    5

Description:
    This module provides utility functions for working with microphones using
    the PyAudio library. It allows the listing of available microphones and
    selecting a specific one.
"""

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
                    return mic

        return available_mics[0]
