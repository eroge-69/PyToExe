import cv2
import numpy as np
from flask import Flask, request, send_file
from PIL import Image
import io

app = Flask(__name__)

def overlay_clothes(manikin_img, clothes_img):
    # Resize clothes to fit mannequin (simple center overlay for demo)
    manikin_h, manikin_w = manikin_img.shape[:2]
    clothes_img = cv2.resize(clothes_img, (manikin_w, int(manikin_h * 0.5)))
    # Place clothes at upper half of mannequin
    y_offset = int(manikin_h * 0.25)
    x_offset = 0
    # Create mask for clothes
    gray = cv2.cvtColor(clothes_img, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
    mask_inv = cv2.bitwise_not(mask)
    roi = manikin_img[y_offset:y_offset+clothes_img.shape[0], x_offset:x_offset+clothes_img.shape[1]]
    manikin_bg = cv2.bitwise_and(roi, roi, mask=mask_inv)
    clothes_fg = cv2.bitwise_and(clothes_img, clothes_img, mask=mask)
    dst = cv2.add(manikin_bg, clothes_fg)
    manikin_img[y_offset:y_offset+clothes_img.shape[0], x_offset:x_offset+clothes_img.shape[1]] = dst
    return manikin_img

@app.route('/adapt', methods=['POST'])
def adapt_clothes():
    manikin_file = request.files['manikin']
    clothes_file = request.files['clothes']
    manikin_img = cv2.imdecode(np.frombuffer(manikin_file.read(), np.uint8), cv2.IMREAD_COLOR)
    clothes_img = cv2.imdecode(np.frombuffer(clothes_file.read(), np.uint8), cv2.IMREAD_COLOR)
    result_img = overlay_clothes(manikin_img, clothes_img)
    # Convert to PIL and save to bytes
    result_pil = Image.fromarray(cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB))
    buf = io.BytesIO()
    result_pil.save(buf, format='JPEG')
    buf.seek(0)
    return send_file(buf, mimetype='image/jpeg', as_attachment=True, download_name='result.jpg')

if __name__ == '__main__':
    app.run(debug=True)