import mediapipe as mp
import cv2
import time


class GestureEstimator:
    def __init__(self):
        time.sleep(0.2)  # ディレイ書けないとカメラが認識されにくくなる？
        self.video = cv2.VideoCapture(-1)

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            min_detection_confidence=0.7, min_tracking_confidence=0.5,
        )

    def __del__(self):
        self.video.release()

    def get_frame(self):
        # read()は、二つの値を返すので、success, imageの2つ変数で受けています。
        # OpencVはデフォルトでは raw imagesなので JPEGに変換
        # ファイルに保存する場合はimwriteを使用、メモリ上に格納したい時はimencodeを使用
        # cv2.imencode() は numpy.ndarray() を返すので .tobytes() で bytes 型に変換
        success, image = self.video.read()
        return image

    def get_pose_img(self, src_image):
        query_image = cv2.cvtColor(src_image, cv2.COLOR_BGR2RGB)
        results = self.hands.process(query_image)
        ret_flag = False
        ret_img = src_image
        ret_landmarks_list = []

        flag1 = results.multi_hand_landmarks is None
        flag2 = results.multi_handedness is None
        if flag1 or flag2:
            return ret_flag, ret_img, ret_landmarks_list

        tgt_image = src_image

        base_width, base_height = src_image.shape[1], src_image.shape[0]

        for hand_landmarks, handedness in zip(
            results.multi_hand_landmarks, results.multi_handedness
        ):

            landmark_buf = []

            # 結果取得
            # keypoint
            for landmark in hand_landmarks.landmark:
                x = min(int(landmark.x * base_width), base_width - 1)
                y = min(int(landmark.y * base_height), base_height - 1)
                landmark_buf.append((x, y))
                cv2.circle(tgt_image, (x, y), 3, (255, 0, 0), 5)

            # connection line
            for con_pair in mp.solutions.hands.HAND_CONNECTIONS:
                cv2.line(
                    tgt_image,
                    landmark_buf[con_pair[0].value],
                    landmark_buf[con_pair[1].value],
                    (255, 0, 0),
                    2,
                )

            ret_landmarks_list.append(landmark_buf)

        ret_flag = True
        ret_img = tgt_image
        return ret_flag, ret_img, ret_landmarks_list
