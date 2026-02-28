let client = null; // MQTT 클라이언트 객체
let connectionFlag = false; // MQTT 연결 상태 플래그
const CLIENT_ID = "client_" + Math.random().toString(16).substr(2, 8); // 고유한 MQTT 클라이언트 ID 생성

// Chart.js 관련 설정 변수
let tempHumidityChart = null; // 온도/습도 차트
let movementChart = null; // 움직임 차트
let movementCount = 0; // 움직임 감지 횟수
let tempData = []; // 온도 데이터 배열
let humidData = []; // 습도 데이터 배열
let timeLabels = []; // 시간 라벨 배열

// 초기화 함수: 차트를 설정하고 생성
function initializeCharts() {
    const tempHumidityCtx = document.getElementById("tempHumidityChart").getContext("2d");
    const movementCtx = document.getElementById("movementChart").getContext("2d");

    // 온도/습도 차트 생성
    tempHumidityChart = new Chart(tempHumidityCtx, {
        type: "line",
        data: {
            labels: [],
            datasets: [
                {
                    label: "온도 (°C)", // 데이터 이름
                    borderColor: "rgba(255, 99, 132, 1)", // 선 색상
                    backgroundColor: "rgba(255, 99, 132, 0.2)", // 배경 색상
                    data: [], // 온도 데이터
                },
                {
                    label: "습도 (%)", // 데이터 이름
                    borderColor: "rgba(54, 162, 235, 1)",
                    backgroundColor: "rgba(54, 162, 235, 0.2)",
                    data: [], // 습도 데이터
                }
            ]
        },
        options: {
            responsive: false,
            maintainAspectRatio: false,
        }
    });

    // 움직임 차트 생성
    movementChart = new Chart(movementCtx, {
        type: "line",
        data: {
            labels: [],
            datasets: [
                {
                    label: "움직임 감지 횟수", // 데이터 이름
                    backgroundColor: "rgba(75, 192, 192, 0.2)", // 배경 색상
                    borderColor: "rgba(75, 192, 192, 1)", // 선 색상
                    data: [], // 움직임 데이터
                }
            ]
        },
        options: {
            responsive: false,
            maintainAspectRatio: false,
        }
    });
}

// MQTT 브로커에 연결
function connect() {
    if (connectionFlag) return; // 이미 연결된 경우 중단
    const brokerInput = document.getElementById("broker");
    let broker = brokerInput.value || brokerInput.placeholder; // 브로커 주소 입력
    const port = 9001; // MQTT 웹 소켓 기본 포트

    console.log(`Attempting to connect to MQTT broker at ${broker}:${port}`);

    // MQTT 클라이언트 생성
    client = new Paho.MQTT.Client(broker, Number(port), CLIENT_ID);

    // 콜백 등록
    client.onConnectionLost = onConnectionLost; // 연결 끊김 처리
    client.onMessageArrived = onMessageArrived; // 메시지 수신 처리

    // MQTT 브로커 연결 시도
    client.connect({
        onSuccess: onConnect, // 성공 시 호출
        onFailure: onConnectFailure, // 실패 시 호출
    });
}

// 연결 성공 시 호출
function onConnect() {
    const topics = ["light", "temp", "humid", "system_logs", "video_stream", "distance"];
    topics.forEach((topic) => {
        client.subscribe(topic); // 모든 토픽 구독
        console.log(`Successfully subscribed to topic: ${topic}`);
    });
    connectionFlag = true; // 연결 상태 업데이트
    addLogMessage("MQTT 연결 성공");
    initializeCharts(); // 차트 초기화
}

// 연결 끊김 처리
function onConnectionLost(responseObject) {
    if (responseObject.errorCode !== 0) {
        console.error("Connection Lost: " + responseObject.errorMessage);
        addLogMessage("연결이 끊어졌습니다: " + responseObject.errorMessage);
        connectionFlag = false; // 연결 상태 업데이트
    }
}

// 연결 실패 처리
function onConnectFailure(response) {
    console.error(`MQTT 연결 실패: ${response.errorMessage}`);
    addLogMessage(`MQTT 연결 실패: ${response.errorMessage}`);
}

// 메시지 수신 처리
function onMessageArrived(msg) {
    const topic = msg.destinationName; // 메시지의 토픽
    const payload = msg.payloadString; // 메시지 내용
    console.log(`Received message on topic '${topic}': ${payload}`);
    const now = new Date();
    const timestamp = now.toTimeString().split(" ")[0]; // 현재 시간 (시간: 분: 초)

    switch (topic) {
        case "light": // 조도 상태 업데이트
            updateElementText("day-night-status", parseInt(payload) <= 300 ? "지금은 밤입니다." : "지금은 낮입니다.");
            break;
        case "temp": // 온도 데이터 업데이트
            tempData.push(parseFloat(payload));
            timeLabels.push(timestamp);
            if (tempData.length > 10) tempData.shift(); // 데이터 크기 제한
            if (timeLabels.length > 10) timeLabels.shift();
            updateTempHumidityChart();
            updateElementText("temperature", `${payload} °C`);
            break;
        case "humid": // 습도 데이터 업데이트
            humidData.push(parseFloat(payload));
            if (humidData.length > 10) humidData.shift();
            updateTempHumidityChart();
            updateElementText("humidity", `${payload} %`);
            break;
        case "distance":
            handleDistanceUpdate(payload); // 거리 업데이트 처리
            break;
        case "system_logs":
            addLogMessage(payload); // 시스템 로그 추가
            break;
        case "video_stream":
            updateCameraStream(payload); // 카메라 스트림 업데이트
            break;
        default:
            console.warn(`Unknown topic received: ${topic}`);
    }
}

// 온도/습도 차트 업데이트
function updateTempHumidityChart() {
    if (!tempHumidityChart) return;
    tempHumidityChart.data.labels = timeLabels;
    tempHumidityChart.data.datasets[0].data = tempData;
    tempHumidityChart.data.datasets[1].data = humidData;
    tempHumidityChart.update();
}

// 움직임 차트 업데이트
function updateMovementChart() {
    if (!movementChart) return;
    movementChart.data.labels = timeLabels;
    movementChart.data.datasets[0].data.push(movementCount);
    if (movementChart.data.datasets[0].data.length > 10) {
        movementChart.data.datasets[0].data.shift();
    }
    movementChart.update();
}

// 스트리밍 화면 올리고 내리기
function handleDistanceUpdate(distance) {
    console.log(`Distance received: ${distance} cm`);
    if (distance <= 30) { // distancd가 30cm 이하라면
        movementCount++; // 움직임 횟수 증가시키고
        updateMovementChart();
        toggleCameraDisplay(true); // 카메라 화면 표시
    } else { // 30cm 초과라면
        toggleCameraDisplay(false); // 카메라 화면 숨김
    }
}

// 카메라 화면 토글
function toggleCameraDisplay(show) {
    const cameraDiv = document.querySelector(".camera-streaming"); // 카메라 스트리밍 영역 선택
    if (cameraDiv) {
        cameraDiv.style.display = show ? "block" : "none"; // 조건에 따라 화면 표시
    }
}

// 카메라 스트림 업데이트
function updateCameraStream(payload) {
    const imgElement = document.querySelector(".camera-streaming img"); // 카메라 스트림 이미지 엘리먼트 선택
    if (imgElement) {
        if (payload) {
            imgElement.src = `data:image/jpeg;base64,${payload}`; // base64 데이터를 이미지 소스로 설정
            imgElement.alt = "Streaming Active"; // 스트리밍 활성 상태로 텍스트 업데이트
        } else {
            imgElement.alt = "Streaming Not Available"; // 스트리밍 데이터가 없으면 표시
        }
    }
}

// HTML 요소 텍스트 업데이트
function updateElementText(id, text) {
    const element = document.getElementById(id); // id로 html 요소 선택
    if (element) element.innerText = text; // 선택된 요소 텍스트 변경
}

// 로그 메시지 추가
function addLogMessage(message) {
    const logContainer = document.getElementById("messages");
    if (!logContainer) return;

    const logLimit = 10; // 메시지 수 제한

    // 현재 날짜와 시간 가져오기
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0'); // 월은 0부터 시작하므로 +1 하였음
    const day = String(now.getDate()).padStart(2, '0');
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');

    const timestamp = `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`; // 타임스탬프 생성
    const logEntry = document.createElement("div"); // 새로운 div 요소 생성
    logEntry.textContent = `[${timestamp}] ${message}`; // 타임스탬프와 메시지 추가

    logContainer.appendChild(logEntry); // 로그 컨테이너에 추가

    while (logContainer.children.length > logLimit) { // 로그 개수 제한 확인
        logContainer.removeChild(logContainer.firstChild); // 가장 오래된 로그 삭제
    }
}

// MQTT 연결 종료
function disconnect() {
    if (!connectionFlag) return;
    client.disconnect();
    connectionFlag = false;
    addLogMessage("MQTT 연결 종료");
}