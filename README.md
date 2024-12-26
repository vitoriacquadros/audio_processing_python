# Detecção de Sons Altos com ESP32 e Microfone INMP441

Este projeto utiliza um ESP32 e o microfone INMP441 para detectar sons altos em uma faixa específica de frequência. Quando um som alto é detectado, o sistema acende um LED de alerta e envia uma mensagem MQTT informando o status de "Crise: Ativo".

---

## 🛠️ Funcionalidades

- **Detecção de sons altos**: Captura e analisa amostras de áudio em tempo real.
- **Filtro de frequência**: Analisa frequências entre 800 Hz e 3000 Hz para maior precisão.
- **Envio MQTT**: Publica mensagens no formato JSON informando o status de "Crise".
- **Indicação com LED**: Acende um LED quando um som alto é detectado.

---

## 🔧 Componentes Necessários

- **ESP32**
- **Microfone INMP441**
- **LED e resistor**
- **Conexão Wi-Fi**
- **Broker MQTT configurado**

---

## Faixa de Frequência
O código analisa frequências entre 800 Hz e 3000 Hz. Essa faixa foi escolhida para evitar interferências de sons de baixa frequência, como ruídos de fundo, e de alta frequência, que não são relevantes para o sistema.

## Limiar de Detecção
O limiar foi definido como 1500 unidades. Esse valor foi ajustado para garantir que apenas sons realmente altos acionem o sistema, reduzindo falsos positivos.

## Publicação MQTT
Sempre que um som alto é detectado, o sistema publica uma mensagem no formato JSON no tópico configurado.


🔍 Problemas e Soluções

- **Ruídos de baixa frequência:** Foram eliminados restringindo a análise a frequências acima de 800 Hz.
- **Interferências de alta frequência:** Excluídas limitando a análise a 3000 Hz.
- **Falsos positivos:** Ajustamos o limiar de detecção para ignorar sons fracos ou irrelevantes.
