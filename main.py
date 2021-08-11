
# ref1: https://qiita.com/Kazuhito/items/222999f134b3b27418cd
# ref2: https://qiita.com/Gyutan/items/1f81afacc7cac0b07526
# main.py

from flask import Flask, render_template, Response
from gesture_estimator import GestureEstimator
import cv2
import time

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

    # "/" を呼び出したときには、indexが表示される。

def gen(ges_est):
    while True:
        frame = ges_est.get_frame()

        if frame is not None:
            frame = ges_est.get_pose_img(frame)
            ret, jpeg = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

# returnではなくジェネレーターのyieldで逐次出力。
# Generatorとして働くためにgenとの関数名にしている
# Content-Type（送り返すファイルの種類として）multipart/x-mixed-replace を利用。
# HTTP応答によりサーバーが任意のタイミングで複数の文書を返し、紙芝居的にレンダリングを切り替えさせるもの。
#（※以下に解説参照あり）

@app.route('/video_feed')
def video_feed():
    return Response(gen(GestureEstimator()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

# 0.0.0.0はすべてのアクセスを受け付けます。    
# webブラウザーには、「localhost:5000」と入力
