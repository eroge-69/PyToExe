from flask import Flask, request, jsonify
from zeep import Client
import random
import traceback

app = Flask(__name__)

USERNAME = '9190292925'
PASSWORD = '28f61bm'
BODY_ID = 350206

@app.route('/send-otp', methods=['POST'])
def send_otp():
    try:
        data = request.get_json(force=True)
        print("Received JSON:", data)
        # اگر داده لیست بود اولین عنصرش رو بگیر
        if isinstance(data, list):
            data = data[0]

        phone = data.get('phone')
        code = data.get('code')

        if not phone:
            return jsonify({'status': 'error', 'message': 'Phone number is required'}), 400

        # اگر کد ارسال نشده، تولید کن
        if not code:
            code = str(random.randint(10000, 99999))

        client = Client('http://api.payamak-panel.com/post/Send.asmx?wsdl')
        response = client.service.SendByBaseNumber2(
            USERNAME,
            PASSWORD,
            code,    # کد به صورت رشته
            phone,
            BODY_ID
        )

        if response.isdigit() and len(response) > 15:
            return jsonify({'status': 'success', 'code': code})
        else:
            return jsonify({'status': 'fail', 'message': f'کد بازگشتی: {response}'}), 400

    except Exception as e:
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
