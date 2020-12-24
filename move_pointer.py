import cv2, sys

def mosaic(src, ratio=0.05):
    small = cv2.resize(src, None, fx=ratio, fy=ratio, interpolation=cv2.INTER_NEAREST)
    return cv2.resize(small, src.shape[:2][::-1], interpolation=cv2.INTER_NEAREST)

filepath = sys.argv[1]
cap = cv2.VideoCapture(filepath)
# Webカメラを使うときはこちら
# cap = cv2.VideoCapture(0)

avg = None
maxRatio = .0

# 頭15フレームは捨てる
for num in range(15):
    ret, frame = cap.read()
    if not ret:
        break

while True:
    # 1フレームずつ取得する。
    ret, frame = cap.read()
    if not ret:
        break

    # ノイズ除去処理
    #mFrame = mosaic(frame) 
    mFrame = cv2.GaussianBlur(frame, (15, 15), 0)

    # グレースケールに変換
    gray = cv2.cvtColor(mFrame, cv2.COLOR_BGR2GRAY)

    # 比較用のフレームを取得する
    if avg is None:
        avg = gray.copy().astype("float")
        continue


    # 現在のフレームと移動平均との差を計算
    cv2.accumulateWeighted(gray, avg, 0.6)
    frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))

    # デルタ画像を閾値処理を行う
    thresh = cv2.threshold(frameDelta, 3, 255, cv2.THRESH_BINARY)[1]

    # デルタ処理画像の白部分（動体部分）の割合を求める
    imageSize = thresh.size
    white = cv2.countNonZero(thresh)
    whiteRatio = white / imageSize
    if whiteRatio > maxRatio:
        maxRatio = whiteRatio

    # 画像の閾値に輪郭線を入れる
    contours, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    frame = cv2.drawContours(frame, contours, -1, (0, 255, 0), 3)

    # 結果を出力
    cv2.imshow("Frame", frame)
    print('\r', '{0:.4f} MAX:{1:.4f}'.format(whiteRatio, maxRatio), end='')
    key = cv2.waitKey(30)
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()
