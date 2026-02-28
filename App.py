from flask import Flask, render_template, request

app = Flask(__name__)

# 캐시된 정적 파일을 항상 갱신하도록 설정
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Index.html 템플릿 렌더링
@app.route('/')
def index(): 
    return render_template('Index.html') # Index.html을 클라이언트에 전달

# 플라스크 서버 실행
if __name__ == "__main__": 
    app.run(host='0.0.0.0', port=8080, debug=True)