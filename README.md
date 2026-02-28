# 🛡️ Raspberry Pi 기반 스마트 홈 감시 시스템 (CCTV)

초음파 센서와 카메라를 연동한 실시간 이벤트 스트리밍 및 환경 모니터링 솔루션입니다. 현관문 앞의 움직임을 감지하여 실시간으로 상황을 중계하고, 집 주변의 온습도 및 조도를 파악할 수 있는 개인 IoT 프로젝트입니다.

### 요구사항
1) 누군가 현관문 앞에 가까이 멈춰서면 초음파센서로 인식하여 카메라가 작동한다. 
2) 초음파센서로 움직임을 인식하여 LED에 불이 들어오고 카메라를 통해 현관문 앞의 상황이 방안의 개인 PC 웹페이지로 실시간 출력된다. 
3) 초음파센서에 움직임이 감지되지 않으면 웹 브라우저에서 카메라는 출력을 멈추고 화면이 사라진다. 
4) 온/습도 센서를 통해 웹 페이지에서 문앞의 온/습도 측정이 가능하다 (외출 시 참고 가능)
5) 조도 센서를 통하여 낮과 밤 파악이 가능하다. 
6) 스위치로 센서데이터 발행 On / Off가 가능하다. 
7) 메시지를 통하여 움직임 감지, LED on/off, MQTT연결상태, 센서데이터 발행 중지/재개 상태를 시간과 함께 나타낸다. 
8) 온습도 변화, 움직임 감지 횟수를 그래프를 통하여 시각화한다.

### 시스템 구조

본 프로젝트는 **Publisher-Subscriber 패턴(MQTT)**을 활용하여 지연 시간을 최소화한 데이터 통신을 구현했습니다.

*   **Raspberry Pi (Publisher)**: 센서 데이터를 수집하고 OpenCV로 캡처한 프레임을 Base64로 인코딩하여 MQTT 브로커로 전송합니다.
*   **MQTT Broker**: 데이터 메시지를 관리하고 웹 클라이언트에 전달합니다.
*   **Web Client (Subscriber)**: Flask 서버를 통해 접속하며, 브로커로부터 받은 데이터를 차트와 스트리밍 화면으로 렌더링합니다.

<img width="672" height="293" alt="Image" src="https://github.com/user-attachments/assets/71268e4f-fdc1-4743-b2f6-dffe161e51fc" />

### 하드웨어 구조

라즈베리파이 1개, LED 1개, 스위치 1개, 초음파 센서 1개, 온습도 센서 1개, 조도 센서 1개, 카메라 1대를 사용한다. 연결되는 GPIO핀은 다음과 같다.

- LED : GPIO6 - 움직임 감지 시 점등
- 스위치 : GPIO21 – 센서데이터 발행 Stop/Resume
- 초음파 센서 Trig : GPIO20 - 거리 측정용 신호 송신
- 초음파 센서 Echo : GPIO16 - 거리 측정용 신호 수신
- 온습도 센서 SDA : GPIO2 (SDA) - 온/습도 데이터 통신
- 온습도 센서 SCL ; GPIO3 (SCL) - 온/습도 데이터 통신
- 조도 센서 - SPI 통신 (MCP3008 이용)
- SPI MOSI : GPIO10 - MCP3008 데이터 전송 (MOSI)
- SPI MISO : GPIO9 - MCP3008 데이터 수신 (MISO)
- SPI SCLK : GPIO11 - MCP3008 클록 신호 (SCLK)
- SPI CE0 : GPIO8 - MCP3008 칩 선택 (CE0)

<img width="641" height="279" alt="Image" src="https://github.com/user-attachments/assets/b99ec13b-1487-406a-bb73-b6cbcea4adaf" /> 

### 디렉토리 구조

소스코드는 총 5개의 파일로 이루어져 있습니다.

<img width="678" height="252" alt="Image" src="https://github.com/user-attachments/assets/5b05ebd9-4ab6-4255-bff5-26fc3042ff90" />

1) App.py : Flask 웹 서버 프레임 워크를 사용하여 웹 서버를 구축하는 파이썬 파일
2) Sensors.py : 라즈베리파이에 연결된 장치(LED, 초음파센서, 조도센서, 온습도센서)들로부터 센서 값을 측정할 수 있는 함수들, GPIO 핀 설정등을 구현해놓은 파이썬 파일
3) Mqtt.py : 브로커와 연결, 로그 메시지 발행, Sensors을 임포트하고 센서 값 측정 함수들을 사용하여 변수에 저장한 뒤 브로커로 센서값들을 발행, 센서데이터 발행 중지/재개, 카메라로부터 사진을 캡처하여 브로커로 발행 등의 기능을 하는 파이썬 파일 
4) mqttio.js : 브로커와 연결하여 Mqtt.py에서 보낸 데이터, 메세지들을 수신. 온습도 변화 값, 움직임 횟수 등을 chart.js를 통하여 시각화하고 메시지에 타임스탬프 띄우기 등의 기능을 구현한 javaScript 파일
5) Index.html : mqttio.js 파일을 이용하여 데이터를 받아 웹 페이지를 구현한 HTML 파일
---

## 📌 주요 기능 (Key Features)

*   **이벤트 기반 실시간 스트리밍**
    *   초음파 센서가 특정 거리(30cm) 내 움직임을 감지하면 자동으로 카메라를 활성화하고 웹 페이지로 실시간 영상을 송출합니다.
*   **환경 데이터 모니터링**
    *   온습도 및 조도 센서를 통해 실외 상태를 실시간으로 파악하며, 조도 값에 따라 낮/밤 상태를 자동 판별합니다.
*   **데이터 시각화**
    *   수집된 환경 데이터와 움직임 감지 횟수를 Chart.js를 이용해 직관적인 라인 차트로 시각화합니다.
*   **시스템 제어 및 로깅**
    *   물리 스위치를 이용해 데이터 발행을 제어할 수 있으며, 모든 동작 상태(MQTT 연결, 센서 감지 등)를 타임스탬프와 함께 로그로 기록합니다.

---

## 🛠 기술 스택 (Tech Stack)

### 💻 Hardware
*   **Main**: Raspberry Pi
*   **Sensors**: Ultrasonic (HC-SR04), Temp/Humidity (HTU21D), Photoresistor (with MCP3008 ADC), LED, Switch
*   **Camera**: USB Webcam

### ⚙️ Software
*   **Backend**: Python, Flask (Web Server)
*   **Frontend**: JavaScript, HTML5, CSS3, Chart.js (Visualization)
*   **Communication**: MQTT (Paho-MQTT)
*   **Image Processing**: OpenCV (Camera Streaming)

---

## 실행 결과
1) putty에 연결하여 mosquitto, App.py 파일을 실행합니다
<img width="1346" height="608" alt="Image" src="https://github.com/user-attachments/assets/5888e116-8111-4d73-b7e7-6b5c62bf4149" />

2) 웹페이지에 접속하여 브로커의 ip 입력하고 커넥트버튼을 눌러 mqtt 연결을 합니다. 연결이 성공하면 연결이 성공하였다는 메시지가 출력됩니다. 
<img width="1134" height="640" alt="Image" src="https://github.com/user-attachments/assets/412337b2-0bb6-48b5-b44f-88d3df8d9daf" />

3) 실제 상황이 연출이 어려운 관계로 책상 위의 상황을 현관 문, 자동차 장난감을 사람이라고 가정하여 진행하겠습니다.
<img width="740" height="533" alt="Image" src="https://github.com/user-attachments/assets/a5b31b4d-7e76-4083-90d5-80cb575dc597" />

4) mqtt.py 실행하여 데이터를 브로커로 전송합니다. 브로커를 통해 받은 데이터(온습도,조도,메세지)들이 웹에 출력됩니다.
<img width="746" height="430" alt="Image" src="https://github.com/user-attachments/assets/8beff195-9ba2-431d-8a2b-ab27c1abe052" /> 

5) 사람이 초음파센서 가까이 접근(30cm로 설정)하게 되면 사람을 인식하여 LED에 불이 들어오게 됩니다.
<img width="754" height="477" alt="Image" src="https://github.com/user-attachments/assets/7b20f298-8377-414f-8365-ddf2433265cb" />

6) 웹 페이지에 카메라 스트리밍 화면이 나타나고, LED가 켜지고 움직임이 감지되었다는 메시지가 출력됩니다.
<img width="904" height="625" alt="Image" src="https://github.com/user-attachments/assets/41e552fa-cd5e-4d5f-885e-753a600a16db" />

7) 다시 사람이 초음파센서로부터 멀어지게되면 사람을 인식하지 못하며 LED가 꺼집니다.
<img width="770" height="590" alt="Image" src="https://github.com/user-attachments/assets/854ff394-5e8c-4a12-9fe5-796bf745a053" /> 

8) 웹페이지에 카메라 스트리밍 화면이 사라지며 LED가 꺼졌다는 메시지를 출력합니다.
<img width="988" height="602" alt="Image" src="https://github.com/user-attachments/assets/83b679a5-5b7b-4841-a452-c11b9645d43f" />

9) 센서데이터 발행을 잠시 중단하기 위해 스위치 제어를 시작해보겠습니다. 스위치를 누르면 센서데이터 발행이 중지되며 ,중지되었다는 메시지가 출력됩니다.
<img width="807" height="562" alt="Image" src="https://github.com/user-attachments/assets/26f930e8-8923-4b47-adff-d84ea793d0a7" />

10) 다시 스위치를 누르게 되면 센서데이터 발행을 재개하며 메시지를 출력합니다.
<img width="787" height="501" alt="Image" src="https://github.com/user-attachments/assets/b55682b4-feea-4bd7-b099-b5db5bcf8e61" />

11) 차트를 통하여 시간에 따른 온습도 변화 추이와 움직임 감지 횟수를 시각화 할 수 있습
니다.
<img width="843" height="315" alt="Image" src="https://github.com/user-attachments/assets/4466e366-6095-4f14-aed4-0a7897d8aae7" /> 
---

## 💡 주요 해결 과제 (Challenges & Learnings)

*   **멀티스레딩을 통한 스트리밍 최적화**
    *   단일 루프에서 센서 데이터 처리와 카메라 스트리밍을 동시에 진행할 시 발생하는 병목 현상을 해결하기 위해, 카메라 스트리밍 로직을 별도 스레드로 분리하여 끊김 없는 영상 송출을 구현했습니다.
*   **효율적인 데이터 패키징**
    *   영상 데이터를 웹으로 전송하기 위해 JPEG 인코딩과 Base64 인코딩을 조합하여 MQTT 프로토콜에 적합한 형태로 변환하여 전송했습니다.
*   **설계의 중요성 인지**
    *   초기 기획 단계에서의 세부적인 파일 구조 및 함수 설계가 개발 생산성에 미치는 영향을 체감하며, 유지보수가 용이한 코드 작성의 중요성을 배웠습니다.
