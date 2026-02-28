# 🛡️ Raspberry Pi 기반 스마트 홈 감시 시스템 (CCTV)

초음파 센서와 카메라를 연동한 실시간 이벤트 스트리밍 및 환경 모니터링 솔루션입니다. 현관문 앞의 움직임을 감지하여 실시간으로 상황을 중계하고, 집 주변의 온습도 및 조도를 파악할 수 있는 IoT 프로젝트입니다.

### 요구사항
1) 누군가 현관문 앞에 가까이 멈춰서면 초음파센서로 인식하여 카메라가 작동한다. 
2) 초음파센서로 움직임을 인식하여 LED에 불이 들어오고 카메라를 통해 현관문 앞의 상황이 방안의 개인 PC 웹페이지로 실시간 출력된다. 
3) 초음파센서에 움직임이 감지되지 않으면 웹 브라우저에서 카메라는 출력을 멈추고 화면이 사라진다. 
4) 온/습도 센서를 통해 웹 페이지에서 문앞의 온/습도 측정이 가능하다 (외출 시 참고 가능)
5) 조도 센서를 통하여 낮과 밤 파악이 가능하다. 
6) 스위치로 센서데이터 발행 On / Off가 가능하다. 
7) 메시지를 통하여 움직임 감지, LED on/off, MQTT연결상태, 센서데이터 발행 중지/재개 상태를 시간과 함께 나타낸다. 
8) 온습도 변화, 움직임 감지 횟수를 그래프를 통하여 시각화한다.

---

## 🏗️ 시스템 구조 (System Architecture)

본 프로젝트는 지연 시간을 최소화하고 안정적인 통신을 위해 **Publisher-Subscriber 패턴(MQTT)**을 활용했습니다.

*   📡 **Raspberry Pi (Publisher)**: 센서 데이터를 수집하고 OpenCV로 캡처한 비디오 프레임을 Base64로 인코딩하여 MQTT 브로커로 전송합니다.
*   🔄 **MQTT Broker**: 데이터 메시지를 중계하고 관리하여 구독된 웹 클라이언트에 즉시 전달합니다.
*   💻 **Web Client (Subscriber)**: Flask 기반의 웹 서버를 통해 접속하며, 브로커로부터 받은 데이터를 시각화된 차트와 스트리밍 화면으로 렌더링합니다.

<img width="672" height="293" alt="시스템 아키텍처 다이어그램" src="https://github.com/user-attachments/assets/71268e4f-fdc1-4743-b2f6-dffe161e51fc" />

---

## 🛠️ 하드웨어 구성 (Hardware Configuration)

시스템은 제어보드(Raspberry Pi), LED(1개), 푸시 버튼 스위치(1개), 초음파 센서(1개), 온습도 센서(1개), 조도 센서(1개), 그리고 웹 카메라(1대)로 구성됩니다. 각 센서와 보드의 연결(GPIO)은 다음과 같습니다.

*   💡 **LED**: `GPIO 6` - 움직임 감지 시 점등
*   🔘 **스위치**: `GPIO 21` – 센서 데이터 발행 Stop/Resume 제어
*   📏 **초음파 센서 (HC-SR04)**: 
    *   Trig: `GPIO 20` - 거리 측정 신호 송신
    *   Echo: `GPIO 16` - 거리 측정 신호 수신
*   🌡️ **온습도 센서 (HTU21D)**: 
    *   SDA: `GPIO 2` - I2C 데이터 통신
    *   SCL: `GPIO 3` - I2C 클럭 통신
*   ☀️ **조도 센서 (포토레지스터 + MCP3008 ADC)**: 
    *   SPI MOSI: `GPIO 10` - 데이터 전송
    *   SPI MISO: `GPIO 9` - 데이터 수신
    *   SPI SCLK: `GPIO 11` - 클럭 신호
    *   SPI CE0: `GPIO 8` - 칩 선택

<img width="641" height="279" alt="하드웨어 결선도" src="https://github.com/user-attachments/assets/b99ec13b-1487-406a-bb73-b6cbcea4adaf" /> 

---

## 🗂️ 디렉토리 구조 (Directory Structure)

소스 코드는 유지 보수와 가독성을 고려하여 역할별로 총 5개의 주요 파일로 나뉘어져 파이썬 서버와 자바스크립트 클라이언트로 구성됩니다.

```text
miniproject/
├── 🐍 App.py             # Flask 프레임워크 기반의 메인 웹 서버 파일
├── ⚙️ Sensors.py         # 라즈베리파이 센서 및 GPIO 제어 함수 집합
├── 📡 Mqtt.py            # MQTT 브로커 통신, 비디오 캡처, 시스템 로직 통합
├── 📁 static/
│   └── 📜 mqttio.js      # MQTT 웹 소켓 연결, Chart.js 데이터 시각화, 웹 UI 제어
└── � templates/
    └── 🌐 Index.html     # 사용자에게 제공되는 메인 대시보드 인터페이스
```

<img width="678" height="252" alt="파일 구성도" src="https://github.com/user-attachments/assets/5b05ebd9-4ab6-4255-bff5-26fc3042ff90" />

---

## 🚀 실행 결과 (Execution Results)

**1. 시스템 및 서버 시작**
Putty로 라즈베리파이에 접속하여 백그라운드에서 `mosquitto` 브로커를 실행하고 파이썬 백엔드 서버인 `App.py`를 가동합니다.

```bash
# 터미널에서 실행
mosquitto -v &
python App.py
```
<img width="1346" height="608" alt="서버 구동 화면" src="https://github.com/user-attachments/assets/5888e116-8111-4d73-b7e7-6b5c62bf4149" />

**2. 대시보드 접속 및 연결**
웹 브라우저를 열고 플라스크 서버 IP(예: `http://라즈베리파이IP:8080`)로 접속한 뒤, 브로커 IP를 입력하고 'Connect' 버튼을 누릅니다. 정상적으로 연결 시 성공 로그 메시지가 출력됩니다.

<img width="1134" height="640" alt="MQTT 연결 화면" src="https://github.com/user-attachments/assets/412337b2-0bb6-48b5-b44f-88d3df8d9daf" />

**3. 시나리오 설정**
실제 환경 구축 대신 책상 위 환경을 현관문으로, 작은 모형 자동차를 방문객으로 가정하여 시연을 진행합니다.

<img width="740" height="533" alt="시뮬레이션 환경 구축" src="https://github.com/user-attachments/assets/a5b31b4d-7e76-4083-90d5-80cb575dc597" />

**4. 데이터 수집 시작**
`Mqtt.py`를 백그라운드에서 실행하면 라즈베리파이는 주기적으로 각종 센서 데이터를 읽고 영상과 함께 브로커를 거쳐 웹 인터페이스에 출력하기 시작합니다.

<img width="746" height="430" alt="정상 데이터 출력 진입" src="https://github.com/user-attachments/assets/8beff195-9ba2-431d-8a2b-ab27c1abe052" /> 

**5. 방문객 이벤트 감지 (LED 활성화)**
모형 자동차(사람)가 초음파 센서 근처 지정 거리(30cm 이하)로 진입하면 이벤트를 인식하여 즉시 물리 LED 모듈에 불이 켜집니다.

<img width="754" height="477" alt="물리 LED 점등" src="https://github.com/user-attachments/assets/7b20f298-8377-414f-8365-ddf2433265cb" />

**6. 웹 스트리밍 시작**
움직임 감지와 동시에 브라우저의 전용 영역에 카메라 실시간 스트리밍이 노출되며, LED 동작 이벤트가 로그에 실시간으로 반영됩니다.

<img width="904" height="625" alt="웹 카메라 송출" src="https://github.com/user-attachments/assets/41e552fa-cd5e-4d5f-885e-753a600a16db" />

**7. 방문객 이탈로 인한 센서 해제**
모형 자동차(사람)가 초음파 센서 측정 범위에서 벗어나면, 시스템은 상태 변화를 인식하고 자동으로 LED 전원을 차단합니다.

<img width="770" height="590" alt="물리 LED 소등" src="https://github.com/user-attachments/assets/854ff394-5e8c-4a12-9fe5-796bf745a053" /> 

**8. 웹 스트리밍 중단**
LED 소등과 연동되어 브라우저 내의 카메라 스트리밍 요소가 사용자로부터 닫히며 자원 낭비를 방지합니다.

<img width="988" height="602" alt="카메라 화면 닫힘" src="https://github.com/user-attachments/assets/83b679a5-5b7b-4841-a452-c11b9645d43f" />

**9. 수동 데이터 모니터링 제어 (OFF)**
회로의 스위치 부품을 물리적으로 클릭하면 센서 데이터 전송 루틴이 즉시 중단되며, 상태 로그에 "센서데이터 발행 중지" 메세지가 수신됩니다.

<img width="807" height="562" alt="발행 중지 제어" src="https://github.com/user-attachments/assets/26f930e8-8923-4b47-adff-d84ea793d0a7" />

**10. 수동 데이터 모니터링 복구 (ON)**
잠시 후 동일하게 스위치를 재클릭 시 중단되었던 데이터 발행 기능이 다시 구동되어 정상적인 운영 상태로 복원됩니다.

<img width="787" height="501" alt="발행 재개 제어" src="https://github.com/user-attachments/assets/b55682b4-feea-4bd7-b099-b5db5bcf8e61" />

**11. 수집 데이터 시각적 차트 제공**
우측 하단이나 별도의 차트 UI 영역을 통하여 수집된 데이터의 시간대별 온/습도 추세와 움직임 감지 빈도를 차트 형태로 직관적으로 체크할 수 있습니다.

<img width="843" height="315" alt="차트 시각화 다이어그램" src="https://github.com/user-attachments/assets/4466e366-6095-4f14-aed4-0a7897d8aae7" /> 

---

## 💡 주요 해결 과제 (Challenges & Learnings)

*   **멀티스레딩을 통한 스트리밍 최적화**
    *   단일 루프에서 센서 데이터 처리와 카메라 스트리밍을 동시에 진행할 시 발생하는 병목 현상을 해결하기 위해, 카메라 스트리밍 로직을 별도 스레드로 분리하여 끊김 없는 영상 송출을 구현했습니다.
*   **효율적인 데이터 패키징**
    *   영상 데이터를 웹으로 전송하기 위해 JPEG 인코딩과 Base64 인코딩을 조합하여 MQTT 프로토콜에 적합한 형태로 변환하여 전송했습니다.
*   **설계의 중요성 인지**
    *   초기 기획 단계에서의 세부적인 파일 구조 및 함수 설계가 개발 생산성에 미치는 영향을 체감하며, 유지보수가 용이한 코드 작성의 중요성을 배웠습니다.
