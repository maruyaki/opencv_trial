import cv2, sys, glob, shutil

filepath = sys.argv[1]
#cap = cv2.VideoCapture(filepath)

files = glob.glob(filepath + '/*')

for filepath in files:
    print(filepath, end = ',')
    cap = cv2.VideoCapture(filepath)
    avg = None
    maxRatio = .0
    moveRecognizeRatio = 0.02
    moveRecognizeAvg = 0.005
    frameCount = 0
    moveRatioSum = .0

    # 頭15フレームは捨てる
    for num in range(15):
        ret, frame = cap.read()
        if not ret:
            break

    while True:
        #u 1フレームずつ取得する。
        ret, frame = cap.read()
        if not ret:
            if moveRatioSum / frameCount < moveRecognizeAvg:
                # 移動平均が閾値以下だったら動体なしとして終了
                print("NO MOVE,,{},{}".format(maxRatio, moveRatioSum / frameCount))
                shutil.copyfile(filepath, 'nm' + filepath.split('/')[-1])
            else:
                # 動体ありとして終了
                print("MOVE RECOGNIZED...Averagious move,,{},{}".format(maxRatio, moveRatioSum / frameCount))
                shutil.copyfile(filepath, 'm' + filepath.split('/')[-1])

            break

        # ノイズ除去処理
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


        # 動体を検知したら動体ありとして終了 
        if whiteRatio >= moveRecognizeRatio:
            print("MOVE RECOGNIZED,", whiteRatio)
            shutil.copyfile(filepath, 'm' + filepath.split('/')[-1])
            break

        moveRatioSum += whiteRatio 
        frameCount += 1

    cap.release()
