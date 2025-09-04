
import cv2

from sys import argv


print(argv[1])

img = cv2.imread(argv[1], 2)
ret, bw_img = cv2.threshold(img, 50, 127, cv2.THRESH_BINARY)
count=0
count0=0
count1=0
for line in bw_img:
    if count==0:
        #print(line)
        for byte in line:
            if byte==0:
                count1+=1
                if count1 == 10:
                   print("1",end='')
                   count1=0
            if byte==127:
                count0+=1
                if count0 == 10:
                   print("0",end='')
                   count0=0
    count+=1
    if count==10:
        count=0
        print("")

"""
cv2.imshow("Binary", bw_img)
cv2.waitKey(0)
cv2.destroyAllWindows()
"""
