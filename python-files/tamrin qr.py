import qrcode
x=input()
qrcode.make(x).save(f'QR_{x}')
