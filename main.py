# ref1: https://qiita.com/Kazuhito/items/222999f134b3b27418cd
# ref2: https://qiita.com/Gyutan/items/1f81afacc7cac0b07526
# main.py

from gesture_estimator import GestureEstimator
import cv2
import os
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    send_from_directory,
    g,
    flash,
    Response,
)
import random

app = Flask(__name__)
recog_now = False
curr_img = None
pre_pc_hand = 0
pc_hand = 0
landms_list = None

pre_operation_msg = "以下に勝て"
operation_msg = pre_operation_msg


@app.route("/")
def index():
    return render_template("index.html")


# フロントエンドでフォルダを認識させるためのおまじないコード
SAVE_DIR = "image"
if not os.path.isdir(SAVE_DIR):
    os.mkdir(SAVE_DIR)


@app.route("/image/<path:filepath>")
def send_js(filepath):
    return send_from_directory(SAVE_DIR, filepath)


def gen(ges_est):
    # returnではなくジェネレーターのyieldで逐次出力。
    # Generatorとして働くためにgenとの関数名にしている
    # Content-Type（送り返すファイルの種類として）multipart/x-mixed-replace を利用。
    # HTTP応答によりサーバーが任意のタイミングで複数の文書を返し、紙芝居的にレンダリングを切り替えさせるもの。
    while True:
        frame = ges_est.get_frame()

        if frame is not None:
            global landms_list
            ret_flag, frame, landms_list = ges_est.get_pose_img(frame)
            _, jpeg = cv2.imencode(".jpg", frame)

            global recog_now, curr_img
            recog_now = ret_flag
            curr_img = jpeg

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + jpeg.tobytes() + b"\r\n\r\n"
            )


@app.route("/video_feed")
def video_feed():
    ges_est = GestureEstimator()
    return Response(gen(ges_est), mimetype="multipart/x-mixed-replace; boundary=frame")


def get_hand_img_data(hand):
    ret_hand_str = None
    ret_hand_img_path = None
    if hand == 0:
        ret_hand_str = "グー"
        ret_hand_img_path = "image/gu.png"
    elif hand == 1:
        ret_hand_str = "チョキ"
        ret_hand_img_path = "image/choki.png"
    elif hand == 2:
        ret_hand_str = "パー"
        ret_hand_img_path = "image/pa.png"

    return ret_hand_str, ret_hand_img_path


def judge_result(operation_msg, result):
    you_win = False
    if operation_msg == "以下に勝て" and result == "勝ち":
        you_win = True
    elif operation_msg == "以下に負けろ" and result == "負け":
        you_win = True
    elif operation_msg == "以下と引き分けろ" and result == "あいこ":
        you_win = True
    return you_win


def get_random_operation_msg():
    rand_val = random.randint(0, 2)
    operation_msg = None
    if rand_val == 0:
        operation_msg = "以下に勝て"
    elif rand_val == 1:
        operation_msg = "以下に負けろ"
    elif rand_val == 2:
        operation_msg = "以下と引き分けろ"
    print("operation_msg:", operation_msg)
    return operation_msg


def judge_gu(landms):
    # thumb = landms[1][1] > landms[2][1] > landms[3][1] > landms[4][1]
    index = landms[6][1] < landms[7][1] < landms[8][1]
    middle = landms[10][1] < landms[11][1] < landms[12][1]
    ring = landms[14][1] < landms[15][1] < landms[16][1]
    little = landms[18][1] < landms[19][1] < landms[20][1]
    print(index, middle, ring, little)
    if index and middle and ring and little:
        return True
    else:
        return False


def judge_choki(landms):
    # thumb = landms[1][1] > landms[2][1] > landms[3][1] > landms[4][1]
    index = landms[5][1] > landms[6][1] > landms[7][1] > landms[8][1]
    middle = landms[9][1] > landms[10][1] > landms[11][1] > landms[12][1]
    ring = landms[14][1] < landms[15][1] < landms[16][1]
    little = landms[18][1] < landms[19][1] < landms[20][1]
    print(index, middle, ring, little)
    if index and middle and ring and little:
        return True
    else:
        return False


def judge_pa(landms):
    # thumb = landms[1][1] > landms[2][1] > landms[3][1] > landms[4][1]
    index = landms[5][1] > landms[6][1] > landms[7][1] > landms[8][1]
    middle = landms[9][1] > landms[10][1] > landms[11][1] > landms[12][1]
    ring = landms[13][1] > landms[14][1] > landms[15][1] > landms[16][1]
    little = landms[17][1] > landms[18][1] > landms[19][1] > landms[20][1]
    print(index, middle, ring, little)
    if index and middle and ring and little:
        return True
    else:
        return False


# 0:gu, 1:choki, 2:pa
def judge_battle(myhand, pc_hand):
    if pc_hand == 0:
        if myhand == 0:
            result = "あいこ"
            result_img = "./image/aiko.gif"
        elif myhand == 1:
            result = "負け"
            result_img = "./image/make.gif"
        elif myhand == 2:
            result = "勝ち"
            result_img = "./image/kachi.gif"
    elif pc_hand == 1:
        if myhand == 0:
            result = "勝ち"
            result_img = "./image/kachi.gif"
        elif myhand == 1:
            result = "あいこ"
            result_img = "./image/aiko.gif"
        elif myhand == 2:
            result = "負け"
            result_img = "./image/make.gif"
    elif pc_hand == 2:
        if myhand == 0:
            result = "負け"
            result_img = "./image/make.gif"
        elif myhand == 1:
            result = "勝ち"
            result_img = "./image/kachi.gif"
        elif myhand == 2:
            result = "あいこ"
            result_img = "./image/aiko.gif"

    return result, result_img


def recognize(curr_img):
    global landms_list
    ret_your_hand = None
    for landms in landms_list:
        if judge_gu(landms):
            ret_your_hand = 0
            break
        if judge_choki(landms):
            ret_your_hand = 1
            break
        elif judge_pa(landms):
            ret_your_hand = 2
            break
        else:
            ret_your_hand = -1

    ret_hand_str, ret_img_path = get_hand_img_data(ret_your_hand)

    return ret_your_hand, ret_hand_str, ret_img_path


@app.route("/janken_core", methods=["GET", "POST"])
def janken():
    if request.method == "GET":
        return render_template("index.html")

    # global cnt
    if request.method == "POST":
        # myhand_img_path = None
        global recog_now, curr_img
        global pre_pc_hand, pc_hand
        global pre_operation_msg, operation_msg
        if recog_now:
            myhand, myhand_s, myhand_pic = recognize(curr_img)

            if myhand == -1:
                error_message = "ジェスチャーが認識されませんでした。グー、チョキ、パーのジェスチャーを入力してください。"
                return render_template("index.html", error_message=error_message)
            # cnt = cnt + 1
            # ここにコンピュータの手の文字列と画像を定義するコードをいれる
            pre_pc_hand = pc_hand
            pre_pc_hand_s, pre_pc_hand_pic = get_hand_img_data(pre_pc_hand)

            result, _ = judge_battle(myhand, pre_pc_hand)

            pre_operation_msg = operation_msg
            result_msg = None
            result_img = None
            if judge_result(pre_operation_msg, result):
                result_msg = "You Win！！"
                result_img = "./image/kachi.gif"
            else:
                result_msg = "You Lose..."
                result_img = "./image/make.gif"

            # 次の値をセット
            pc_hand = random.randint(0, 2)
            pc_hand_s, pc_hand_pic = get_hand_img_data(pc_hand)

            operation_msg = get_random_operation_msg()
            # print(operation_msg)

            return render_template(
                "index.html",
                # result=result,
                result_img=result_img,
                result_msg=result_msg,
                myhand_s=myhand_s,
                myhand_pic=myhand_pic,
                pc_hand_s=pc_hand_s,
                pre_pc_hand_s=pre_pc_hand_s,
                pc_hand_pic=pc_hand_pic,
                pre_pc_hand_pic=pre_pc_hand_pic,
                operation_msg=operation_msg,
                pre_operation_msg=pre_operation_msg,
            )

        else:
            pre_pc_hand = pc_hand
            pre_operation_msg = operation_msg
            pc_hand_s, pc_hand_pic = get_hand_img_data(pre_pc_hand)

            error_message = "ジェスチャーが認識されませんでした。グー、チョキ、パーのジェスチャーを入力してください。"
            return render_template(
                "index.html",
                error_message=error_message,
                pc_hand_s=pc_hand_s,
                pc_hand_pic=pc_hand_pic,
                operation_msg=operation_msg,
                pre_operation_msg=pre_operation_msg,
            )


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)

# 0.0.0.0はすべてのアクセスを受け付けます。
# webブラウザーには、「localhost:5000」と入力
