from machine import Pin, I2S
import network
import time
import math
import ustruct
from umqtt.robust import MQTTClient
import gc
import ujson

# Configuração dos pinos I2S
ws_pin = Pin(23)
sd_pin = Pin(19)
sck_pin = Pin(22)

# Configuração do pino de alerta
alert_pin = Pin(2, Pin.OUT)

# Configuração do Wi-Fi
SSID = "xxxx"
WIFI_PASSWORD = 'xxxx'

# Configuração MQTT
BROKER = "e8d57473374e430790cfc2a1208ceb5f.s1.eu.hivemq.cloud"
PORT = 8884
USERNAME = "analyzerspectrum"
PASSWORD = "Esp32conectado"
TOPIC = b"automacao/teste"

# Conecta ao Wi-Fi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, WIFI_PASSWORD)
    while not wlan.isconnected():
        print("Conectando ao Wi-Fi...")
        time.sleep(1)
    print("Conectado ao Wi-Fi!")
    print("Endereço IP:", wlan.ifconfig()[0])

# Conecta ao MQTT
def connect_mqtt(): 
    client = MQTTClient(
        client_id="ifrsrgautorvy2024",
        server='mqtt-dashboard.com'
    )
    client.connect()
    print("Conectado ao broker MQTT!")
    return client

# FFT manual
def fft(samples, fs):
    N = len(samples)
    result = []
    for k in range(N):
        real = 0
        imag = 0
        for n in range(N):
            angle = 2 * math.pi * k * n / N
            real += samples[n] * math.cos(angle)
            imag -= samples[n] * math.sin(angle)
        magnitude = math.sqrt(real**2 + imag**2)
        result.append(magnitude)
    freqs = [(k / N) * fs for k in range(N)]
    return freqs, result

# Suavização dos dados
def smooth_samples(samples, window_size=5):
    return [
        sum(samples[i:i+window_size]) / window_size
        for i in range(len(samples) - window_size + 1)
    ]

# Verifica som alto com sensibilidade ajustada
def check_sound_alert(frequencies, magnitudes, threshold=2000):
    relevant_magnitudes = [
        m for f, m in zip(frequencies, magnitudes) if 800 <= f <= 2500
    ]
    if len(relevant_magnitudes) > 0:
        magnitude_avg = sum(relevant_magnitudes) / len(relevant_magnitudes)
        return magnitude_avg > threshold
    return False

# Reconecta ao broker MQTT
def reconnect_mqtt():
    global mqtt_client
    try:
        mqtt_client.disconnect()
    except:
        pass
    print("Reconectando ao broker MQTT...")
    mqtt_client = connect_mqtt()

# Loop principal
try:
    connect_wifi()
    mqtt_client = connect_mqtt()

    # Configuração do periférico I2S
    audio_in = I2S(
        0,
        sck=sck_pin,
        ws=ws_pin,
        sd=sd_pin,
        mode=I2S.RX,
        bits=16,
        format=I2S.MONO,
        rate=16000,
        ibuf=4800
    )
    
    mic_samples = bytearray(512)
    mic_samples_mv = memoryview(mic_samples)

    last_publish_time = time.time()

    while True:
        try:
            num_read = audio_in.readinto(mic_samples_mv)
            if num_read > 0:
                samples = ustruct.unpack('<' + 'h' * (num_read // 2), mic_samples[:num_read])
                samples = [s - sum(samples) / len(samples) for s in samples]  # Remoção do valor médio (DC offset)

                # Suavização dos dados
                samples = smooth_samples(samples, window_size=3)

                # FFT com 128 amostras
                fft_result = fft(samples[:128], 16000)

                # Verifica se som alto foi detectado
                if check_sound_alert(fft_result[0], fft_result[1], threshold=2000):
                    print("Som alto detectado!")
                    alert_pin.value(1)

                    # Publicar mensagem JSON apenas se houver conexão
                    if mqtt_client is not None:
                        current_time = time.time()
                        if current_time - last_publish_time > 1:  #Evita publicar com muita frequência
                            try:
                                mqtt_client.ping()
                                message = ujson.dumps({"Crise": "Ativa"})
                                mqtt_client.publish(TOPIC, message)
                                print(f"Mensagem enviada: {message}")
                                last_publish_time = current_time
                            except Exception as mqtt_error:
                                print(f"Erro ao publicar no MQTT: {mqtt_error}")
                                reconnect_mqtt()
                else:
                    alert_pin.value(0)
        except Exception as loop_error:
            print(f"Erro no loop principal: {loop_error}")
            reconnect_mqtt()
            gc.collect()

        time.sleep(1)  #Intervalo aumentado para reduzir frequência de verificação

except Exception as e:
    print(f"Erro geral: {e}")
finally:
    if 'audio_in' in locals():
        audio_in.deinit()
    if 'mqtt_client' in locals() and mqtt_client is not None:
        mqtt_client.disconnect()
