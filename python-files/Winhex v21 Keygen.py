import binascii
import datetime
import hashlib
import sys

sys.stdout = open('user.txt', 'w')
import random

#pip install pycryptodome
from Crypto.Cipher import AES
from Crypto.Util import Counter
from Crypto.Util.strxor import strxor

#winhex 21.2
PUB_KEY = bytes.fromhex('4DEFEAE49CF72587DEADB0E192EE26C2244563BD5B98461F5CDD4595932AB4FD')

#need a currect license to dec 
PRIVATE_KEY=bytes.fromhex('725D5C612CCC0FF538E919E4365F3C4900000000000000000000000000000000')

CTR_INIT_VALUE = bytes.fromhex('D8DE2B1AA3036D3241607571F1E7C14D')


'''
// X-Ways license file
 
Name: semthex
Addr: ru-board.com
Addr: RUSSIA
Data: 21C99167CC69236A2EB9540CF881EFF6
Data: 2376D8CC4E33860CF5A9E379945DA0BE
Cksm: 3DD34CCA
'''
def str2dt(time_str, format="%Y-%m-%d"):
    dt = datetime.datetime.strptime(time_str, format)
    return dt

def datetime_to_dos_date(dt) -> int:
    year = dt.year - 1980
    month = dt.month
    day = dt.day

    dos_date: int = (year << 9) | (month << 5) | day
    return dos_date

def dos_date_to_datetime(dos_date: int) -> str:
    day = dos_date & 0x1F
    month = (dos_date >> 5) & 0x0F
    year = ((dos_date >> 9) & 0x7F) + 1980

    # Create datetime object
    dt = datetime.datetime(year, month, day)
    
    # Returns the formatted time string
    return dt.strftime('%Y-%m-%d')







def sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()



def int_to_bytes(n: int, order='little') -> bytes:
    # Get the bit length of an integer
    bit_length = n.bit_length()
    # Calculate the minimum number of bytes required
    byte_length = (bit_length + 7) // 8
    # Convert to byte sequence, using big-endian byte order
    byte_array = n.to_bytes(byte_length, byteorder=order)
    return byte_array



def zero_pad(data, block_size=16, already_pad_add=False):
    # Calculate the number of bytes that need to be padded
    pad_len = block_size - (len(data) % block_size)
    if not already_pad_add:
        # If the data is already aligned, pad_len will be equal to block_size and no padding is needed.
        if pad_len == block_size:
            return data
    # To pad, use b'\0' to represent zero-byte padding
    padded_data = data + b"\0" * pad_len
    return padded_data


def aes_sha256_ctr(key: bytes, data: bytes, block: bytes = CTR_INIT_VALUE) -> bytes:
    aeskey_sz=len(key)
    if aeskey_sz!=32:
        key=zero_pad(key,32)

    aeskey = sha256(key)
    

    initvalue=int.from_bytes(block, 'little')
    counter = Counter.new(AES.block_size*8, initial_value=initvalue, little_endian=True)
    # print(counter.values())
    cipher = AES.new(key=aeskey, mode=AES.MODE_CTR, counter=counter)
    ret = cipher.encrypt(data)


    # count=len(data)//32
    # end_=int_to_bytes(initvalue+count)
    # print('[-]end counter:',end_.hex())
    #ctr mode--> enc==dec
    
    
    return ret



class LicInfo:
    def __init__(self,name:bytes,mail:bytes,addr:bytes,data1_hexstr:bytes=b'',data2_hexstr:bytes=b'',cksm_hexstr:bytes=b'') -> None:
        self.name=name
        self.mail=mail
        self.addr=addr
        if data1_hexstr:
            self.data1=bytes.fromhex(data1_hexstr.decode()) 
        else:
            x=LicInfo.gen_data1().hex()
            self.data1=bytes.fromhex(x)
        self.userinfo:bytes=LicInfo.mk_lic_userinfo(name,mail,addr)
        if data2_hexstr:
            self.data2=bytes.fromhex(data2_hexstr.decode())
        else:
            self.data2=self.calc_data2()
        self.lic_allinfo=LicInfo.mk_lic(name,mail,addr,self.data1,self.data2)    
        # print('lic info:',self.lic_info.hex())
        self.cksm=binascii.crc32(self.lic_allinfo+b'sector-aligned').to_bytes(4,'little')
        if cksm_hexstr:
            assert(self.cksm==bytes.fromhex(cksm_hexstr.decode()))

    @staticmethod
    def mk_lic_userinfo(name:bytes,mail:bytes,addr:bytes)->bytes:
        lic_info=zero_pad(name,81)
        lic_info+=zero_pad(mail,61)
        lic_info+=zero_pad(addr,61)
        return lic_info
    @staticmethod
    def mk_lic(name:bytes,mail:bytes,addr:bytes,data1:bytes,data2:bytes)->bytes:
        '''
        struct LicInfo
        {
        char name[81];
        char mailarr[61];
        char homeaddr[61];
        char keydata[32];
        };

        '''
        lic_info=LicInfo.mk_lic_userinfo(name,mail,addr)
        lic_info+=zero_pad(data1,16)
        lic_info+=zero_pad(data2,16)
        '''
        Cksm = binascii.crc32(lic_info+b'sector-aligned')
        print(hex(Cksm))
        '''
        return lic_info
    
    @staticmethod
    def gen_data1()->bytes:
        user_number=0xea6
        enddate=datetime_to_dos_date(str2dt('2028-08-27'))
        startdate=datetime_to_dos_date(str2dt('2024-08-10'))

        data1=b''

        # i_0_1= 0x1100
        i_0_1=random.randint(0,0xffff)
        
        

        OFFSET_DATE=0x4705
    
        # end To be less than 0x611Cu 07/09/2024 To be greater than 0x58E9u  08/28/2028
        # *(_WORD *)&name_718264.keydata[4] ^ *(_WORD *)&name_718264.keydata[6] ^ 0x159D; +0x4705
        # i_4_5=0x5544
        i_4_5=random.randint(0,0xffff)
        i_6_7=(enddate-OFFSET_DATE)^0x159d^i_4_5


        # i_9=random.randint(0,0xff)
        i_9=0x99


        
        # i_2_3=0x3322
        i_2_3=random.randint(0,0xffff)

        # start time
        # *(_WORD *)&name_718264.keydata[2] ^ *(_WORD *)&name_718264.keydata[12] ^ 0xEA69;+0x4705
        i_c_d=(startdate-OFFSET_DATE)^i_2_3^0xEA69
        i_c=i_c_d&0xff


        #user number <=3750u 0xea6
        # *(_WORD *)&name_718264.keydata[0xA] ^ *(_WORD *)&name_718264.keydata[2] ^ 0x69C5;
        i_a_b=user_number ^ i_2_3 ^ 0x69C5


        # calc type  
        # ; ==>0x610x61
        # (name_718264.keydata[12] ^ name_718264.keydata[8] ^ 0xB7) ^0x61
        i_8=i_c^0xB7 ^0x61

        # i_e=random.randint(0,0xff)
        i_e=0xee

        data1+=i_0_1.to_bytes(2,'little')+\
            i_2_3.to_bytes(2,'little')+\
            i_4_5.to_bytes(2,'little')+\
            i_6_7.to_bytes(2,'little')+\
            i_8.to_bytes(1,'little')+\
            i_9.to_bytes(1,'little')+\
            i_a_b.to_bytes(2,'little')+\
            i_c_d.to_bytes(2,'little')+\
            i_e.to_bytes(1,'little')
        
        '''
        # WinHex_v19.8
        unsigned int Random_check_sum_5C3358()
        {
        unsigned int result; // eax
        HANDLE CurrentProcess; // eax

        result = ((unsigned __int8)(lic_info_63EB5C.keydata[0xD] ^ lic_info_63EB5C.keydata[8])
                * (unsigned __int8)(lic_info_63EB5C.keydata[0xB] ^ lic_info_63EB5C.keydata[0xC])
                * ((unsigned __int8)lic_info_63EB5C.keydata[5] + (unsigned int)(unsigned __int8)lic_info_63EB5C.keydata[1])) >> 2;
        if ( (_BYTE)result == lic_info_63EB5C.keydata[0xF] )
            return result;
        if ( Delphi_Random_402EA8(3) == 2 )
            sub_5CC468();
        CurrentProcess = GetCurrentProcess();
        return TerminateProcess(CurrentProcess, 0);
        }
        '''
        i_f=  ((data1[0xD] ^ data1[8])
            * (data1[0xB] ^ data1[0xC])
            * (data1[5] + data1[1])
            ) >> 2
        data1+=(i_f&0xff).to_bytes(1,'little')     

        return data1


    def calc_data2(self)->bytes:
        #name + mail + addr   81+61+61=0xcb
        user_data = sha256(self.userinfo)

        lic_enc = aes_sha256_ctr(PUB_KEY, user_data)
        key2 = sha256(lic_enc+self.data1) 


        ret = aes_sha256_ctr(key2, PRIVATE_KEY)

        return ret[:16]

    def __repr__(self) -> str:
        ret='// X-Ways license file\n\n'
        ret+=f'Name: {self.name.decode()}\n'\
            f'Addr: {self.mail.decode()}\n'\
            f'Addr: {self.addr.decode()}\n'\
            f'Data: {self.data1.hex().upper()}\n'\
            f'Data: {self.data2.hex().upper()}\n'\
            f'Cksm: {self.cksm.hex().upper()}\n'
        return ret
    # def __str__(self) -> str:
    #     return self.__repr__()



def read_lic(user_txt_path:str):
    lines=[]
    with open(user_txt_path,'rb') as f:
        lines=f.readlines()
    infos=[]
    for x in lines:
        if b':' in x:
            temp=x.split(b':')[1].strip()
            infos.append(temp)
    return infos







def check_lic_data2(licpath=r'user.txt'):
    infos=read_lic(licpath)
    lic=LicInfo(*infos)

    lic_info=lic.lic_allinfo

    
    lic_data1 = lic.data1
    lic_data2 = lic.data2

    lic_info_sha256 = sha256(lic_info[:0xcb])

    
    print('AES1:')
    lic_enc = aes_sha256_ctr(PUB_KEY, lic_info_sha256)
    lic_enc_data1_sha256 = sha256(lic_enc+lic_data1)  

    print('AES2:')
    lic_enc2 = aes_sha256_ctr(lic_enc_data1_sha256, lic_data2)
    '''
    need 725D5C612CCC0FF538E919E4365F3C4900000000000000000000000000000000
    '''
    print('data2 correct?',PRIVATE_KEY==zero_pad(lic_enc2,32))


    # xordata = b''
    # with open(r'code_data.bin', 'rb') as f:
    #     xordata = f.read()
    # print('AES3:')
    # print('[*]target key:',lic_enc2.hex())
    # buf = aes_sha256_ctr(lic_enc2, xordata)


    # with open('dec.bin', 'wb') as f:
    #     f.write(buf)
    




def check_data1(data1:bytes):#=bytes.fromhex('21C99167CC69236A2EB9540CF881EFF6')

    type_15h=((data1[0xc]^data1[8]^0xb7) &0x1f) +0x14

    numb_3=(data1[0xc]^data1[8]^0xb7)>>5


    wfatdate=strxor(strxor(data1[4:6],data1[6:8]),b'\x9d\x15')

    i=int.from_bytes(wfatdate,'little')
    enddate=dos_date_to_datetime(i+0x4705)

    date=strxor(strxor(data1[2:4],data1[12:14]),b'\x69\xea')
    i=int.from_bytes(date,'little')
    date=dos_date_to_datetime(i+0x4705)


    number=strxor(strxor(data1[10:12],data1[2:4]),b'\xc5\x69')#max 3750

    sum=  ((data1[0xD] ^ data1[8])
          * (data1[0xB] ^ data1[0xC])
          * (data1[5] + data1[1])
          ) >> 2
    sum&=0xff




def kg(name:bytes=b'test',mail:bytes=b'hello@world.com',addr:bytes=b'xxxxxxx'):

    lic=LicInfo(name,mail,addr)

    check_data1(lic.data1)

    print(lic)
    pass

if __name__ == '__main__':

    
    kg(b'bunion',b'im@home.com',b'uk')

    # data1=LicInfo.gen_data1()
    # data1=bytes.fromhex('21C99167CC69236A2EB9540CF881EFF6')
    # check_data1( )

    # check_lic_data2('user.txt')
    pass

sys.stdout.close()
