# 🛡️ Raspberry Pi 기반 스마트 홈 감시 시스템 (CCTV)

초음파 센서와 카메라를 연동한 실시간 이벤트 스트리밍 및 환경 모니터링 솔루션입니다. 현관문 앞의 움직임을 감지하여 실시간으로 상황을 중계하고, 집 주변의 온습도 및 조도를 파악할 수 있는 IoT 프로젝트입니다.

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

## 🏗 시스템 구조 (System Architecture)

본 프로젝트는 **Publisher-Subscriber 패턴(MQTT)**을 활용하여 지연 시간을 최소화한 데이터 통신을 구현했습니다.

*   **Raspberry Pi (Publisher)**: 센서 데이터를 수집하고 OpenCV로 캡처한 프레임을 Base64로 인코딩하여 MQTT 브로커로 전송합니다.
*   **MQTT Broker**: 데이터 메시지를 관리하고 웹 클라이언트에 전달합니다.
*   **Web Client (Subscriber)**: Flask 서버를 통해 접속하며, 브로커로부터 받은 데이터를 차트와 스트리밍 화면으로 렌더링합니다.

---

## 💡 주요 해결 과제 (Challenges & Learnings)

*   **멀티스레딩을 통한 스트리밍 최적화**
    *   단일 루프에서 센서 데이터 처리와 카메라 스트리밍을 동시에 진행할 시 발생하는 병목 현상을 해결하기 위해, 카메라 스트리밍 로직을 별도 스레드로 분리하여 끊김 없는 영상 송출을 구현했습니다.
*   **효율적인 데이터 패키징**
    *   영상 데이터를 웹으로 전송하기 위해 JPEG 인코딩과 Base64 인코딩을 조합하여 MQTT 프로토콜에 적합한 형태로 변환하여 전송했습니다.
*   **설계의 중요성 인지**
    *   초기 기획 단계에서의 세부적인 파일 구조 및 함수 설계가 개발 생산성에 미치는 영향을 체감하며, 유지보수가 용이한 코드 작성의 중요성을 배웠습니다.