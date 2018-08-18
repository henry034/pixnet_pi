import aiy.audio
import wave
import numpy as np

def play_file(filepath, volume):
    with wave.open(filepath, 'rb') as f:
        nchannels, sampwidth, framerate, nframes = f.getparams()[:4] 
        str_data = f.readframes(nframes)
    wave_data = np.fromstring(str_data, dtype=np.short) 
    aiy.audio.play_audio(wave_data, volume) 
