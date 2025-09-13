import cv2

 
print("hello")
img_path = "./tuccilong.png"
img = cv2.imread(img_path)
print(img)

cv2.imshow("teat", img)
cv2.waitKey(0)