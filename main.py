import sounddevice as sd
import numpy as np

# Parameters for the sound

duration = 10  # seconds, you can change this
sampling_freq = 44100  # Hz
frame_size = 1024 
threshold_freq = (500, 3000)
amplitude_threshold = 50 # nivel para detectar a crise

#Function callback for processing the audio

def audio_callback(indata, frames, time, status):
    #APLICA A TRANSFORMADA DE FOURIER (FFT) NO SINAL DE ENTRADA
    fft_result = np.fft.rfft(indata[:, 0]) #aplica a transformada de fourier
    #CALCULA A FREQUENCIA
    fft_freq = np.fft.rfftfreq(len(fft_result), 1.0/sampling_freq)
    #CALCULA O AMPLITUDE
    amplitude = np.abs(fft_result)
    
    #FILTRA AS FREQUENCIAS
    
    crisis_frequencies = fft_freq[(fft_freq >= threshold_freq[0]) & (fft_freq <= threshold_freq[1])]    
    amplitude_crisis = amplitude[(fft_freq >= threshold_freq[0]) & (fft_freq <= threshold_freq[1])]
    
    if amplitude_crisis.size > amplitude_threshold:
        print("Crisis detected!")
    else:
        print("No crisis detected.")
        
# Start the audio stream

with sd.InputStream(callback=audio_callback, channels=1, samplerate=sampling_freq):
    sd.sleep(duration * 1000)