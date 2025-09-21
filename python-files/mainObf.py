import time as _t,sys as _s,os as _o,threading as _th,ctypes as _ct,base64 as _b

_d=_b.b64decode
def _x1():
 if _s.platform.startswith(_d(b'd2lu').decode()):return _ct.windll.kernel32.IsDebuggerPresent()!=0
 elif _s.platform.startswith(_d(b'bGludXg=').decode()):
  try:
   if _ct.CDLL(_d(b'bGliYy5zby42').decode()).ptrace(0,0,None,None)==-1:return True
  except:pass
 return False
class _X2(_th.Thread):
 def __init__(self,t=2.):super().__init__(daemon=True);self.t=t;self.l=_t.time();self.r=True
 def run(self):
  while self.r:
   if _t.time()-self.l>self.t:_o._exit(1)
   _t.sleep(0.1)
 def p(self):self.l=_t.time()
 def s(self):self.r=False
_x3=lambda l:0 if not l else(ord(l[0])-1 if ord(l[0])%2==0 else ord(l[0])+1)+_x3(l[1:])
try:
 if _x1():1/0
 _w=_X2();_w.start()
 with open(_d(b'dGVzdC5qcGc=').decode(),_d(b'cmI=').decode()) as _f:
  _c=_f.read(35).decode();_w.p()
  if all([_c[0]==_d(b'IQ==').decode(),(sum(ord(_i)for _i in _c[1:7])/4-104==35 and _w.p() is None),(_t.asctime()[:3]==_d(b'U3Vu').decode() and _t.asctime()[14:16]==_d(b'NDk=').decode() and _w.p() is None),''.join(chr(ord(_i)+1)for _i in _c[7:27])==_d(b'UG9saXplaWF1dG90dWVyZ3JpZmY=').decode(),_x3(_c[27:32])%31==0]):
   _w.s();print(_d(b'WW91IGFyZSBpbiE=').decode())
  else:1/0
except:print(_d(b'Tm9wZQ==').decode())