print('Добро пожаловать в калькулятор сроков подачи арбитражных жалоб в ВС РФ ')

input_date = int(input("Ведите число определения кассационного суда округа:   "))
input_month = int(input("Введите месяц определения кассационного суда округа:   "))

if input_month > 12:
    print("ошибка")
if input_month < 1:
    print("ошибка")

if input_month == 1:
    input_month = 31    
    month = 28
    day = 0
if input_month == 2:
    input_month = 28  
    month = 31
    day = 31
if input_month == 3:
    input_month = 31
    month = 30
    day = 59
if input_month == 4: 
    input_month = 30
    month = 31
    day = 90
if input_month == 5: 
    input_month = 31
    month = 30
    day = 120
if input_month == 6: 
    input_month = 30
    month = 31
    day = 151
if input_month == 7: 
    input_month = 31
    month = 31
    day = 181
if input_month == 8: 
    input_month = 31
    month = 30
    day = 212
if input_month == 9: 
    input_month = 30
    month = 31
    day = 243
if input_month == 10: 
    input_month = 31
    month = 30
    day = 273
if input_month == 11: 
    input_month = 30
    month = 31
    day = 304
if input_month == 12: 
    input_month = 31
    month = 31
    day = 334

def first (a, b): # разница числа и колличества дней в месяце для опредения оставшихся дней после даты определения округа
    sum = a - b
    return sum

first1 = int(first(input_month, input_date))



def day1(a, b, c): # сумма разници дней в месяце определения округа, следующего месяца и колличества дней от первого числа месяца определения округа до даты определения
        sum = a + b + c 
        return sum
    
day2 = int(day1(first1, month, input_date))




if input_date == 1:
    day4 = int(input_date)
    day4 = 1
if input_date == 2:
    day4 = int(input_date)
    day4 = 2
if input_date == 3:
    day4 = int(input_date)
    day4 = 3
if input_date == 4:
    day4 = int(input_date)
    day4 = 4
if input_date == 5:
    day4 = int(input_date)
    day4 = 5
if input_date == 6:
    day4 = int(input_date)
    day4 = 6
if input_date == 7:
    day4 = int(input_date)
    day4 = 7
if input_date == 8:
    day4 = int(input_date)
    day4 = 8
if input_date == 9:
    day4 = int(input_date)
    day4 = 9
if input_date == 10:
    day4 = int(input_date)
    day4 = 10
if input_date == 11:
    day4 = int(input_date)
    day4 = 11
if input_date == 12:
    day4 = int(input_date)
    day4 = 12
if input_date == 13:
    day4 = int(input_date)
    day4 = 13
if input_date == 14:
    day4 = int(input_date)
    day4 = 14 
if input_date == 15:
    day4 = int(input_date)
    day4 = 15
if input_date == 16:
    day4 = int(input_date)
    day4 = 16
if input_date == 17:
    day4 = int(input_date)
    day4 = 17
if input_date == 18:
    day4 = int(input_date)
    day4 = 18
if input_date == 19:
    day4 = int(input_date)
    day4 = 19
if input_date == 20:
    day4 = int(input_date)
    day4 = 20
if input_date == 21:
    day4 = int(input_date)
    day4 = 21
if input_date == 22:
    day4 = int(input_date)
    day4 = 22
if input_date == 23:
    day4 = int(input_date)
    day4 = 23
if input_date == 24:
    day4 = int(input_date)
    day4 = 24
if input_date == 25:
    day4 = int(input_date)
    day4 = 25
if input_date == 26:
    day4 = int(input_date)
    day4 = 26
if input_date == 27:
    day4 = int(input_date)
    day4 = 27
if input_date == 28:
    day4 = int(input_date)
    day4 = 28
if input_date == 29:
    day4 = int(input_date)
    day4 = 29
if input_date == 30:
    day4 = int(input_date)
    day4 = 30
if input_date == 31:
    day4 = int(input_date)
    day4 = 31

def num(a, b,): # сумма дней двухмесячного срока и дней в месяце подачи, для определения месяца до целого
    sum = a + b
    return sum
numer = num(day2, day4)



def all(a, b): # сумма целых месяцев от месяца подачи до числа конца срока и месяцев предидущих, для определения дня в году 1/365
    sum = a + b
    return sum
resolt = all(numer, day)
print('Дата последнего дня для подачи кассационной жалобы в ВС РФ:    ')


# ЯНВАРЬ
if resolt == 1:
    print("01/01/2025 выходной день дата подачи до 09/01/2025")
if resolt == 2:
    print("02/01/2025 выходной день дата подачи до 09/01/2025")
if resolt == 3:
    print("03/01/2025 выходной день дата подачи до 09/01/2025")
if resolt == 4:
    print("04/01/2025 выходной день дата подачи до 09/01/2025")
if resolt == 5:
    print("05/01/2025 выходной день дата подачи до 09/01/2025")
if resolt == 6:
    print("06/01/2025 выходной день дата подачи до 09/01/2025")
if resolt == 7:
    print("07/01/2025 выходной день дата подачи до 09/01/2025")
if resolt == 8:
    print("08/01/2025 выходной день дата подачи до 09/01/2025")
if resolt == 9:
    print("09/01/2025")
if resolt == 10:
    print("10/01/2025")
if resolt == 11:
    print("11/01/2025 выходной день дата подачи до 13/01/2025")
if resolt == 12:
    print("12/01/2025 выходной день дата подачи до 13/01/2025")
if resolt == 13:
    print("13/01/2025")
if resolt == 14:
    print("14/01/2025")
if resolt == 15:
    print("15/01/2025")
if resolt == 16:
    print("16/01/2025")
if resolt == 17:
    print("17/01/2025")
if resolt == 18:
    print("18/01/2025 выходной день дата подачи до 20/01/2025")
if resolt == 19:
    print("19/01/2025 выходной день дата подачи до 20/01/2025")
if resolt == 20:
    print("20/01/2025")
if resolt == 21:
    print("21/01/2025")
if resolt == 22:
    print("22/01/2025")
if resolt == 23:
    print("23/01/2025")
if resolt == 24:
    print("24/01/2025")
if resolt == 25:
    print("25/01/2025 выходной день дата подачи до 27/01/2025")
if resolt == 26:
    print("26/01/2025 выходной день дата подачи до 27/01/2025")
if resolt == 27:
    print("27/01/2025")
if resolt == 28:
    print("28/01/2025")
if resolt == 29:
    print("29/01/2025")
if resolt == 30:
    print("30/01/2025")
if resolt == 31:
    print("31/01/2025")

# ФЕВРАЛЬ

if resolt == 32:
    print("01/02/2025 выходной день дата подачи до 03/02/2025")
if resolt == 33:
    print("01/02/2025 выходной день дата подачи до 03/02/2025")
if resolt == 34:
    print("03/02/2025")
if resolt == 35:
    print("04/02/2025")
if resolt == 36:
    print("05/02/2025")
if resolt == 37:
    print("06/02/2025")
if resolt == 38:
    print("07/02/2025")
if resolt == 39:
    print("08/02/2025 выходной день дата подачи до 10/02/2025")
if resolt == 40:
    print("09/02/2025 выходной день дата подачи до 10/02/2025")
if resolt == 41:
    print("10/02/2025")
if resolt == 42:
    print("11/02/2025")
if resolt == 43:
    print("12/02/2025")
if resolt == 44:
    print("13/02/2025")
if resolt == 45:
    print("14/02/2025")
if resolt == 46:
    print("15/02/2025 выходной день дата подачи до 17/02/2025")
if resolt == 47:
    print("16/02/2025 выходной день дата подачи до 17/02/2025")
if resolt == 48:
    print("17/02/2025")
if resolt == 49:
    print("18/02/2025")
if resolt == 50:
    print("19/02/2025")
if resolt == 51:
    print("20/02/2025")
if resolt == 52:
    print("21/02/2025")
if resolt == 53:
    print("22/02/2025 выходной день дата подачи до 24/02/2025")
if resolt == 54:
    print("23/02/2025 выходной день дата подачи до 24/02/2025")
if resolt == 55:
    print("24/02/2025")
if resolt == 56:
    print("25/02/2025")
if resolt == 57:
    print("26/02/2025")
if resolt == 58:
    print("27/02/2025")
if resolt == 59:
    print("28/02/2025")

# МАРТ

if resolt == 60:
    print("01/03/2025 выходной день дата подачи до 03/03/2025")
if resolt == 61:
    print("02/03/2025 выходной день дата подачи до 03/03/2025")
if resolt == 62:
    print("03/03/2025")
if resolt == 63:
    print("04/03/2025")
if resolt == 64:
    print("05/03/2025")
if resolt == 65:
    print("06/03/2025")
if resolt == 66:
    print("07/03/2025")
if resolt == 67:
    print("08/03/2025 выходной день дата подачи до 10/03/2025")
if resolt == 68:
    print("09/03/2025 выходной день дата подачи до 10/03/2025")
if resolt == 69:
    print("10/03/2025")
if resolt == 70:
    print("11/03/2025")
if resolt == 71:
    print("12/03/2025")
if resolt == 72:
    print("13/03/2025")
if resolt == 73:
    print("14/03/2025")
if resolt == 74:
    print("15/03/2025 выходной день дата подачи до 17/03/2025")
if resolt == 75:
    print("16/03/2025 выходной день дата подачи до 17/03/2025")
if resolt == 76:
    print("17/03/2025")
if resolt == 77:
    print("18/03/2025")
if resolt == 78:
    print("19/03/2025")
if resolt == 79:
    print("20/03/2025")
if resolt == 80:
    print("21/03/2025")
if resolt == 81:
    print("22/03/2025 выходной день дата подачи до 24/03/2025")
if resolt == 82:
    print("23/03/2025 выходной день дата подачи до 24/03/2025")
if resolt == 83:
    print("24/03/2025")
if resolt == 84:
    print("25/03/2025")
if resolt == 85:
    print("26/03/2025")
if resolt == 86:
    print("27/03/2025")
if resolt == 87:
    print("28/03/2025")
if resolt == 88:
    print("29/03/2025 выходной день дата подачи до 31/03/2025")
if resolt == 89:
    print("30/03/2025 выходной день дата подачи до 31/03/2025")
if resolt == 90:
    print("31/03/2025")

#АПРЕЛЬ

if resolt == 91:
    print("01/04/2025")
if resolt == 92:
    print("02/04/2025")
if resolt == 93:
    print("03/04/2025")
if resolt == 94:
    print("04/04/2025")
if resolt == 95:
    print("05/04/2025 выходной день дата подачи до 07/04/2025")
if resolt == 96:
    print("06/04/2025 выходной день дата подачи до 07/04/2025")
if resolt == 97:
    print("07/04/2025")
if resolt == 98:
    print("08/04/2025")
if resolt == 99:
    print("09/04/2025")
if resolt == 100:
    print("10/04/2025")
if resolt == 101:
    print("11/04/2025")
if resolt == 102:
    print("12/04/2025 выходной день дата подачи до 14/04/2025")
if resolt == 103:
    print("13/04/2025 выходной день дата подачи до 14/04/2025")
if resolt == 104:
    print("14/04/2025")
if resolt == 105:
    print("15/04/2025")
if resolt == 106:
    print("16/04/2025")
if resolt == 107:
    print("17/04/2025")
if resolt == 108:
    print("18/04/2025")
if resolt == 109:
    print("19/04/2025 выходной день дата подачи до 21/04/2025")
if resolt == 110:
    print("20/04/2025 выходной день дата подачи до 21/04/2025")
if resolt == 111:
    print("21/04/2025")
if resolt == 112:
    print("22/04/2025")
if resolt == 113:
    print("23/04/2025")
if resolt == 114:
    print("24/04/2025")
if resolt == 115:
    print("25/04/2025")
if resolt == 116:
    print("26/04/2025 выходной день дата подачи до 28/04/2025")
if resolt == 117:
    print("27/04/2025 выходной день дата подачи до 28/04/2025")
if resolt == 118:
    print("28/04/2025")
if resolt == 119:
    print("29/04/2025")
if resolt == 120:
    print("30/04/2025")

# МАЙ

if resolt == 121:
    print("01/05/2025 выходной день дата подачи до 05/05/2025")
if resolt == 122:
    print("02/05/2025 выходной день дата подачи до 05/05/2025")
if resolt == 123:
    print("03/05/2025 выходной день дата подачи до 05/05/2025")
if resolt == 124:
    print("04/05/2025 выходной день дата подачи до 05/05/2025")
if resolt == 125:
    print("05/05/2025")
if resolt == 126:
    print("06/05/2025")
if resolt == 127:
    print("07/05/2025")
if resolt == 128:
    print("08/05/2025 выходной день дата подачи до 12/05/2025")
if resolt == 129:
    print("09/05/2025 выходной день дата подачи до 12/05/2025")
if resolt == 130:
    print("10/05/2025 выходной день дата подачи до 12/05/2025")
if resolt == 131:
    print("11/05/2025 выходной день дата подачи до 12/05/2025")
if resolt == 132:
    print("12/05/2025")
if resolt == 133:
    print("13/05/2025")
if resolt == 134:
    print("14/05/2025")
if resolt == 135:
    print("15/05/2025")
if resolt == 136:
    print("16/05/2025")
if resolt == 137:
    print("17/05/2025 выходной день дата подачи до 19/05/2025")
if resolt == 138:
    print("18/05/2025 выходной день дата подачи до 19/05/2025")
if resolt == 139:
    print("19/05/2025")
if resolt == 140:
    print("20/05/2025")
if resolt == 141:
    print("21/05/2025")
if resolt == 142:
    print("22/05/2025")
if resolt == 143:
    print("23/05/2025")
if resolt == 144:
    print("24/05/2025 выходной день дата подачи до 26/05/2025")
if resolt == 145:
    print("25/05/2025 выходной день дата подачи до 26/05/2025")
if resolt == 146:
    print("26/05/2025")
if resolt == 147:
    print("27/05/2025")
if resolt == 148:
    print("28/05/2025")
if resolt == 149:
    print("29/05/2025")
if resolt == 150:
    print("30/05/2025")
if resolt == 151:
    print("31/05/2025 выходной день дата подачи до 02/06/2025")

#ИЮНЬ

if resolt == 152:
    print("01/06/2025 выходной день дата подачи до 02/06/2025")
if resolt == 153:
    print("02/06/2025")
if resolt == 154:
    print("03/06/2025")
if resolt == 155:
    print("04/06/2025")
if resolt == 156:
    print("05/06/2025")
if resolt == 157:
    print("06/06/2025")
if resolt == 158:
    print("07/06/2025 выходной день дата подачи до 09/06/2025")
if resolt == 159:
    print("08/06/2025 выходной день дата подачи до 09/06/2025")
if resolt == 160:
    print("09/06/2025")
if resolt == 161:
    print("10/06/2025")
if resolt == 162:
    print("11/06/2025")
if resolt == 163:
    print("12/06/2025 выходной день дата подачи до 16/06/2025")
if resolt == 164:
    print("13/06/2025 выходной день дата подачи до 16/06/2025")
if resolt == 165:
    print("14/06/2025 выходной день дата подачи до 16/06/2025")
if resolt == 166:
    print("15/06/2025 выходной день дата подачи до 16/06/2025")
if resolt == 167:
    print("16/06/2025")
if resolt == 168:
    print("17/06/2025")
if resolt == 169:
    print("18/06/2025")
if resolt == 170:
    print("19/06/2025")
if resolt == 171:
    print("20/06/2025")
if resolt == 172:
    print("21/06/2025 выходной день дата подачи до 23/06/2025")
if resolt == 173:
    print("22/06/2025 выходной день дата подачи до 23/06/2025")
if resolt == 174:
    print("23/06/2025")
if resolt == 175:
    print("24/06/2025")
if resolt == 176:
    print("25/06/2025")
if resolt == 177:
    print("26/06/2025")
if resolt == 178:
    print("27/06/2025")
if resolt == 179:
    print("28/06/2025 выходной день дата подачи до 30/06/2025")
if resolt == 180:
    print("29/06/2025 выходной день дата подачи до 30/06/2025")
if resolt == 181:
    print("30/06/2025")

#ИЮЛЬ

if resolt == 182:
    print("01/07/2025")
if resolt == 183:
    print("02/07/2025")
if resolt == 184:
    print("03/07/2025")
if resolt == 185:
    print("04/07/2025")
if resolt == 186:
    print("05/07/2025 выходной день дата подачи до 07/07/2025")
if resolt == 187:
    print("06/07/2025 выходной день дата подачи до 07/07/2025")
if resolt == 188:
    print("07/07/2025")
if resolt == 189:
    print("08/07/2025")
if resolt == 190:
    print("09/07/2025")
if resolt == 191:
    print("10/07/2025")
if resolt == 192:
    print("11/07/2025")
if resolt == 193:
    print("12/07/2025 выходной день дата подачи до 14/07/2025")
if resolt == 194:
    print("13/07/2025 выходной день дата подачи до 14/07/2025")
if resolt == 195:
    print("14/07/2025")
if resolt == 196:
    print("15/07/2025")
if resolt == 197:
    print("16/07/2025")
if resolt == 198:
    print("17/07/2025")
if resolt == 199:
    print("18/07/2025")
if resolt == 200:
    print("19/07/2025 выходной день дата подачи до 21/07/2025")
if resolt == 201:
    print("20/07/2025 выходной день дата подачи до 21/07/2025")
if resolt == 202:
    print("21/07/2025")
if resolt == 203:
    print("22/07/2025")
if resolt == 204:
    print("23/07/2025")
if resolt == 205:
    print("24/07/2025")
if resolt == 206:
    print("25/07/2025")
if resolt == 207:
    print("26/07/2025 выходной день дата подачи до 28/07/2025")
if resolt == 208:
    print("27/07/2025 выходной день дата подачи до 28/07/2025")
if resolt == 209:
    print("28/07/2025")
if resolt == 210:
    print("29/07/2025")
if resolt == 211:
    print("30/07/2025")
if resolt == 212:
    print("31/07/2025")

#АВГУСТ

if resolt == 213:
    print("01/08/2025")
if resolt == 214:
    print("02/08/2025 выходной день дата подачи до 04/08/2025")
if resolt == 215:
    print("03/08/2025 выходной день дата подачи до 04/08/2025")
if resolt == 216:
    print("04/08/2025")
if resolt == 217:
    print("05/08/2025")
if resolt == 218:
    print("06/08/2025")
if resolt == 219:
    print("07/08/2025")
if resolt == 220:
    print("08/08/2025")
if resolt == 221:
    print("09/08/2025 выходной день дата подачи до 11/08/2025")
if resolt == 222:
    print("10/08/2025 выходной день дата подачи до 11/08/2025")
if resolt == 223:
    print("11/08/2025")
if resolt == 224:
    print("12/08/2025")
if resolt == 225:
    print("13/08/2025")
if resolt == 226:
    print("14/08/2025")
if resolt == 227:
    print("15/08/2025")
if resolt == 228:
    print("16/08/2025 выходной день дата подачи до 18/08/2025")
if resolt == 229:
    print("17/08/2025 выходной день дата подачи до 18/08/2025")
if resolt == 230:
    print("18/08/2025")
if resolt == 231:
    print("19/08/2025")
if resolt == 232:
    print("20/08/2025")
if resolt == 233:
    print("21/08/2025")
if resolt == 234:
    print("22/08/2025")
if resolt == 235:
    print("23/08/2025 выходной день дата подачи до 25/08/2025")
if resolt == 236:
    print("24/08/2025 выходной день дата подачи до 25/08/2025")
if resolt == 237:
    print("25/08/2025")
if resolt == 238:
    print("26/08/2025")
if resolt == 239:
    print("27/08/2025")
if resolt == 240:
    print("28/08/2025")
if resolt == 241:
    print("29/08/2025")
if resolt == 242:
    print("30/08/2025 выходной день дата подачи до 01/09/2025")
if resolt == 243:
    print("31/08/2025 выходной день дата подачи до 01/09/2025")

#СЕНТЯБРЬ

if resolt == 244:
    print("01/09/2025")
if resolt == 245:
    print("02/09/2025")
if resolt == 246:
    print("03/09/2025")
if resolt == 247:
    print("04/09/2025")
if resolt == 248:
    print("05/09/2025")
if resolt == 249:
    print("06/09/2025 выходной день дата подачи до 08/09/2025")
if resolt == 250:
    print("07/09/2025 выходной день дата подачи до 08/09/2025")
if resolt == 251:
    print("08/09/2025")
if resolt == 252:
    print("09/09/2025")
if resolt == 253:
    print("10/09/2025")
if resolt == 254:
    print("11/09/2025")
if resolt == 255:
    print("12/09/2025")
if resolt == 256:
    print("13/09/2025 выходной день дата подачи до 01/09/2025")
if resolt == 257:
    print("14/09/2025 выходной день дата подачи до 01/09/2025")
if resolt == 258:
    print("15/09/2025")
if resolt == 259:
    print("16/09/2025")
if resolt == 260:
    print("17/09/2025")
if resolt == 261:
    print("18/09/2025")
if resolt == 262:
    print("19/09/2025")
if resolt == 263:
    print("20/09/2025 выходной день дата подачи до 22/09/2025")
if resolt == 264:
    print("21/09/2025 выходной день дата подачи до 22/09/2025")
if resolt == 265:
    print("22/09/2025")
if resolt == 266:
    print("23/09/2025")
if resolt == 267:
    print("24/09/2025")
if resolt == 268:
    print("25/09/2025")
if resolt == 269:
    print("26/09/2025")
if resolt == 270:
    print("27/09/2025 выходной день дата подачи до 29/09/2025")
if resolt == 271:
    print("28/09/2025 выходной день дата подачи до 29/09/2025")
if resolt == 272:
    print("29/09/2025")
if resolt == 273:
    print("30/09/2025")

#ОКТЯБРЬ

if resolt == 274:
    print("01/10/2025")
if resolt == 275:
    print("02/10/2025")
if resolt == 276:
    print("03/10/2025")
if resolt == 277:
    print("04/10/2025 выходной день дата подачи до 06/10/2025")
if resolt == 278:
    print("05/10/2025 выходной день дата подачи до 06/10/2025")
if resolt == 279:
    print("06/10/2025")
if resolt == 280:
    print("07/10/2025")
if resolt == 281:
    print("08/10/2025")
if resolt == 282:
    print("09/10/2025")
if resolt == 283:
    print("10/10/2025")
if resolt == 284:
    print("11/10/2025 выходной день дата подачи до 13/10/2025")
if resolt == 285:
    print("12/10/2025 выходной день дата подачи до 13/10/2025")
if resolt == 286:
    print("13/10/2025")
if resolt == 287:
    print("14/10/2025")
if resolt == 288:
    print("15/10/2025")
if resolt == 289:
    print("16/10/2025")
if resolt == 290:
    print("17/10/2025")
if resolt == 291:
    print("18/10/2025 выходной день дата подачи до 20/10/2025")
if resolt == 292:
    print("19/10/2025 выходной день дата подачи до 20/10/2025")
if resolt == 293:
    print("20/10/2025")
if resolt == 294:
    print("21/10/2025")
if resolt == 295:
    print("22/10/2025")
if resolt == 296:
    print("23/10/2025")
if resolt == 297:
    print("24/10/2025")
if resolt == 298:
    print("25/10/2025 выходной день дата подачи до 27/10/2025")
if resolt == 299:
    print("26/10/2025 выходной день дата подачи до 27/10/2025")
if resolt == 300:
    print("27/10/2025")
if resolt == 301:
    print("28/10/2025")
if resolt == 302:
    print("29/10/2025")
if resolt == 303:
    print("30/10/2025")
if resolt == 304:
    print("31/10/2025")

#НОЯБРЬ

if resolt == 305:
    print("01/11/2025 выходной день дата подачи до 05/11/2025")
if resolt == 306:
    print("02/11/2025 выходной день дата подачи до 05/11/2025")
if resolt == 307:
    print("03/11/2025 выходной день дата подачи до 05/11/2025")
if resolt == 308:
    print("04/11/2025 выходной день дата подачи до 05/11/2025")
if resolt == 309:
    print("05/11/2025")
if resolt == 310:
    print("06/11/2025")
if resolt == 311:
    print("07/11/2025")
if resolt == 312:
    print("08/11/2025 выходной день дата подачи до 10/11/2025")
if resolt == 313:
    print("09/11/2025 выходной день дата подачи до 10/11/2025")
if resolt == 314:
    print("10/11/2025")
if resolt == 315:
    print("11/11/2025")
if resolt == 316:
    print("12/1/2025")
if resolt == 317:
    print("13/11/2025")
if resolt == 318:
    print("14/11/2025")
if resolt == 319:
    print("15/11/2025 выходной день дата подачи до 17/11/2025")
if resolt == 320:
    print("16/11/2025 выходной день дата подачи до 17/11/2025")
if resolt == 321:
    print("17/11/2025")
if resolt == 322:
    print("18/11/2025")
if resolt == 323:
    print("19/11/2025")
if resolt == 324:
    print("20/11/2025")
if resolt == 325:
    print("21/11/2025")
if resolt == 326:
    print("22/11/2025 выходной день дата подачи до 24/11/2025")
if resolt == 327:
    print("23/11/2025 выходной день дата подачи до 24/11/2025")
if resolt == 328:
    print("24/11/2025")
if resolt == 329:
    print("25/11/2025")
if resolt == 330:
    print("26/11/2025")
if resolt == 331:
    print("27/11/2025")
if resolt == 332:
    print("28/11/2025")
if resolt == 333:
    print("29/11/2025 выходной день дата подачи до 01/12/2025")
if resolt == 334:
    print("30/11/2025 выходной день дата подачи до 01/12/2025")

#ДЕКАБРЬ

if resolt == 335:
    print("01/12/2025")
if resolt == 336:
    print("02/12/2025")
if resolt == 337:
    print("03/12/2025")
if resolt == 338:
    print("04/12/2025")
if resolt == 339:
    print("05/12/2025")
if resolt == 340:
    print("06/12/2025 выходной день дата подачи до 08/12/2025")
if resolt == 341:
    print("07/12/2025 выходной день дата подачи до 08/12/2025")
if resolt == 342:
    print("08/12/2025")
if resolt == 343:
    print("09/12/2025")
if resolt == 344:
    print("10/12/2025")
if resolt == 345:
    print("11/12/2025")
if resolt == 346:
    print("12/12/2025")
if resolt == 347:
    print("13/12/2025 выходной день дата подачи до 15/12/2025")
if resolt == 348:
    print("14/12/2025 выходной день дата подачи до 15/12/2025")
if resolt == 349:
    print("15/12/2025")
if resolt == 350:
    print("16/12/2025")
if resolt == 351:
    print("17/12/2025")
if resolt == 352:
    print("18/12/2025")
if resolt == 353:
    print("19/12/2025")
if resolt == 354:
    print("20/12/2025 выходной день дата подачи до 22/12/2025")
if resolt == 355:
    print("21/12/2025 выходной день дата подачи до 22/12/2025")
if resolt == 356:
    print("22/12/2025")
if resolt == 357:
    print("23/12/2025")
if resolt == 358:
    print("24/12/2025")
if resolt == 359:
    print("25/12/2025")
if resolt == 360:
    print("26/12/2025")
if resolt == 361:
    print("27/12/2025 выходной день дата подачи до 29/12/2025")
if resolt == 362:
    print("28/12/2025 выходной день дата подачи до 29/12/2025")
if resolt == 363:
    print("29/12/2025")
if resolt == 364:
    print("30/12/2025")
if resolt == 365:
    print("31/12/2025 выходной день дата подачи до 12/01/2026")


    # 2026 ГОД

    # ЯНВАРЬ
if resolt == 366:
    print("01/01/2026 выходной день дата подачи до 12/01/2026")
if resolt == 367:
    print("02/01/2026 выходной день дата подачи до 12/01/2026")
if resolt == 368:
    print("03/01/2026 выходной день дата подачи до 12/01/2026")
if resolt == 369:
    print("04/01/2026 выходной день дата подачи до 12/01/2026")
if resolt == 370:
    print("05/01/2026 выходной день дата подачи до 12/01/2026")
if resolt == 371:
    print("06/01/2026 выходной день дата подачи до 12/01/2026")
if resolt == 372:
    print("07/01/2026 выходной день дата подачи до 12/01/2026")
if resolt == 373:
    print("08/01/2026 выходной день дата подачи до 12/01/2026")
if resolt == 374:
    print("09/01/2026 выходной день дата подачи до 12/01/2026")
if resolt == 375:
    print("10/01/2026 выходной день дата подачи до 12/01/2026")
if resolt == 376:
    print("11/01/2026 выходной день дата подачи до 12/01/2026")
if resolt == 377:
    print("12/01/2026")
if resolt == 378:
    print("13/01/2026")
if resolt == 379:
    print("14/01/2026")
if resolt == 380:
    print("15/01/2026")
if resolt == 381:
    print("16/01/2026")
if resolt == 382:
    print("17/01/2026 выходной день дата подачи до 19/01/2026")
if resolt == 383:
    print("18/01/2026 выходной день дата подачи до 19/01/2026")
if resolt == 384:
    print("19/01/2026")
if resolt == 385:
    print("20/01/2026")
if resolt == 386:
    print("21/01/2026")
if resolt == 387:
    print("22/01/2026")
if resolt == 388:
    print("23/01/2026")
if resolt == 389:
    print("24/01/2026 выходной день дата подачи до 26/01/2026")
if resolt == 390:
    print("25/01/2026 выходной день дата подачи до 26/01/2026")
if resolt == 391:
    print("26/01/2026")
if resolt == 392:
    print("27/01/2026")
if resolt == 393:
    print("28/01/2026")
if resolt == 394:
    print("29/01/2026")
if resolt == 395:
    print("30/01/2026")
if resolt == 396:
    print("31/01/2026 выходной день дата подачи до 02/02/2026")

# ФЕВРАЛЬ

if resolt == 397:
    print("01/02/2026 выходной день дата подачи до 02/02/2026")
if resolt == 398:
    print("01/02/2026")
if resolt == 399:
    print("03/02/2026")
if resolt == 400:
    print("04/02/2026")
if resolt == 401:
    print("05/02/2026")
if resolt == 402:
    print("06/02/2026")
if resolt == 403:
    print("07/02/2026 выходной день дата подачи до 09/02/2026")
if resolt == 404:
    print("08/02/2026 выходной день дата подачи до 09/02/2026")
if resolt == 405:
    print("09/02/2026")
if resolt == 406:
    print("10/02/2026")
if resolt == 407:
    print("11/02/2026")
if resolt == 408:
    print("12/02/2026")
if resolt == 409:
    print("13/02/2026")
if resolt == 410:
    print("14/02/2026 выходной день дата подачи до 16/02/2026")
if resolt == 411:
    print("15/02/2026 выходной день дата подачи до 16/02/2026")
if resolt == 412:
    print("16/02/2026")
if resolt == 413:
    print("17/02/2026")
if resolt == 414:
    print("18/02/2026")
if resolt == 415:
    print("19/02/2026")
if resolt == 416:
    print("20/02/2026")
if resolt == 417:
    print("21/02/2026 выходной день дата подачи до 24/02/2026")
if resolt == 418:
    print("22/02/2026 выходной день дата подачи до 24/02/2026")
if resolt == 419:
    print("23/02/2026 выходной день дата подачи до 24/02/2026")
if resolt == 420:
    print("24/02/2026")
if resolt == 421:
    print("25/02/2026")
if resolt == 422:
    print("26/02/2026")
if resolt == 423:
    print("27/02/2026")
if resolt == 424:
    print("28/02/2026 выходной день дата подачи до 02/03/2026")

# МАРТ

if resolt == 425:
    print("01/03/2026 выходной день дата подачи до 02/03/2026")
if resolt == 426:
    print("02/03/2026")
if resolt == 427:
    print("03/03/2026")
if resolt == 428:
    print("04/03/2026")
if resolt == 429:
    print("05/03/2026")
if resolt == 430:
    print("06/03/2026")
if resolt == 431:
    print("07/03/2026 выходной день дата подачи до 10/03/2026")
if resolt == 432:
    print("08/03/2026 выходной день дата подачи до 10/03/2026")
if resolt == 433:
    print("09/03/2026 выходной день дата подачи до 10/03/2026")
if resolt == 434:
    print("10/03/2026")
if resolt == 435:
    print("11/03/2026")
if resolt == 436:
    print("12/03/2026")
if resolt == 437:
    print("13/03/2026")
if resolt == 438:
    print("14/03/2026 выходной день дата подачи до 16/03/2026")
if resolt == 439:
    print("15/03/2026 выходной день дата подачи до 16/03/2026")
if resolt == 440:
    print("16/03/2026")
if resolt == 441:
    print("17/03/2026")
if resolt == 442:
    print("18/03/2026")
if resolt == 443:
    print("19/03/2026")
if resolt == 444:
    print("20/03/2026")
if resolt == 445:
    print("21/03/2026 выходной день дата подачи до 23/03/2026")
if resolt == 446:
    print("22/03/2026 выходной день дата подачи до 23/03/2026")
if resolt == 447:
    print("23/03/2026")
if resolt == 448:
    print("24/03/2026")
if resolt == 449:
    print("25/03/2026")
if resolt == 450:
    print("26/03/2026")
if resolt == 451:
    print("27/03/2026")
if resolt == 452:
    print("28/03/2026 выходной день дата подачи до 30/03/2026")
if resolt == 453:
    print("29/03/2026 выходной день дата подачи до 30/03/2026")
if resolt == 454:
    print("30/03/2026")
if resolt == 455:
    print("31/03/2026")

#АПРЕЛЬ

if resolt == 456:
    print("01/04/2026")
if resolt == 457:
    print("02/04/2026")
if resolt == 458:
    print("03/04/2026")
if resolt == 459:
    print("04/04/2026 выходной день дата подачи до 06/04/2026")
if resolt == 460:
    print("05/04/2026 выходной день дата подачи до 06/04/2026")
if resolt == 461:
    print("06/04/2026")
if resolt == 462:
    print("07/04/2026")
if resolt == 463:
    print("08/04/2026")
if resolt == 464:
    print("09/04/2026")
if resolt == 465:
    print("10/04/2026")
if resolt == 466:
    print("11/04/2026 выходной день дата подачи до 13/04/2026")
if resolt == 467:
    print("12/04/2026 выходной день дата подачи до 13/04/2026")
if resolt == 468:
    print("13/04/2026")
if resolt == 469:
    print("14/04/2026")
if resolt == 470:
    print("15/04/2026")
if resolt == 471:
    print("16/04/2026")
if resolt == 472:
    print("17/04/2026")
if resolt == 473:
    print("18/04/2026 выходной день дата подачи до 20/04/2026")
if resolt == 474:
    print("19/04/2026 выходной день дата подачи до 20/04/2026")
if resolt == 475:
    print("20/04/2026")
if resolt == 476:
    print("21/04/2026")
if resolt == 477:
    print("22/04/2026")
if resolt == 478:
    print("23/04/2026")
if resolt == 479:
    print("24/04/2026")
if resolt == 480:
    print("25/04/2026 выходной день дата подачи до 27/04/2026")
if resolt == 481:
    print("26/04/2026 выходной день дата подачи до 27/04/2026")
if resolt == 482:
    print("27/04/2026")
if resolt == 483:
    print("28/04/2026")
if resolt == 484:
    print("29/04/2026")
if resolt == 485:
    print("30/04/2026")

# МАЙ

if resolt == 486:
    print("01/05/2026 выходной день дата подачи до 04/05/2026")
if resolt == 487:
    print("02/05/2026 выходной день дата подачи до 04/05/2026")
if resolt == 488:
    print("03/05/2026 выходной день дата подачи до 04/05/2026")
if resolt == 489:
    print("04/05/2026")
if resolt == 490:
    print("05/05/2026")
if resolt == 491:
    print("06/05/2026")
if resolt == 492:
    print("07/05/2026")
if resolt == 493:
    print("08/05/2026")
if resolt == 494:
    print("09/05/2026 выходной день дата подачи до 11/05/2026")
if resolt == 495:
    print("10/05/2026 выходной день дата подачи до 11/05/2026")
if resolt == 496:
    print("11/05/2026")
if resolt == 497:
    print("12/05/2026")
if resolt == 498:
    print("13/05/2026")
if resolt == 499:
    print("14/05/2026")
if resolt == 500:
    print("15/05/2026")
if resolt == 501:
    print("16/05/2026 выходной день дата подачи до 18/05/2026")
if resolt == 502:
    print("17/05/2026 выходной день дата подачи до 18/05/2026")
if resolt == 503:
    print("18/05/2026")
if resolt == 504:
    print("19/05/2026")
if resolt == 505:
    print("20/05/2026")
if resolt == 506:
    print("21/05/2026")
if resolt == 507:
    print("22/05/2026")
if resolt == 508:
    print("23/05/2026 выходной день дата подачи до 25/05/2026")
if resolt == 509:
    print("24/05/2026 выходной день дата подачи до 25/05/2026")
if resolt == 510:
    print("25/05/2026")
if resolt == 511:
    print("26/05/2026")
if resolt == 512:
    print("27/05/2026")
if resolt == 513:
    print("28/05/2026")
if resolt == 514:
    print("29/05/2026")
if resolt == 515:
    print("30/05/2026 выходной день дата подачи до 01/06/2026")
if resolt == 516:
    print("31/05/2026 выходной день дата подачи до 01/06/2026")

#ИЮНЬ

if resolt == 517:
    print("01/06/2026")
if resolt == 518:
    print("02/06/2026")
if resolt == 519:
    print("03/06/2026")
if resolt == 520:
    print("04/06/2026")
if resolt == 521:
    print("05/06/2026")
if resolt == 522:
    print("06/06/2026 выходной день дата подачи до 08/06/2026")
if resolt == 523:
    print("07/06/2026 выходной день дата подачи до 08/06/2026")
if resolt == 524:
    print("08/06/2026")
if resolt == 525:
    print("09/06/2026")
if resolt == 526:
    print("10/06/2026")
if resolt == 527:
    print("11/06/2026")
if resolt == 528:
    print("12/06/2026 выходной день дата подачи до 15/06/2026")
if resolt == 529:
    print("13/06/2026 выходной день дата подачи до 15/06/2026")
if resolt == 530:
    print("14/06/2026 выходной день дата подачи до 15/06/2026")
if resolt == 531:
    print("15/06/2026")
if resolt == 532:
    print("16/06/2026")
if resolt == 533:
    print("17/06/2026")
if resolt == 534:
    print("18/06/2026")
if resolt == 535:
    print("19/06/2026")
if resolt == 536:
    print("20/06/2026 выходной день дата подачи до 22/06/2026")
if resolt == 537:
    print("21/06/2026 выходной день дата подачи до 22/06/2026")
if resolt == 538:
    print("22/06/2026")
if resolt == 539:
    print("23/06/2026")
if resolt == 540:
    print("24/06/2026")
if resolt == 541:
    print("25/06/2026")
if resolt == 542:
    print("26/06/2026")
if resolt == 543:
    print("27/06/2026 выходной день дата подачи до 29/06/2026")
if resolt == 544:
    print("28/06/2026 выходной день дата подачи до 29/06/2026")
if resolt == 545:
    print("29/06/2026")
if resolt == 546:
    print("30/06/2026")

#ИЮЛЬ

if resolt == 547:
    print("01/07/2026")
if resolt == 548:
    print("02/07/2026")
if resolt == 549:
    print("03/07/2026")
if resolt == 550:
    print("04/07/2026 выходной день дата подачи до 06/07/2026")
if resolt == 551:
    print("05/07/2026 выходной день дата подачи до 06/07/2026")
if resolt == 552:
    print("06/07/2026")
if resolt == 553:
    print("07/07/2026")
if resolt == 554:
    print("08/07/2026")
if resolt == 555:
    print("09/07/2026")
if resolt == 556:
    print("10/07/2026")
if resolt == 557:
    print("11/07/2026 выходной день дата подачи до 13/07/2026")
if resolt == 558:
    print("12/07/2026 выходной день дата подачи до 13/07/2026")
if resolt == 559:
    print("13/07/2026")
if resolt == 560:
    print("14/07/2026")
if resolt == 561:
    print("15/07/2026")
if resolt == 562:
    print("16/07/2026")
if resolt == 563:
    print("17/07/2026")
if resolt == 564:
    print("18/07/2026 выходной день дата подачи до 20/07/2026")
if resolt == 565:
    print("19/07/2026 выходной день дата подачи до 20/07/2026")
if resolt == 566:
    print("20/07/2026")
if resolt == 567:
    print("21/07/2026")
if resolt == 568:
    print("22/07/2026")
if resolt == 569:
    print("23/07/2026")
if resolt == 570:
    print("24/07/2026")
if resolt == 571:
    print("25/07/2026 выходной день дата подачи до 27/07/2026")
if resolt == 572:
    print("26/07/2026 выходной день дата подачи до 27/07/2026")
if resolt == 573:
    print("27/07/2026")
if resolt == 574:
    print("28/07/2026")
if resolt == 575:
    print("29/07/2026")
if resolt == 576:
    print("30/07/2026")
if resolt == 577:
    print("31/07/2026")

print('В случае пропуска срока, возможно подать ходатайство о восстановлении пропущенного срока, в таком случае ваш срок будет составлять 6 месяцев с даты вынесения определения кассационного суда округа')


input_date2 = int(input("Ведите число подачи жалобы в ВС РФ:   "))
input_month2 = int(input("Введите месяц подачи жалобы в ВС РФ:   "))


if input_month2 == 1:
    input_month2 = 31    
    l_month = 0
if input_month2 == 2:
    input_month2 = 28  
    l_month = 31
if input_month2 == 3:
    input_month2 = 31
    l_month = 59
if input_month2 == 4: 
    input_month2 = 30
    l_month = 90
if input_month2 == 5: 
    input_month2 = 31
    l_month = 120
if  input_month2 == 6: 
    input_month2 = 30
    l_month = 151
if input_month2 == 7: 
    input_month2 = 31
    l_month = 181
if input_month2 == 8: 
    input_month2 = 31
    l_month = 212
if input_month2 == 9: 
    input_month2 = 30
    l_month = 243
if input_month2 == 10: 
    input_month2 = 31
    l_month = 273
if input_month2 == 11: 
    input_month2 = 30
    l_month = 304
if input_month2 == 12: 
    input_month2 = 31
    l_month = 334


def VSRF(a,b): # сумма даты подачи жалобы в ВСРФ и месяцев целых предидущих для определения дня в году 1/365 
    sum = a + b
    return sum
VSRF1 = int(VSRF(input_date2, l_month))



# остаток срока 
def Dif(a,b): # разница результата последнего дня подачи жалобы в ВСРФ и даты подачи жалобы для определения остатка срока
    sum = a - b
    return sum
Dif1 = int(Dif(resolt, VSRF1))
print('Остаток дней на подачу жалобы на отказ:    ')
# для перехода на следующий год (баг со сроками)
if Dif1 > 70:
    Dif_2 = Dif1 - 365
if Dif1 < 70:
    Dif_2 = Dif1
if Dif1 < 0: # баг с минцсовыми сроками
    Dif_2 = 0
    Dif1 = 0


print(Dif_2)


input_date3 = int(input("Ведите число определения об отказе:   "))
input_month3 = int(input("Введите месяц определения об отказе:   "))



if input_month3 == 1:
    input_month3 = 31    
    l_month2 = 0
if input_month3 == 2:
    input_month3 = 28  
    l_month2 = 31
if input_month3 == 3:
    input_month3 = 31
    l_month2 = 59
if input_month3 == 4: 
    input_month3 = 30
    l_month2 = 90
if input_month3 == 5: 
    input_month3 = 31
    l_month2 = 120
if  input_month3 == 6: 
    input_month3 = 30
    l_month2 = 151
if input_month3 == 7: 
    input_month3 = 31
    l_month2 = 181
if input_month3 == 8: 
    input_month3 = 31
    l_month2 = 212
if input_month3 == 9: 
    input_month3 = 30
    l_month2 = 243
if input_month3 == 10: 
    input_month3 = 31
    l_month2 = 273
if input_month3 == 11: 
    input_month3 = 30
    l_month2 = 304
if input_month3 == 12: 
    input_month3 = 31
    l_month2 = 334
 # для отмены минусовых значений при подачи жалоб в последний день срока, в выходные дни
if Dif1 < 0:
    Dif1 = Dif1 * -1

# номер дня подачи жалобы на отказ  
def VSRF_ot(a,b): # сумма даты подачи жалобы на отказ и предидущих дней месяцев для опредения номера дня в году 1/365
    sum = a + b
    return sum
VSRF1_ot = int(VSRF_ot(input_date3, l_month2))

# последний день подачи жалобы на отказ
def Otkaz(a, b): # сумма номера дня подачи жалобы на отказ и остатка срока
    sum = a + b
    return sum
Otkaz_date = int(Otkaz(VSRF1_ot, Dif1))
print('Дата последнего дня на подачу жалобы на отказ')

resolt = Otkaz_date


# ЯНВАРЬ
if resolt == 1:
    print("01/01/2025 выходной день дата подачи до 09/01/2025")
if resolt == 2:
    print("02/01/2025 выходной день дата подачи до 09/01/2025")
if resolt == 3:
    print("03/01/2025 выходной день дата подачи до 09/01/2025")
if resolt == 4:
    print("04/01/2025 выходной день дата подачи до 09/01/2025")
if resolt == 5:
    print("05/01/2025 выходной день дата подачи до 09/01/2025")
if resolt == 6:
    print("06/01/2025 выходной день дата подачи до 09/01/2025")
if resolt == 7:
    print("07/01/2025 выходной день дата подачи до 09/01/2025")
if resolt == 8:
    print("08/01/2025 выходной день дата подачи до 09/01/2025")
if resolt == 9:
    print("09/01/2025")
if resolt == 10:
    print("10/01/2025")
if resolt == 11:
    print("11/01/2025 выходной день дата подачи до 13/01/2025")
if resolt == 12:
    print("12/01/2025 выходной день дата подачи до 13/01/2025")
if resolt == 13:
    print("13/01/2025")
if resolt == 14:
    print("14/01/2025")
if resolt == 15:
    print("15/01/2025")
if resolt == 16:
    print("16/01/2025")
if resolt == 17:
    print("17/01/2025")
if resolt == 18:
    print("18/01/2025 выходной день дата подачи до 20/01/2025")
if resolt == 19:
    print("19/01/2025 выходной день дата подачи до 20/01/2025")
if resolt == 20:
    print("20/01/2025")
if resolt == 21:
    print("21/01/2025")
if resolt == 22:
    print("22/01/2025")
if resolt == 23:
    print("23/01/2025")
if resolt == 24:
    print("24/01/2025")
if resolt == 25:
    print("25/01/2025 выходной день дата подачи до 27/01/2025")
if resolt == 26:
    print("26/01/2025 выходной день дата подачи до 27/01/2025")
if resolt == 27:
    print("27/01/2025")
if resolt == 28:
    print("28/01/2025")
if resolt == 29:
    print("29/01/2025")
if resolt == 30:
    print("30/01/2025")
if resolt == 31:
    print("31/01/2025")

# ФЕВРАЛЬ

if resolt == 32:
    print("01/02/2025 выходной день дата подачи до 03/02/2025")
if resolt == 33:
    print("01/02/2025 выходной день дата подачи до 03/02/2025")
if resolt == 34:
    print("03/02/2025")
if resolt == 35:
    print("04/02/2025")
if resolt == 36:
    print("05/02/2025")
if resolt == 37:
    print("06/02/2025")
if resolt == 38:
    print("07/02/2025")
if resolt == 39:
    print("08/02/2025 выходной день дата подачи до 10/02/2025")
if resolt == 40:
    print("09/02/2025 выходной день дата подачи до 10/02/2025")
if resolt == 41:
    print("10/02/2025")
if resolt == 42:
    print("11/02/2025")
if resolt == 43:
    print("12/02/2025")
if resolt == 44:
    print("13/02/2025")
if resolt == 45:
    print("14/02/2025")
if resolt == 46:
    print("15/02/2025 выходной день дата подачи до 17/02/2025")
if resolt == 47:
    print("16/02/2025 выходной день дата подачи до 17/02/2025")
if resolt == 48:
    print("17/02/2025")
if resolt == 49:
    print("18/02/2025")
if resolt == 50:
    print("19/02/2025")
if resolt == 51:
    print("20/02/2025")
if resolt == 52:
    print("21/02/2025")
if resolt == 53:
    print("22/02/2025 выходной день дата подачи до 24/02/2025")
if resolt == 54:
    print("23/02/2025 выходной день дата подачи до 24/02/2025")
if resolt == 55:
    print("24/02/2025")
if resolt == 56:
    print("25/02/2025")
if resolt == 57:
    print("26/02/2025")
if resolt == 58:
    print("27/02/2025")
if resolt == 59:
    print("28/02/2025")

# МАРТ

if resolt == 60:
    print("01/03/2025 выходной день дата подачи до 03/03/2025")
if resolt == 61:
    print("02/03/2025 выходной день дата подачи до 03/03/2025")
if resolt == 62:
    print("03/03/2025")
if resolt == 63:
    print("04/03/2025")
if resolt == 64:
    print("05/03/2025")
if resolt == 65:
    print("06/03/2025")
if resolt == 66:
    print("07/03/2025")
if resolt == 67:
    print("08/03/2025 выходной день дата подачи до 10/03/2025")
if resolt == 68:
    print("09/03/2025 выходной день дата подачи до 10/03/2025")
if resolt == 69:
    print("10/03/2025")
if resolt == 70:
    print("11/03/2025")
if resolt == 71:
    print("12/03/2025")
if resolt == 72:
    print("13/03/2025")
if resolt == 73:
    print("14/03/2025")
if resolt == 74:
    print("15/03/2025 выходной день дата подачи до 17/03/2025")
if resolt == 75:
    print("16/03/2025 выходной день дата подачи до 17/03/2025")
if resolt == 76:
    print("17/03/2025")
if resolt == 77:
    print("18/03/2025")
if resolt == 78:
    print("19/03/2025")
if resolt == 79:
    print("20/03/2025")
if resolt == 80:
    print("21/03/2025")
if resolt == 81:
    print("22/03/2025 выходной день дата подачи до 24/03/2025")
if resolt == 82:
    print("23/03/2025 выходной день дата подачи до 24/03/2025")
if resolt == 83:
    print("24/03/2025")
if resolt == 84:
    print("25/03/2025")
if resolt == 85:
    print("26/03/2025")
if resolt == 86:
    print("27/03/2025")
if resolt == 87:
    print("28/03/2025")
if resolt == 88:
    print("29/03/2025 выходной день дата подачи до 31/03/2025")
if resolt == 89:
    print("30/03/2025 выходной день дата подачи до 31/03/2025")
if resolt == 90:
    print("31/03/2025")

#АПРЕЛЬ

if resolt == 91:
    print("01/04/2025")
if resolt == 92:
    print("02/04/2025")
if resolt == 93:
    print("03/04/2025")
if resolt == 94:
    print("04/04/2025")
if resolt == 95:
    print("05/04/2025 выходной день дата подачи до 07/04/2025")
if resolt == 96:
    print("06/04/2025 выходной день дата подачи до 07/04/2025")
if resolt == 97:
    print("07/04/2025")
if resolt == 98:
    print("08/04/2025")
if resolt == 99:
    print("09/04/2025")
if resolt == 100:
    print("10/04/2025")
if resolt == 101:
    print("11/04/2025")
if resolt == 102:
    print("12/04/2025 выходной день дата подачи до 14/04/2025")
if resolt == 103:
    print("13/04/2025 выходной день дата подачи до 14/04/2025")
if resolt == 104:
    print("14/04/2025")
if resolt == 105:
    print("15/04/2025")
if resolt == 106:
    print("16/04/2025")
if resolt == 107:
    print("17/04/2025")
if resolt == 108:
    print("18/04/2025")
if resolt == 109:
    print("19/04/2025 выходной день дата подачи до 21/04/2025")
if resolt == 110:
    print("20/04/2025 выходной день дата подачи до 21/04/2025")
if resolt == 111:
    print("21/04/2025")
if resolt == 112:
    print("22/04/2025")
if resolt == 113:
    print("23/04/2025")
if resolt == 114:
    print("24/04/2025")
if resolt == 115:
    print("25/04/2025")
if resolt == 116:
    print("26/04/2025 выходной день дата подачи до 28/04/2025")
if resolt == 117:
    print("27/04/2025 выходной день дата подачи до 28/04/2025")
if resolt == 118:
    print("28/04/2025")
if resolt == 119:
    print("29/04/2025")
if resolt == 120:
    print("30/04/2025")

# МАЙ

if resolt == 121:
    print("01/05/2025 выходной день дата подачи до 05/05/2025")
if resolt == 122:
    print("02/05/2025 выходной день дата подачи до 05/05/2025")
if resolt == 123:
    print("03/05/2025 выходной день дата подачи до 05/05/2025")
if resolt == 124:
    print("04/05/2025 выходной день дата подачи до 05/05/2025")
if resolt == 125:
    print("05/05/2025")
if resolt == 126:
    print("06/05/2025")
if resolt == 127:
    print("07/05/2025")
if resolt == 128:
    print("08/05/2025 выходной день дата подачи до 12/05/2025")
if resolt == 129:
    print("09/05/2025 выходной день дата подачи до 12/05/2025")
if resolt == 130:
    print("10/05/2025 выходной день дата подачи до 12/05/2025")
if resolt == 131:
    print("11/05/2025 выходной день дата подачи до 12/05/2025")
if resolt == 132:
    print("12/05/2025")
if resolt == 133:
    print("13/05/2025")
if resolt == 134:
    print("14/05/2025")
if resolt == 135:
    print("15/05/2025")
if resolt == 136:
    print("16/05/2025")
if resolt == 137:
    print("17/05/2025 выходной день дата подачи до 19/05/2025")
if resolt == 138:
    print("18/05/2025 выходной день дата подачи до 19/05/2025")
if resolt == 139:
    print("19/05/2025")
if resolt == 140:
    print("20/05/2025")
if resolt == 141:
    print("21/05/2025")
if resolt == 142:
    print("22/05/2025")
if resolt == 143:
    print("23/05/2025")
if resolt == 144:
    print("24/05/2025 выходной день дата подачи до 26/05/2025")
if resolt == 145:
    print("25/05/2025 выходной день дата подачи до 26/05/2025")
if resolt == 146:
    print("26/05/2025")
if resolt == 147:
    print("27/05/2025")
if resolt == 148:
    print("28/05/2025")
if resolt == 149:
    print("29/05/2025")
if resolt == 150:
    print("30/05/2025")
if resolt == 151:
    print("31/05/2025 выходной день дата подачи до 02/06/2025")

#ИЮНЬ

if resolt == 152:
    print("01/06/2025 выходной день дата подачи до 02/06/2025")
if resolt == 153:
    print("02/06/2025")
if resolt == 154:
    print("03/06/2025")
if resolt == 155:
    print("04/06/2025")
if resolt == 156:
    print("05/06/2025")
if resolt == 157:
    print("06/06/2025")
if resolt == 158:
    print("07/06/2025 выходной день дата подачи до 09/06/2025")
if resolt == 159:
    print("08/06/2025 выходной день дата подачи до 09/06/2025")
if resolt == 160:
    print("09/06/2025")
if resolt == 161:
    print("10/06/2025")
if resolt == 162:
    print("11/06/2025")
if resolt == 163:
    print("12/06/2025 выходной день дата подачи до 16/06/2025")
if resolt == 164:
    print("13/06/2025 выходной день дата подачи до 16/06/2025")
if resolt == 165:
    print("14/06/2025 выходной день дата подачи до 16/06/2025")
if resolt == 166:
    print("15/06/2025 выходной день дата подачи до 16/06/2025")
if resolt == 167:
    print("16/06/2025")
if resolt == 168:
    print("17/06/2025")
if resolt == 169:
    print("18/06/2025")
if resolt == 170:
    print("19/06/2025")
if resolt == 171:
    print("20/06/2025")
if resolt == 172:
    print("21/06/2025 выходной день дата подачи до 23/06/2025")
if resolt == 173:
    print("22/06/2025 выходной день дата подачи до 23/06/2025")
if resolt == 174:
    print("23/06/2025")
if resolt == 175:
    print("24/06/2025")
if resolt == 176:
    print("25/06/2025")
if resolt == 177:
    print("26/06/2025")
if resolt == 178:
    print("27/06/2025")
if resolt == 179:
    print("28/06/2025 выходной день дата подачи до 30/06/2025")
if resolt == 180:
    print("29/06/2025 выходной день дата подачи до 30/06/2025")
if resolt == 181:
    print("30/06/2025")

#ИЮЛЬ

if resolt == 182:
    print("01/07/2025")
if resolt == 183:
    print("02/07/2025")
if resolt == 184:
    print("03/07/2025")
if resolt == 185:
    print("04/07/2025")
if resolt == 186:
    print("05/07/2025 выходной день дата подачи до 07/07/2025")
if resolt == 187:
    print("06/07/2025 выходной день дата подачи до 07/07/2025")
if resolt == 188:
    print("07/07/2025")
if resolt == 189:
    print("08/07/2025")
if resolt == 190:
    print("09/07/2025")
if resolt == 191:
    print("10/07/2025")
if resolt == 192:
    print("11/07/2025")
if resolt == 193:
    print("12/07/2025 выходной день дата подачи до 14/07/2025")
if resolt == 194:
    print("13/07/2025 выходной день дата подачи до 14/07/2025")
if resolt == 195:
    print("14/07/2025")
if resolt == 196:
    print("15/07/2025")
if resolt == 197:
    print("16/07/2025")
if resolt == 198:
    print("17/07/2025")
if resolt == 199:
    print("18/07/2025")
if resolt == 200:
    print("19/07/2025 выходной день дата подачи до 21/07/2025")
if resolt == 201:
    print("20/07/2025 выходной день дата подачи до 21/07/2025")
if resolt == 202:
    print("21/07/2025")
if resolt == 203:
    print("22/07/2025")
if resolt == 204:
    print("23/07/2025")
if resolt == 205:
    print("24/07/2025")
if resolt == 206:
    print("25/07/2025")
if resolt == 207:
    print("26/07/2025 выходной день дата подачи до 28/07/2025")
if resolt == 208:
    print("27/07/2025 выходной день дата подачи до 28/07/2025")
if resolt == 209:
    print("28/07/2025")
if resolt == 210:
    print("29/07/2025")
if resolt == 211:
    print("30/07/2025")
if resolt == 212:
    print("31/07/2025")

#АВГУСТ

if resolt == 213:
    print("01/08/2025")
if resolt == 214:
    print("02/08/2025 выходной день дата подачи до 04/08/2025")
if resolt == 215:
    print("03/08/2025 выходной день дата подачи до 04/08/2025")
if resolt == 216:
    print("04/08/2025")
if resolt == 217:
    print("05/08/2025")
if resolt == 218:
    print("06/08/2025")
if resolt == 219:
    print("07/08/2025")
if resolt == 220:
    print("08/08/2025")
if resolt == 221:
    print("09/08/2025 выходной день дата подачи до 11/08/2025")
if resolt == 222:
    print("10/08/2025 выходной день дата подачи до 11/08/2025")
if resolt == 223:
    print("11/08/2025")
if resolt == 224:
    print("12/08/2025")
if resolt == 225:
    print("13/08/2025")
if resolt == 226:
    print("14/08/2025")
if resolt == 227:
    print("15/08/2025")
if resolt == 228:
    print("16/08/2025 выходной день дата подачи до 18/08/2025")
if resolt == 229:
    print("17/08/2025 выходной день дата подачи до 18/08/2025")
if resolt == 230:
    print("18/08/2025")
if resolt == 231:
    print("19/08/2025")
if resolt == 232:
    print("20/08/2025")
if resolt == 233:
    print("21/08/2025")
if resolt == 234:
    print("22/08/2025")
if resolt == 235:
    print("23/08/2025 выходной день дата подачи до 25/08/2025")
if resolt == 236:
    print("24/08/2025 выходной день дата подачи до 25/08/2025")
if resolt == 237:
    print("25/08/2025")
if resolt == 238:
    print("26/08/2025")
if resolt == 239:
    print("27/08/2025")
if resolt == 240:
    print("28/08/2025")
if resolt == 241:
    print("29/08/2025")
if resolt == 242:
    print("30/08/2025 выходной день дата подачи до 01/09/2025")
if resolt == 243:
    print("31/08/2025 выходной день дата подачи до 01/09/2025")

#СЕНТЯБРЬ

if resolt == 244:
    print("01/09/2025")
if resolt == 245:
    print("02/09/2025")
if resolt == 246:
    print("03/09/2025")
if resolt == 247:
    print("04/09/2025")
if resolt == 248:
    print("05/09/2025")
if resolt == 249:
    print("06/09/2025 выходной день дата подачи до 08/09/2025")
if resolt == 250:
    print("07/09/2025 выходной день дата подачи до 08/09/2025")
if resolt == 251:
    print("08/09/2025")
if resolt == 252:
    print("09/09/2025")
if resolt == 253:
    print("10/09/2025")
if resolt == 254:
    print("11/09/2025")
if resolt == 255:
    print("12/09/2025")
if resolt == 256:
    print("13/09/2025 выходной день дата подачи до 01/09/2025")
if resolt == 257:
    print("14/09/2025 выходной день дата подачи до 01/09/2025")
if resolt == 258:
    print("15/09/2025")
if resolt == 259:
    print("16/09/2025")
if resolt == 260:
    print("17/09/2025")
if resolt == 261:
    print("18/09/2025")
if resolt == 262:
    print("19/09/2025")
if resolt == 263:
    print("20/09/2025 выходной день дата подачи до 22/09/2025")
if resolt == 264:
    print("21/09/2025 выходной день дата подачи до 22/09/2025")
if resolt == 265:
    print("22/09/2025")
if resolt == 266:
    print("23/09/2025")
if resolt == 267:
    print("24/09/2025")
if resolt == 268:
    print("25/09/2025")
if resolt == 269:
    print("26/09/2025")
if resolt == 270:
    print("27/09/2025 выходной день дата подачи до 29/09/2025")
if resolt == 271:
    print("28/09/2025 выходной день дата подачи до 29/09/2025")
if resolt == 272:
    print("29/09/2025")
if resolt == 273:
    print("30/09/2025")

#ОКТЯБРЬ

if resolt == 274:
    print("01/10/2025")
if resolt == 275:
    print("02/10/2025")
if resolt == 276:
    print("03/10/2025")
if resolt == 277:
    print("04/10/2025 выходной день дата подачи до 06/10/2025")
if resolt == 278:
    print("05/10/2025 выходной день дата подачи до 06/10/2025")
if resolt == 279:
    print("06/10/2025")
if resolt == 280:
    print("07/10/2025")
if resolt == 281:
    print("08/10/2025")
if resolt == 282:
    print("09/10/2025")
if resolt == 283:
    print("10/10/2025")
if resolt == 284:
    print("11/10/2025 выходной день дата подачи до 13/10/2025")
if resolt == 285:
    print("12/10/2025 выходной день дата подачи до 13/10/2025")
if resolt == 286:
    print("13/10/2025")
if resolt == 287:
    print("14/10/2025")
if resolt == 288:
    print("15/10/2025")
if resolt == 289:
    print("16/10/2025")
if resolt == 290:
    print("17/10/2025")
if resolt == 291:
    print("18/10/2025 выходной день дата подачи до 20/10/2025")
if resolt == 292:
    print("19/10/2025 выходной день дата подачи до 20/10/2025")
if resolt == 293:
    print("20/10/2025")
if resolt == 294:
    print("21/10/2025")
if resolt == 295:
    print("22/10/2025")
if resolt == 296:
    print("23/10/2025")
if resolt == 297:
    print("24/10/2025")
if resolt == 298:
    print("25/10/2025 выходной день дата подачи до 27/10/2025")
if resolt == 299:
    print("26/10/2025 выходной день дата подачи до 27/10/2025")
if resolt == 300:
    print("27/10/2025")
if resolt == 301:
    print("28/10/2025")
if resolt == 302:
    print("29/10/2025")
if resolt == 303:
    print("30/10/2025")
if resolt == 304:
    print("31/10/2025")

#НОЯБРЬ

if resolt == 305:
    print("01/11/2025 выходной день дата подачи до 05/11/2025")
if resolt == 306:
    print("02/11/2025 выходной день дата подачи до 05/11/2025")
if resolt == 307:
    print("03/11/2025 выходной день дата подачи до 05/11/2025")
if resolt == 308:
    print("04/11/2025 выходной день дата подачи до 05/11/2025")
if resolt == 309:
    print("05/11/2025")
if resolt == 310:
    print("06/11/2025")
if resolt == 311:
    print("07/11/2025")
if resolt == 312:
    print("08/11/2025 выходной день дата подачи до 10/11/2025")
if resolt == 313:
    print("09/11/2025 выходной день дата подачи до 10/11/2025")
if resolt == 314:
    print("10/11/2025")
if resolt == 315:
    print("11/11/2025")
if resolt == 316:
    print("12/1/2025")
if resolt == 317:
    print("13/11/2025")
if resolt == 318:
    print("14/11/2025")
if resolt == 319:
    print("15/11/2025 выходной день дата подачи до 17/11/2025")
if resolt == 320:
    print("16/11/2025 выходной день дата подачи до 17/11/2025")
if resolt == 321:
    print("17/11/2025")
if resolt == 322:
    print("18/11/2025")
if resolt == 323:
    print("19/11/2025")
if resolt == 324:
    print("20/11/2025")
if resolt == 325:
    print("21/11/2025")
if resolt == 326:
    print("22/11/2025 выходной день дата подачи до 24/11/2025")
if resolt == 327:
    print("23/11/2025 выходной день дата подачи до 24/11/2025")
if resolt == 328:
    print("24/11/2025")
if resolt == 329:
    print("25/11/2025")
if resolt == 330:
    print("26/11/2025")
if resolt == 331:
    print("27/11/2025")
if resolt == 332:
    print("28/11/2025")
if resolt == 333:
    print("29/11/2025 выходной день дата подачи до 01/12/2025")
if resolt == 334:
    print("30/11/2025 выходной день дата подачи до 01/12/2025")

#ДЕКАБРЬ

if resolt == 335:
    print("01/12/2025")
if resolt == 336:
    print("02/12/2025")
if resolt == 337:
    print("03/12/2025")
if resolt == 338:
    print("04/12/2025")
if resolt == 339:
    print("05/12/2025")
if resolt == 340:
    print("06/12/2025 выходной день дата подачи до 08/12/2025")
if resolt == 341:
    print("07/12/2025 выходной день дата подачи до 08/12/2025")
if resolt == 342:
    print("08/12/2025")
if resolt == 343:
    print("09/12/2025")
if resolt == 344:
    print("10/12/2025")
if resolt == 345:
    print("11/12/2025")
if resolt == 346:
    print("12/12/2025")
if resolt == 347:
    print("13/12/2025 выходной день дата подачи до 15/12/2025")
if resolt == 348:
    print("14/12/2025 выходной день дата подачи до 15/12/2025")
if resolt == 349:
    print("15/12/2025")
if resolt == 350:
    print("16/12/2025")
if resolt == 351:
    print("17/12/2025")
if resolt == 352:
    print("18/12/2025")
if resolt == 353:
    print("19/12/2025")
if resolt == 354:
    print("20/12/2025 выходной день дата подачи до 22/12/2025")
if resolt == 355:
    print("21/12/2025 выходной день дата подачи до 22/12/2025")
if resolt == 356:
    print("22/12/2025")
if resolt == 357:
    print("23/12/2025")
if resolt == 358:
    print("24/12/2025")
if resolt == 359:
    print("25/12/2025")
if resolt == 360:
    print("26/12/2025")
if resolt == 361:
    print("27/12/2025 выходной день дата подачи до 29/12/2025")
if resolt == 362:
    print("28/12/2025 выходной день дата подачи до 29/12/2025")
if resolt == 363:
    print("29/12/2025")
if resolt == 364:
    print("30/12/2025")
if resolt == 365:
    print("31/12/2025 выходной день дата подачи до 12/01/2026")


    #2026 ГОД

    # ЯНВАРЬ
if resolt == 366:
    print("01/01/2026 выходной день дата подачи до 12/01/2026")
if resolt == 367:
    print("02/01/2026 выходной день дата подачи до 12/01/2026")
if resolt == 368:
    print("03/01/2026 выходной день дата подачи до 12/01/2026")
if resolt == 369:
    print("04/01/2026 выходной день дата подачи до 12/01/2026")
if resolt == 370:
    print("05/01/2026 выходной день дата подачи до 12/01/2026")
if resolt == 371:
    print("06/01/2026 выходной день дата подачи до 12/01/2026")
if resolt == 372:
    print("07/01/2026 выходной день дата подачи до 12/01/2026")
if resolt == 373:
    print("08/01/2026 выходной день дата подачи до 12/01/2026")
if resolt == 374:
    print("09/01/2026 выходной день дата подачи до 12/01/2026")
if resolt == 375:
    print("10/01/2026 выходной день дата подачи до 12/01/2026")
if resolt == 376:
    print("11/01/2026 выходной день дата подачи до 12/01/2026")
if resolt == 377:
    print("12/01/2026")
if resolt == 378:
    print("13/01/2026")
if resolt == 379:
    print("14/01/2026")
if resolt == 380:
    print("15/01/2026")
if resolt == 381:
    print("16/01/2026")
if resolt == 382:
    print("17/01/2026 выходной день дата подачи до 19/01/2026")
if resolt == 383:
    print("18/01/2026 выходной день дата подачи до 19/01/2026")
if resolt == 384:
    print("19/01/2026")
if resolt == 385:
    print("20/01/2026")
if resolt == 386:
    print("21/01/2026")
if resolt == 387:
    print("22/01/2026")
if resolt == 388:
    print("23/01/2026")
if resolt == 389:
    print("24/01/2026 выходной день дата подачи до 26/01/2026")
if resolt == 390:
    print("25/01/2026 выходной день дата подачи до 26/01/2026")
if resolt == 391:
    print("26/01/2026")
if resolt == 392:
    print("27/01/2026")
if resolt == 393:
    print("28/01/2026")
if resolt == 394:
    print("29/01/2026")
if resolt == 395:
    print("30/01/2026")
if resolt == 396:
    print("31/01/2026 выходной день дата подачи до 02/02/2026")

# ФЕВРАЛЬ

if resolt == 397:
    print("01/02/2026 выходной день дата подачи до 02/02/2026")
if resolt == 398:
    print("01/02/2026")
if resolt == 399:
    print("03/02/2026")
if resolt == 400:
    print("04/02/2026")
if resolt == 401:
    print("05/02/2026")
if resolt == 402:
    print("06/02/2026")
if resolt == 403:
    print("07/02/2026 выходной день дата подачи до 09/02/2026")
if resolt == 404:
    print("08/02/2026 выходной день дата подачи до 09/02/2026")
if resolt == 405:
    print("09/02/2026")
if resolt == 406:
    print("10/02/2026")
if resolt == 407:
    print("11/02/2026")
if resolt == 408:
    print("12/02/2026")
if resolt == 409:
    print("13/02/2026")
if resolt == 410:
    print("14/02/2026 выходной день дата подачи до 16/02/2026")
if resolt == 411:
    print("15/02/2026 выходной день дата подачи до 16/02/2026")
if resolt == 412:
    print("16/02/2026")
if resolt == 413:
    print("17/02/2026")
if resolt == 414:
    print("18/02/2026")
if resolt == 415:
    print("19/02/2026")
if resolt == 416:
    print("20/02/2026")
if resolt == 417:
    print("21/02/2026 выходной день дата подачи до 24/02/2026")
if resolt == 418:
    print("22/02/2026 выходной день дата подачи до 24/02/2026")
if resolt == 419:
    print("23/02/2026 выходной день дата подачи до 24/02/2026")
if resolt == 420:
    print("24/02/2026")
if resolt == 421:
    print("25/02/2026")
if resolt == 422:
    print("26/02/2026")
if resolt == 423:
    print("27/02/2026")
if resolt == 424:
    print("28/02/2026 выходной день дата подачи до 02/03/2026")

# МАРТ

if resolt == 425:
    print("01/03/2026 выходной день дата подачи до 02/03/2026")
if resolt == 426:
    print("02/03/2026")
if resolt == 427:
    print("03/03/2026")
if resolt == 428:
    print("04/03/2026")
if resolt == 429:
    print("05/03/2026")
if resolt == 430:
    print("06/03/2026")
if resolt == 431:
    print("07/03/2026 выходной день дата подачи до 10/03/2026")
if resolt == 432:
    print("08/03/2026 выходной день дата подачи до 10/03/2026")
if resolt == 433:
    print("09/03/2026 выходной день дата подачи до 10/03/2026")
if resolt == 434:
    print("10/03/2026")
if resolt == 435:
    print("11/03/2026")
if resolt == 436:
    print("12/03/2026")
if resolt == 437:
    print("13/03/2026")
if resolt == 438:
    print("14/03/2026 выходной день дата подачи до 16/03/2026")
if resolt == 439:
    print("15/03/2026 выходной день дата подачи до 16/03/2026")
if resolt == 440:
    print("16/03/2026")
if resolt == 441:
    print("17/03/2026")
if resolt == 442:
    print("18/03/2026")
if resolt == 443:
    print("19/03/2026")
if resolt == 444:
    print("20/03/2026")
if resolt == 445:
    print("21/03/2026 выходной день дата подачи до 23/03/2026")
if resolt == 446:
    print("22/03/2026 выходной день дата подачи до 23/03/2026")
if resolt == 447:
    print("23/03/2026")
if resolt == 448:
    print("24/03/2026")
if resolt == 449:
    print("25/03/2026")
if resolt == 450:
    print("26/03/2026")
if resolt == 451:
    print("27/03/2026")
if resolt == 452:
    print("28/03/2026 выходной день дата подачи до 30/03/2026")
if resolt == 453:
    print("29/03/2026 выходной день дата подачи до 30/03/2026")
if resolt == 454:
    print("30/03/2026")
if resolt == 455:
    print("31/03/2026")

#АПРЕЛЬ

if resolt == 456:
    print("01/04/2026")
if resolt == 457:
    print("02/04/2026")
if resolt == 458:
    print("03/04/2026")
if resolt == 459:
    print("04/04/2026 выходной день дата подачи до 06/04/2026")
if resolt == 460:
    print("05/04/2026 выходной день дата подачи до 06/04/2026")
if resolt == 461:
    print("06/04/2026")
if resolt == 462:
    print("07/04/2026")
if resolt == 463:
    print("08/04/2026")
if resolt == 464:
    print("09/04/2026")
if resolt == 465:
    print("10/04/2026")
if resolt == 466:
    print("11/04/2026 выходной день дата подачи до 13/04/2026")
if resolt == 467:
    print("12/04/2026 выходной день дата подачи до 13/04/2026")
if resolt == 468:
    print("13/04/2026")
if resolt == 469:
    print("14/04/2026")
if resolt == 470:
    print("15/04/2026")
if resolt == 471:
    print("16/04/2026")
if resolt == 472:
    print("17/04/2026")
if resolt == 473:
    print("18/04/2026 выходной день дата подачи до 20/04/2026")
if resolt == 474:
    print("19/04/2026 выходной день дата подачи до 20/04/2026")
if resolt == 475:
    print("20/04/2026")
if resolt == 476:
    print("21/04/2026")
if resolt == 477:
    print("22/04/2026")
if resolt == 478:
    print("23/04/2026")
if resolt == 479:
    print("24/04/2026")
if resolt == 480:
    print("25/04/2026 выходной день дата подачи до 27/04/2026")
if resolt == 481:
    print("26/04/2026 выходной день дата подачи до 27/04/2026")
if resolt == 482:
    print("27/04/2026")
if resolt == 483:
    print("28/04/2026")
if resolt == 484:
    print("29/04/2026")
if resolt == 485:
    print("30/04/2026")

# МАЙ

if resolt == 486:
    print("01/05/2026 выходной день дата подачи до 04/05/2026")
if resolt == 487:
    print("02/05/2026 выходной день дата подачи до 04/05/2026")
if resolt == 488:
    print("03/05/2026 выходной день дата подачи до 04/05/2026")
if resolt == 489:
    print("04/05/2026")
if resolt == 490:
    print("05/05/2026")
if resolt == 491:
    print("06/05/2026")
if resolt == 492:
    print("07/05/2026")
if resolt == 493:
    print("08/05/2026")
if resolt == 494:
    print("09/05/2026 выходной день дата подачи до 11/05/2026")
if resolt == 495:
    print("10/05/2026 выходной день дата подачи до 11/05/2026")
if resolt == 496:
    print("11/05/2026")
if resolt == 497:
    print("12/05/2026")
if resolt == 498:
    print("13/05/2026")
if resolt == 499:
    print("14/05/2026")
if resolt == 500:
    print("15/05/2026")
if resolt == 501:
    print("16/05/2026 выходной день дата подачи до 18/05/2026")
if resolt == 502:
    print("17/05/2026 выходной день дата подачи до 18/05/2026")
if resolt == 503:
    print("18/05/2026")
if resolt == 504:
    print("19/05/2026")
if resolt == 505:
    print("20/05/2026")
if resolt == 506:
    print("21/05/2026")
if resolt == 507:
    print("22/05/2026")
if resolt == 508:
    print("23/05/2026 выходной день дата подачи до 25/05/2026")
if resolt == 509:
    print("24/05/2026 выходной день дата подачи до 25/05/2026")
if resolt == 510:
    print("25/05/2026")
if resolt == 511:
    print("26/05/2026")
if resolt == 512:
    print("27/05/2026")
if resolt == 513:
    print("28/05/2026")
if resolt == 514:
    print("29/05/2026")
if resolt == 515:
    print("30/05/2026 выходной день дата подачи до 01/06/2026")
if resolt == 516:
    print("31/05/2026 выходной день дата подачи до 01/06/2026")

#ИЮНЬ

if resolt == 517:
    print("01/06/2026")
if resolt == 518:
    print("02/06/2026")
if resolt == 519:
    print("03/06/2026")
if resolt == 520:
    print("04/06/2026")
if resolt == 521:
    print("05/06/2026")
if resolt == 522:
    print("06/06/2026 выходной день дата подачи до 08/06/2026")
if resolt == 523:
    print("07/06/2026 выходной день дата подачи до 08/06/2026")
if resolt == 524:
    print("08/06/2026")
if resolt == 525:
    print("09/06/2026")
if resolt == 526:
    print("10/06/2026")
if resolt == 527:
    print("11/06/2026")
if resolt == 528:
    print("12/06/2026 выходной день дата подачи до 15/06/2026")
if resolt == 529:
    print("13/06/2026 выходной день дата подачи до 15/06/2026")
if resolt == 530:
    print("14/06/2026 выходной день дата подачи до 15/06/2026")
if resolt == 531:
    print("15/06/2026")
if resolt == 532:
    print("16/06/2026")
if resolt == 533:
    print("17/06/2026")
if resolt == 534:
    print("18/06/2026")
if resolt == 535:
    print("19/06/2026")
if resolt == 536:
    print("20/06/2026 выходной день дата подачи до 22/06/2026")
if resolt == 537:
    print("21/06/2026 выходной день дата подачи до 22/06/2026")
if resolt == 538:
    print("22/06/2026")
if resolt == 539:
    print("23/06/2026")
if resolt == 540:
    print("24/06/2026")
if resolt == 541:
    print("25/06/2026")
if resolt == 542:
    print("26/06/2026")
if resolt == 543:
    print("27/06/2026 выходной день дата подачи до 29/06/2026")
if resolt == 544:
    print("28/06/2026 выходной день дата подачи до 29/06/2026")
if resolt == 545:
    print("29/06/2026")
if resolt == 546:
    print("30/06/2026")

#ИЮЛЬ

if resolt == 547:
    print("01/07/2026")
if resolt == 548:
    print("02/07/2026")
if resolt == 549:
    print("03/07/2026")
if resolt == 550:
    print("04/07/2026 выходной день дата подачи до 06/07/2026")
if resolt == 551:
    print("05/07/2026 выходной день дата подачи до 06/07/2026")
if resolt == 552:
    print("06/07/2026")
if resolt == 553:
    print("07/07/2026")
if resolt == 554:
    print("08/07/2026")
if resolt == 555:
    print("09/07/2026")
if resolt == 556:
    print("10/07/2026")
if resolt == 557:
    print("11/07/2026 выходной день дата подачи до 13/07/2026")
if resolt == 558:
    print("12/07/2026 выходной день дата подачи до 13/07/2026")
if resolt == 559:
    print("13/07/2026")
if resolt == 560:
    print("14/07/2026")
if resolt == 561:
    print("15/07/2026")
if resolt == 562:
    print("16/07/2026")
if resolt == 563:
    print("17/07/2026")
if resolt == 564:
    print("18/07/2026 выходной день дата подачи до 20/07/2026")
if resolt == 565:
    print("19/07/2026 выходной день дата подачи до 20/07/2026")
if resolt == 566:
    print("20/07/2026")
if resolt == 567:
    print("21/07/2026")
if resolt == 568:
    print("22/07/2026")
if resolt == 569:
    print("23/07/2026")
if resolt == 570:
    print("24/07/2026")
if resolt == 571:
    print("25/07/2026 выходной день дата подачи до 27/07/2026")
if resolt == 572:
    print("26/07/2026 выходной день дата подачи до 27/07/2026")
if resolt == 573:
    print("27/07/2026")
if resolt == 574:
    print("28/07/2026")
if resolt == 575:
    print("29/07/2026")
if resolt == 576:
    print("30/07/2026")
if resolt == 577:
    print("31/07/2026")

print("Нажмите Enter для закрытия программы")
a = input()
