import wave
import numpy as np


class AudioSignal:
    def __init__(self, file_path):
        with wave.open(file_path, "rb") as wav_file:
            n_frames = wav_file.getnframes()
            self.n_frames = n_frames

            frame_rate = wav_file.getframerate()
            duration = n_frames / float(frame_rate)
            self.duration = duration

            audio_frames = wav_file.readframes(n_frames)
            audio_signal = np.frombuffer(audio_frames, dtype=np.int16)
            n_channels = wav_file.getnchannels()

            if 0 >= n_channels > 2:
                raise NotImplementedError(
                    f"Wav file has {n_channels} channels")

            if n_channels == 2:
                audio_signal = audio_signal[::2]
            audio_signal = audio_signal / np.max(np.abs(audio_signal))
            self.signal = audio_signal
