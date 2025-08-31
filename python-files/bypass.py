import binascii
from mitmproxy import http
import decrypt
import proto
import Login_pb2


aesUtils = decrypt.AESUtils()
protoUtils = proto.ProtobufUtils()


def hexToOctetStream(hex_str: str) -> bytes:
    return bytes.fromhex(hex_str)


def checkUIDExists(uid: str) -> bool:
    uid = uid.strip()
    try:
        with open("uid.txt", "r", encoding="utf-8") as file:
            for line in file:
                if line.strip() == uid:
                    return True
    except FileNotFoundError:
        print("Error: uid.txt not found.")
    return False


class MajorLoginInterceptor:
    def request(self, flow: http.HTTPFlow) -> None:

        if flow.request.method.upper() == "POST" and "/MajorLogin" in flow.request.path:
            enc_body = flow.request.content.hex()
            dec_body = aesUtils.decrypt_aes_cbc(enc_body)
            body = protoUtils.decode_protobuf(dec_body.hex(), Login_pb2.LoginReq)

            body.deviceData = "KqsHTxnXXUCG8sxXFVB2j0AUs3+0cvY/WgLeTdfTE/KPENeJPpny2EPnJDs8C8cBVMcd1ApAoCmM9MhzDDXabISdK31SKSFSr06eVCZ4D2Yj/C7G"
            body.reserved20 = b"\u0013RFC\u0007\u000e\\Q1"

            binary_data = body.SerializeToString()
            finalEncContent = aesUtils.encrypt_aes_cbc(
                hexToOctetStream(binary_data.hex())
            )
            flow.request.content = bytes.fromhex(finalEncContent.hex())

    def response(self, flow: http.HTTPFlow) -> None:
        if (
            flow.request.method.upper() == "POST"
            and "MajorLogin".lower() in flow.request.path.lower()
        ):

            respBody = flow.response.content.hex()
            decodedBody = protoUtils.decode_protobuf(respBody, Login_pb2.getUID)
            checkUID = checkUIDExists(str(decodedBody.uid))

            if not checkUID:
                flow.response.content = f"[ffffff] BUY THE UID BYPASS AND USE\n\n[FFFFFF]UID: {decodedBody.uid} .".encode()
                flow.response.status_code = 400
                return None


addons = [MajorLoginInterceptor()]
