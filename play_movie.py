import cv2

filepath = "144801.mkv"
cap = cv2.VideoCapture(filepath)
# Webカメラを使うときはこちら
# cap = cv2.VideoCapture(0)

while True:
    # 1フレームずつ取得する。
    ret, frame = cap.read()
    if not ret:
        break

    # 結果を出力
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(30)
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()
