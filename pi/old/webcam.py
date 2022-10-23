import cv2

cam = cv2.VideoCapture(0)

while True:
    ret,image = cam.read()
    cv2.imshow("Imagetest",image)
    k = cv2.waitKey(1)
    if k!=-1:
        break

