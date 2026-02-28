import time
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import cv2
import base64
import Sensor as sensors
import threading

# MQTT 브로커 설정
BROKER_IP = "localhost" # 브로커 IP 주소
BROKER_PORT = 1883 # MQTT 기본 포트

# MQTT 클라이언트 초기화
client = mqtt.Client(protocol=mqtt.MQTTv311) # MQTT 프로토콜 설정

# 로그 메시지 발행 함수
def log_message(content):
    log_entry = f"{content}" # 로그 메시지 생성
    client.publish("system_logs", log_entry) # MQTT로 로그 발행
    print(log_entry) # 출력

# MQTT 연결 성공 시 호출되는 콜백 함수
def on_connect(client, userdata, flags, rc):
    print(f"브로커와 연결되었습니다.")

# MQTT 연결 종료 시 호출되는 콜백 함수
def on_disconnect(client, userdata, rc):
    print(f"브로커 연결이 끊겼습니다.")

# 버튼 상태에 따라 센서 데이터 발행을 중지/재개
def stop_resume(button_pin, current_state):
    btn_status = GPIO.input(button_pin) # 버튼 상태 읽기
    if btn_status == GPIO.HIGH: # 버튼이 눌린 경우
        print("버튼 입력 감지")
        new_state = 0 if current_state == 1 else 1 # 상태 토글
        if new_state == 1:
            log_message("센서데이터 발행 재개")
        else:
            log_message("센서데이터 발행 중지")
        return new_state
    return current_state # 버튼이 눌리지 않은 경우 상태 유지

# MQTT 클라이언트에 콜백 함수 설정
client.on_connect = on_connect
client.on_disconnect = on_disconnect

# 카메라 스트리밍 함수 (지속 실행)
def start_streaming(broker="localhost", port=1883, topic="video_stream", fps=5):
    try:
        # 카메라 스트리밍 전용 MQTT 클라이언트 설정
        camera_client = mqtt.Client(protocol=mqtt.MQTTv311)
        camera_client.connect(broker, port)
        camera_client.loop_start()
        
        cap = cv2.VideoCapture(0) # USB 카메라 초기화
        if not cap.isOpened():
            print(f"USB 카메라를 열 수 없습니다. 연결을 확인하세요.")
            return

        print(f"카메라 스트리밍 시작.")
        while True:
            ret, frame = cap.read()
            if not ret:
                print(f"프레임 캡처 실패.")
                break
            
            # 프레임을 JPEG로 인코딩 후 MQTT로 전송
            _, buffer = cv2.imencode('.jpg', frame)
            jpg_as_text = base64.b64encode(buffer).decode('utf-8')
            camera_client.publish(topic, jpg_as_text)
            
            time.sleep(1 / fps) # FPS 설정
    except Exception as e:
        print(f"카메라 스트리밍 중 오류 발생: {e}")
    finally:
        cap.release() # 카메라 해제
        camera_client.loop_stop()
        camera_client.disconnect()
        print(f"카메라 스트리밍 종료.")

# 센서 데이터 전송 루프
def send_sensor_data():
    current_state = 1 # 센서 데이터 발행 초기 상태
    on_off = 0 # LED 초기 상태
    
    try:
        while True:
            # 버튼 상태를 확인하여 센서 데이터 발행 여부 결정
            current_state = stop_resume(sensors.button, current_state)
            
            if current_state == 1: # 상태가 1일 때만 센서 데이터 발행
                try:
                    # 센서 데이터 읽기
                    distance = sensors.measure_distance()
                    light = sensors.getLight()
                    temp = sensors.getTemperature()
                    humid = sensors.getHumidity()
                except Exception as e:
                    print(f"센서 데이터 읽기 오류: {e}")
                    continue
                
                # MQTT로 데이터 발행
                try:
                    client.publish("distance", round(distance, 2))
                    client.publish("light", light)
                    client.publish("temp", round(temp, 2))
                    client.publish("humid", round(humid, 2))
                    print(f"센서 데이터 발행: 거리={distance}cm, 조도={light}lx, 온도={temp}°C, 습도={humid}%")
                except Exception as e:
                    print(f"센서 데이터 발행 오류: {e}")

                # LED 제어: 거리 데이터 기반
                if distance <= 30:
                    if on_off == 0: # LED가 꺼져 있으면 켜기
                        log_message("움직임이 감지되었습니다.")
                        log_message("LED를 킵니다.")
                        on_off = 1
                        sensors.controlLED(on_off)
                else:
                    if on_off == 1: # LED가 켜져 있으면 끄기
                        log_message("LED를 끕니다.")
                        on_off = 0
                        sensors.controlLED(on_off)
            
            time.sleep(3) # 3초마다 데이터
            
    except KeyboardInterrupt:
        print("센서 데이터 전송 루프가 중단되었습니다.")
    finally:
        client.loop_stop() # MQTT 루프 정지
        client.disconnect() # 브로커 연결 해제
        log_message("MQTT 클라이언트 연결 종료.")

# MQTT 브로커 연결 및 데이터 전송
try:
    client.connect(BROKER_IP, BROKER_PORT)
    print(f"브로커에 연결되었습니다: {BROKER_IP}:{BROKER_PORT}")
    client.loop_start()
    
    # 카메라 스트리밍 실행 (별도 쓰레드)
    streaming_thread = threading.Thread(target=start_streaming)
    streaming_thread.start()
    
    # 센서 데이터 전송 루프 실행
    send_sensor_data()

except Exception as e:
    log_message(f"MQTT 브로커 연결 실패: {e}")
finally:
    client.loop_stop()
    client.disconnect()
    log_message("MQTT 클라이언트 종료.")