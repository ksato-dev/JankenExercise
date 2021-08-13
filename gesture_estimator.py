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
        # OpenCVはデフォルトでは raw imagesなので JPEGに変換
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

    @classmethod
    def _judge_gu(cls, landms):
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

    @classmethod
    def _judge_choki(cls, landms):
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

    @classmethod
    def _judge_pa(cls, landms):
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

    @classmethod
    def recognize(cls, landms_list, curr_img):
        # global landms_list
        ret_your_hand = None
        for landms in landms_list:
            if cls._judge_gu(landms):
                ret_your_hand = 0
                break
            if cls._judge_choki(landms):
                ret_your_hand = 1
                break
            elif cls._judge_pa(landms):
                ret_your_hand = 2
                break
            else:
                ret_your_hand = -1

        return ret_your_hand
