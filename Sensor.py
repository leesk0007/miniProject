import time
import RPi.GPIO as GPIO
from adafruit_htu21d import HTU21D
import busio
import Adafruit_MCP3008

# GPIO 핀 정의
trig = 20 # 초음파 센서 TRIG 핀 (출력)
echo = 16 # 초음파 센서 ECHO 핀 (입력)
led = 6 # LED 핀 (출력)
button = 21 # 버튼 핀 (입력)

# I2C 설정 (온습도 센서를 위한 핀 정의)
sda = 2 # I2C SDA 핀
scl = 3 # I2C SCL 핀
i2c = busio.I2C(scl, sda) # I2C 객체 생성
sensor = HTU21D(i2c) # HTU21D 온습도 센서 객체 생성

# GPIO 초기화
GPIO.setmode(GPIO.BCM) # BCM 핀 번호 체계 사용
GPIO.setwarnings(False) # GPIO 경고 비활성화
GPIO.setup(trig, GPIO.OUT) # 초음파 센서 TRIG 핀 출력으로 설정
GPIO.setup(echo, GPIO.IN) # 초음파 센서 ECHO 핀 입력으로 설정
GPIO.setup(led, GPIO.OUT) # LED 핀 출력으로 설정
GPIO.setup(button, GPIO.IN, GPIO.PUD_DOWN) # 버튼 핀 풀다운 저항 설정

# MCP3008 설정 (조도 센서를 위한 ADC)
mcp = Adafruit_MCP3008.MCP3008(clk=11, cs=8, miso=9, mosi=10)

# LED 제어 함수
def controlLED(on_off):
    GPIO.output(led, on_off) # LED 핀에 on_off 값 출력

# 초음파 센서를 이용한 거리 측정 함수
def measure_distance():
    time.sleep(0.2) # 센서 초기화 시간 대기
    GPIO.output(trig, 1) # TRIG 핀에 신호 출력
    time.sleep(0.00001) # 10µs 펄스 생성
    GPIO.output(trig, 0) # TRIG 핀 신호 종료
    
    # 초음파 송출 후 응답 대기
    while GPIO.input(echo) == 0:
        pulse_start = time.time() # 신호 시작 시간 기록
    while GPIO.input(echo) == 1:
        pulse_end = time.time() # 신호 종료 시간 기록
        
    # 펄스 지속 시간 계산
    pulse_duration = pulse_end - pulse_start
    # 거리를 계산 (음속: 340 m/s)
    distance = pulse_duration * 340 * 100 / 2 # cm로 변환 (왕복 시간 계산)
    return round(distance, 2) # 거리 값을 소수점 두 자리로 반환

# 조도 센서 데이터 읽기 함수
def getLight(channel=0): 
    return mcp.read_adc(channel) # 지정된 채널에서 ADC 값 읽기

# 온도 데이터 읽기 함수
def getTemperature():
    # HTU21D 센서를 통해 온도 데이터를 읽음. 
    return float(sensor.temperature)

# 습도 데이터 읽기 함수
def getHumidity():
    # HTU21D 센서를 통해 습도 데이터를 읽음. 
    return float(sensor.relative_humidity)

# GPIO 종료
def cleanup():
    # GPIO 설정을 정리하고 모든 핀을 초기 상태로 복원
    GPIO.cleanup()