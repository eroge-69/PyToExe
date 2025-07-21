# region Thư viện
import keyboard
import tkinter as tk
from tkinter import ttk
import time
import webbrowser
from PIL import Image, ImageTk

print('╭──────────────────────────────────────────────────────────────╮')
print('│                                                              │')

# region Biến số
typed_word = ''

sini = ''
pini = ''

t1_var = None
t2_var = None
popup_window = None

WORD_DELIMITERS = ['space', 'enter', ':', ''', ''', ';', ',', '.', '?', '/', '[', ']', '{', '}', '<', '>', '`', '~', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '=', '_', '+']

num = 0

# Biến mới để kiểm soát trạng thái hoạt động của bộ gõ
is_active = True
# Biến để lưu tổ hợp phím tắt đã chọn
selected_hotkey = None
# Dictionary lưu trữ các hotkey và mô tả của chúng
HOTKEYS = {
    'Ctrl + Shift + Q': 'ctrl+shift+q',
    'Ctrl + Alt + Q': 'ctrl+alt+q',
    'Ctrl + Q':'ctrl+q',
    'Ctrl + Shift': 'ctrl+shift',
    'Alt + Z': 'alt+z',
}

# region Các Rules
PAD_RULES = {
    'q': 'q', 'w': 'ng', 'e': 'kh', 'r': 'r', 't': 't', 'y': 'nh', 'u': 'th', 'i': 'tr', 'o': 'p', 'p': '',
    'a': '', 's': 's', 'd': 'đ', 'f': 'ph', 'g': 'g', 'h': 'h', 'j': 'gi', 'k': 'c', 'l': 'l',
    'z': 'd', 'x': 'x', 'c': 'ch', 'v': 'v', 'b': 'b', 'n': 'n', 'm': 'm'
}

NA_RULES = {
    'q': ('oa', 0), 'w': ('oă', 2), 'e': ('oe', 0), 'r': ('uê', 0), 't': ('ua', 0),
    'y': ('uâ', 2), 'u': ('uơ', 0), 'i': ('ya', 0),
    'o': ('@', 1), 'p': ('', 0),
    'a': ('a', 0), 's': ('â', 2), 'd': ('e', 0), 'f': ('o', 0), 'g': ('u', 0),
    'h': ('y', 0), 'j': ('i', 0), 'k': ('uyi', 0), 'l': ('uya', 0), 'z': ('ă', 2),
    'x': ('ơ', 0), 'c': ('ê', 0), 'v': ('ô', 0), 'b': ('ư', 0), 'n': ('ia', 0),
    'm': ('ưa', 0)
}

PAC_RULES = {
    'q': 'j', 'w': 'w', 'e': 'm', 'r': 'n', 't': 'q', 'y': 'y', 'u': 'p',
    'i': 't', 'o': 'c', 'p': 'k', 'h': 'P', 'j': 'T', 'k': 'C', 'l': 'K'
}

VAN_RULES = {
    'a': ('a', 1), 'aj': ('ai', 1), 'aw': ('ao', 1), 'am': ('am', 1), 'an': ('an', 1), 'aq': ('ang', 1), 'ay': ('anh', 1),
    'ă': ('a', 1), 'ăj': ('ay', 1), 'ăw': ('au', 1), 'ăm': ('ăm', 1), 'ăn': ('ăn', 1), 'ăq': ('ăng', 1), 'ăy': ('anh', 1),
    'e': ('e', 1), 'ej': ('e', 1), 'ew': ('eo', 1), 'em': ('em', 1), 'en': ('en', 1), 'eq': ('eng', 1), 'ey': ('eng', 1),
    'ê': ('ê', 1), 'êj': ('ê', 1), 'êw': ('êu', 1), 'êm': ('êm', 1), 'ên': ('ên', 1), 'êq': ('êng', 1), 'êy': ('ênh', 1),
    'i': ('i', 1), 'ij': ('i', 1), 'iw': ('iu', 1), 'im': ('im', 1), 'in': ('in', 1), 'iq': ('inh', 1), 'iy': ('inh', 1),
    'o': ('o', 1), 'oj': ('oi', 1), 'ow': ('o', 1), 'om': ('om', 1), 'on': ('on', 1), 'oq': ('ong', 1), 'oy': ('oong', 2),
    'ô': ('ô', 1), 'ôj': ('ôi', 1), 'ôw': ('ô', 1), 'ôm': ('ôm', 1), 'ôn': ('ôn', 1), 'ôq': ('ông', 1), 'ôy': ('ôông', 2),
    'u': ('u', 1), 'uj': ('ui', 1), 'uw': ('u', 1), 'um': ('um', 1), 'un': ('un', 1), 'uq': ('ung', 1), 'uy': ('ung', 1),
    'ư': ('ư', 1), 'ưj': ('ưi', 1), 'ưw': ('ưu', 1), 'ưm': ('ưm', 1), 'ưn': ('ưn', 1), 'ưq': ('ưng', 1), 'ưy': ('ưng', 1),
    'ơ': ('ơ', 1), 'ơj': ('ơi', 1), 'ơw': ('ơu', 1), 'ơm': ('ơm', 1), 'ơn': ('ơn', 1), 'ơq': ('ơng', 1), 'ơy': ('ơng', 1),
    'â': ('ơ', 1), 'âj': ('ây', 1), 'âw': ('âu', 1), 'âm': ('âm', 1), 'ân': ('ân', 1), 'âq': ('âng', 1), 'ây': ('âng', 1),
    'y': ('y', 1), 'yj': ('y', 1), 'yw': ('yu', 1), 'ym': ('ym', 1), 'yn': ('yn', 1), 'yq': ('ynh', 1), 'yy': ('ynh', 1),
    'ia': ('ia', 1), 'iaj': ('iây', 2), 'iaw': ('iêu', 2), 'iam': ('iêm', 2), 'ian': ('iên', 2), 'iaq': ('iêng', 2), 'iay': ('iêng', 2),
    'ưa': ('ưa', 1), 'ưaj': ('ươi', 2), 'ưaw': ('ươu', 2), 'ưam': ('ươm', 2), 'ưan': ('ươn', 2), 'ưaq': ('ương', 2), 'ưay': ('ương', 2),

    'ya': ('ya', 1), 'yaj': ('yây', 2), 'yaw': ('yêu', 2), 'yam': ('yêm', 2), 'yan': ('yên', 2), 'yaq': ('yêng', 2), 'yay': ('yêng', 2),

    'oa': ('oa', 1), 'oaj': ('oai', 2), 'oaw': ('oao', 2), 'oam': ('oam', 2), 'oan': ('oan', 2), 'oaq': ('oang', 2), 'oay': ('oanh', 2),
    'oă': ('oa', 1), 'oăj': ('oay', 2), 'oăw': ('oau', 2), 'oăm': ('oăm', 1), 'oăn': ('oăn', 1), 'oăq': ('oăng', 1), 'oăy': ('oanh', 2),
    'oe': ('oe', 1), 'oej': ('oe', 1), 'oew': ('oeo', 2), 'oem': ('oem', 2), 'oen': ('oen', 2), 'oeq': ('oeng', 2), 'oey': ('oeng', 2),
    'uê': ('uê', 1), 'uêj': ('uê', 1), 'uêw': ('uêu', 2), 'uêm': ('uêm', 2), 'uên': ('uên', 2), 'uêq': ('uêng', 2), 'uêy': ('uênh', 2),
    'uyi': ('uy', 1), 'uyij': ('uy', 2), 'uyiw': ('uyu', 2), 'uyim': ('uym', 2), 'uyin': ('uyn', 2), 'uyiq': ('uynh', 2), 'uyiy': ('uynh', 2),
    'uya': ('uya', 2), 'uyaj': ('uyê', 2), 'uyaw': ('uyêu', 3), 'uyam': ('uyêm', 3), 'uyan': ('uyên', 3), 'uyaq': ('uyêng', 3), 'uyay': ('uyênh', 3),
    'ua': ('ua', 1), 'uaj': ('uôi', 2), 'uaw': ('uôu', 2), 'uam': ('uôm', 2), 'uan': ('uôn', 2), 'uaq': ('uông', 2), 'uay': ('uông', 2),
    'uâ': ('uâ', 2), 'uâj': ('uây', 2), 'uâw': ('uâu', 2), 'uâm': ('uâm', 2), 'uân': ('uân', 2), 'uâq': ('uâng', 2), 'uây': ('uâng', 2),
    'uơ': ('uơ', 2), 'uơj': ('uơi', 2), 'uơw': ('uơu', 2), 'uơm': ('uơm', 2), 'uơn': ('uơn', 2), 'uơq': ('uơng', 2), 'uơy': ('uơng', 2),

    '@': ('ắk', 0), '@j': ('ắk', 0), '@w': ('ắk', 0), '@m': ('ắk', 0), '@n': ('ắk', 0), '@q': ('ắk', 0), '@y': ('ắk', 0),

    'qa': ('ua', 2), 'qaj': ('uai', 2), 'qaw': ('uao', 2), 'qam': ('uam', 2), 'qan': ('uan', 2), 'qaq': ('uang', 2), 'qay': ('uanh', 2),
    'qă': ('ua', 2), 'qăj': ('uay', 2), 'qăw': ('uau', 2), 'qăm': ('uăm', 2), 'qăn': ('uăn', 2), 'qăq': ('uăng', 2), 'qăy': ('uanh', 2),
    'qe': ('ue', 2), 'qej': ('ue', 2), 'qew': ('ueo', 2), 'qem': ('uem', 2), 'qen': ('uen', 2), 'qeq': ('ueng', 2), 'qey': ('ueng', 2),

    'ap': ('áp', 0), 'at': ('át', 0), 'ac': ('ác', 0), 'ak': ('ách', 0), 'aP': ('ạp', 0), 'aT': ('ạt', 0), 'aC': ('ạc', 0), 'aK': ('ạch', 0),
    'ăp': ('ắp', 0), 'ăt': ('ắt', 0), 'ăc': ('ắc', 0), 'ăk': ('ách', 0), 'ăP': ('ặp', 0), 'ăT': ('ặt', 0), 'ăC': ('ặc', 0), 'ăK': ('ạch', 0),
    'ep': ('ép', 0), 'et': ('ét', 0), 'ec': ('éc', 0), 'ek': ('éc', 0), 'eP': ('ẹp', 0), 'eT': ('ẹt', 0), 'eC': ('ẹc', 0), 'eK': ('ẹc', 0),
    'êp': ('ếp', 0), 'êt': ('ết', 0), 'êc': ('ếc', 0), 'êk': ('ếch', 0), 'êP': ('ệp', 0), 'êT': ('ệt', 0), 'êC': ('ệc', 0), 'êK': ('ệch', 0),
    'ip': ('íp', 0), 'it': ('ít', 0), 'ic': ('ích', 0), 'ik': ('ích', 0), 'iP': ('ịp', 0), 'iT': ('ịt', 0), 'iC': ('ịch', 0), 'iK': ('ịch', 0),
    'op': ('óp', 0), 'ot': ('ót', 0), 'oc': ('óc', 0), 'ok': ('oóc', 0), 'oP': ('ọp', 0), 'oT': ('ọt', 0), 'oC': ('ọc', 0), 'oK': ('oọc', 0),
    'ôp': ('ốp', 0), 'ôt': ('ốt', 0), 'ôc': ('ốc', 0), 'ôk': ('ốc', 0), 'ôP': ('ộp', 0), 'ôT': ('ột', 0), 'ôC': ('ộc', 0), 'ôK': ('ôộc', 0),
    'up': ('úp', 0), 'ut': ('út', 0), 'uc': ('úc', 0), 'uk': ('úc', 0), 'uP': ('ụp', 0), 'uT': ('ụt', 0), 'uC': ('ục', 0), 'uK': ('ục', 0),
    'ưp': ('ứp', 0), 'ưt': ('ứt', 0), 'ưc': ('ức', 0), 'ưk': ('ức', 0), 'ưP': ('ựp', 0), 'ưT': ('ựt', 0), 'ưC': ('ực', 0), 'ưK': ('ực', 0),
    'ơp': ('ớp', 0), 'ơt': ('ớt', 0), 'ơc': ('ớc', 0), 'ơk': ('ớc', 0), 'ơP': ('ớp', 0), 'ơT': ('ớt', 0), 'ơC': ('ớc', 0), 'ơK': ('ớc', 0),
    'âp': ('ấp', 0), 'ât': ('ất', 0), 'âc': ('ấc', 0), 'âk': ('ấc', 0), 'âP': ('ập', 0), 'âT': ('ật', 0), 'âC': ('ậc', 0), 'âK': ('ậc', 0),
    'yp': ('ýp', 0), 'yt': ('ýt', 0), 'yc': ('ých', 0), 'yk': ('ých', 0), 'yP': ('ỵp', 0), 'yT': ('ỵt', 0), 'yC': ('ỵc', 0), 'yK': ('ỵc', 0),
    'iap': ('iếp', 0), 'iat': ('iết', 0), 'iac': ('iếc', 0), 'iak': ('iếch', 0), 'iaP': ('iệp', 0), 'iaT': ('iệt', 0), 'iaC': ('iệc', 0), 'iaK': ('iệch', 0),
    'ưap': ('ướp', 0), 'ưat': ('ướt', 0), 'ưac': ('ước', 0), 'ưak': ('ước', 0), 'ưaP': ('ượp', 0), 'ưaT': ('ượt', 0), 'ưaC': ('ược', 0), 'ưaK': ('ược', 0),

    'oap': ('oáp', 0), 'oat': ('oát', 0), 'oac': ('oác', 0), 'oak': ('oách', 0), 'oaP': ('oạp', 0), 'oaT': ('oạt', 0), 'oaC': ('oạc', 0), 'oaK': ('oạch', 0),
    'oăp': ('oắp', 0), 'oăt': ('oắt', 0), 'oăc': ('oắc', 0), 'oăk': ('oách', 0), 'oăP': ('oặp', 0), 'oăT': ('oặt', 0), 'oăC': ('oặc', 0), 'oăK': ('oạch', 0),
    'oep': ('oép', 0), 'oet': ('oét', 0), 'oec': ('oéc', 0), 'oek': ('oéc', 0), 'oeP': ('oẹp', 0), 'oeT': ('oẹt', 0), 'oeC': ('oẹc', 0), 'oeK': ('oẹc', 0),
    'uêp': ('uếp', 0), 'uêt': ('uết', 0), 'uêc': ('uếc', 0), 'uêk': ('uếch', 0), 'uêP': ('uệp', 0), 'uêT': ('uệt', 0), 'uêC': ('uệc', 0), 'uêK': ('uệch', 0),
    'uyip': ('uýp', 0), 'uyit': ('uýt', 0), 'uyic': ('uých', 0), 'uyik': ('uých', 0), 'uyiP': ('uỵp', 0), 'uyiT': ('uỵt', 0), 'uyiC': ('uỵch', 0), 'uyiK': ('uỵch', 0),
    'uyap': ('uyếp', 0), 'uyat': ('uyết', 0), 'uyac': ('uyếc', 0), 'uyak': ('uyếch', 0), 'uyaP': ('uyệp', 0), 'uyaT': ('uyệt', 0), 'uyac': ('uyếc', 0), 'uyak': ('uyếch', 0),
    'uyac': ('uyếc', 0), 'uyak': ('uyếch', 0), 'uyaP': ('uyệp', 0), 'uyaT': ('uyệt', 0), 'uyaC': ('uyệc', 0), 'uyaK': ('uyệch', 0),
    'uap': ('uốp', 0), 'uat': ('uốt', 0), 'uac': ('uốc', 0), 'uak': ('uốc', 0), 'uaP': ('uộp', 0), 'uaT': ('uột', 0), 'uaC': ('uộc', 0), 'uaK': ('uộc', 0),
    'uâp': ('uấp', 0), 'uât': ('uất', 0), 'uâc': ('uấc', 0), 'uâk': ('uấc', 0), 'uâP': ('uập', 0), 'uâT': ('uật', 0), 'uâC': ('uậc', 0), 'uâK': ('uậc', 0),
    'uơp': ('uớp', 0), 'uơt': ('uớt', 0), 'uơc': ('uớc', 0), 'uơk': ('uớc', 0), 'uơP': ('uợp', 0), 'uơT': ('uợt', 0), 'uơC': ('uợc', 0), 'uơK': ('uợc', 0),

    '@p': ('ắk', 0), '@t': ('ắk', 0), '@c': ('ắk', 0), '@k': ('ắk', 0), '@P': ('ặk', 0), '@T': ('ặk', 0), '@C': ('ặk', 0), '@K': ('ặk', 0),

    'qap': ('uáp', 0), 'qat': ('uát', 0), 'qac': ('uác', 0), 'qak': ('uách', 0), 'qaP': ('uạp', 0), 'qaT': ('uạt', 0), 'qaC': ('uạc', 0), 'qaK': ('uạch', 0),
    'qăp': ('uắp', 0), 'qăt': ('uắt', 0), 'qăc': ('uắc', 0), 'qăk': ('uách', 0), 'qăP': ('uặp', 0), 'qăT': ('uặt', 0), 'qăC': ('uặc', 0), 'qăK': ('uạch', 0),
    'qep': ('uép', 0), 'qet': ('uét', 0), 'qec': ('uéc', 0), 'qek': ('uéc', 0), 'qep': ('uẹp', 0), 'qet': ('uẹt', 0), 'qec': ('uẹc', 0), 'qek': ('uẹc', 0)
}

DT_INPUT_CHARS = {
    'a': 2, 's': 1, 'd': 3, 'f': 4, 'g': 5
}

NA_val_XLV_global = ''

# region Thêm Thanh
def add_tone_mark(word, tone_type, vtdd):
    vowels_with_marks = {
        'a': ('a', 'á', 'à', 'ả', 'ã', 'ạ'), 'ă': ('ă', 'ắ', 'ằ', 'ẳ', 'ẵ', 'ặ'),
        'â': ('â', 'ấ', 'ầ', 'ẩ', 'ẫ', 'ậ'), 'e': ('e', 'é', 'è', 'ẻ', 'ẽ', 'ẹ'),
        'ê': ('ê', 'ế', 'ề', 'ể', 'ễ', 'ệ'), 'i': ('i', 'í', 'ì', 'ỉ', 'ĩ', 'ị'),
        'o': ('o', 'ó', 'ò', 'ỏ', 'õ', 'ọ'), 'ô': ('ô', 'ố', 'ồ', 'ổ', 'ỗ', 'ộ'),
        'ơ': ('ơ', 'ớ', 'ờ', 'ở', 'ỡ', 'ợ'), 'u': ('u', 'ú', 'ù', 'ủ', 'ũ', 'ụ'),
        'ư': ('ư', 'ứ', 'ừ', 'ử', 'ữ', 'ự'), 'y': ('y', 'ý', 'ỳ', 'ỷ', 'ỹ', 'ỵ')
    }

    if tone_type == 0:
        return word

    vowel_index = -1
    if vtdd > 0 and vtdd <= len(word):
        if word[vtdd - 1] in vowels_with_marks:
            vowel_index = vtdd - 1

    if vowel_index == -1:
        return word

    original_vowel = word[vowel_index]
    if original_vowel in vowels_with_marks:
        marked_vowel = vowels_with_marks[original_vowel][tone_type]
        return word[:vowel_index] + marked_vowel + word[vowel_index+1:]

    return word

# region Xử Lý Vần
def XLV(sini: str) -> str:
    global NA_val_XLV_global

    if len(sini) > 0:
        if sini[0] == 'p' or sini[0] == 'P':
            return sini[1:]
    if len(sini) == 2:
        if sini[1] == 'p' or sini[1] == 'P':
            return sini[0]

    original_input_case = sini

    capitalize_first = False
    if original_input_case and original_input_case[0].isupper():
        capitalize_first = True

    all_caps = False
    if original_input_case and original_input_case.isupper():
        all_caps = True

    nhập = sini.lower()

    def apply_case_and_return(result_word):
        if all_caps and result_word:
            return result_word.upper()
        elif capitalize_first and result_word:
            return result_word[0].upper() + result_word[1:]
        return result_word

    if not (1 <= len(nhập) <= 4):
        return apply_case_and_return(sini)
    if not nhập.isalpha():
        return apply_case_and_return(sini)

    PAD = ''
    NA_val_XLV_global = ''
    cần_PAC = 0
    PAC = ''
    DT = 0

    first_char = nhập[0]
    PAD = PAD_RULES.get(first_char, '')
    if not PAD and first_char != 'a':
        return apply_case_and_return(sini)

    final_pad = PAD
    if PAD == 'c' or PAD == 'g' or PAD == 'ng':
        first_vowel_of_na = NA_RULES.get(nhập[1])[0][0] if len(nhập) > 1 and nhập[1] in NA_RULES else ''
        if first_vowel_of_na in ['i', 'y', 'e', 'ê']:
            if PAD == 'c':
                final_pad = 'k'
            elif PAD == 'g':
                final_pad = 'gh'
            elif PAD == 'ng':
                final_pad = 'ngh'
    elif PAD == 'gi':
        first_vowel_of_na = NA_RULES.get(nhập[1])[0][0] if len(nhập) > 1 and nhập[1] in NA_RULES else ''
        if first_vowel_of_na in ['i', 'y']:
            final_pad = 'g'
    elif PAD == 'q':
        if len(sini) > 1:
            if nhập[1] in ['a', 's', 'd', 'f', 'g', 'h', 'j', 'z', 'x', 'c', 'v', 'b', 'n', 'm']:
                return apply_case_and_return(sini)
            elif nhập[1] in ['q', 'w', 'e']:
                if nhập[1] == 'q':
                    NA_val_XLV_global = 'qa'
                elif nhập[1] == 'w':
                    NA_val_XLV_global = 'qă'
                elif nhập[1] == 'e':
                    NA_val_XLV_global = 'qe'
                else:
                    pass

    if len(nhập) > 1:
        second_char = nhập[1]
        na_info = NA_RULES.get(second_char)

        if na_info is None:
            return apply_case_and_return(sini)

        if not (PAD == 'q' and nhập[1] in ['q', 'w', 'e']):
            NA_val_XLV_global, cần_PAC = na_info

        if cần_PAC == 1:
            if len(nhập) > 2:
                third_char = nhập[2]
                if third_char in DT_INPUT_CHARS:
                    DT = DT_INPUT_CHARS[third_char]
                else:
                    return apply_case_and_return(sini)
            if len(nhập) > 3:
                fourth_char = nhập[3]
                if DT == 0 and fourth_char in DT_INPUT_CHARS:
                    DT = DT_INPUT_CHARS[fourth_char]
                else:
                    return apply_case_and_return(sini)
    else:
        if len(nhập) == 1 and nhập[0] in PAD_RULES:
            na_info = NA_RULES.get(nhập[0])
            if na_info:
                NA_val_XLV_global, cần_PAC = na_info
                if cần_PAC == 0:
                    van_info = VAN_RULES.get(NA_val_XLV_global)
                    if van_info:
                        van_text, vtdd_from_rules = van_info
                        pini_temp = add_tone_mark(van_text, DT, vtdd_from_rules)
                        return apply_case_and_return(pini_temp)
            return apply_case_and_return(sini)

    if len(nhập) > 2:
        third_char = nhập[2]
        temp_pac = PAC_RULES.get(third_char)
        if temp_pac:
            PAC = temp_pac

        if third_char in DT_INPUT_CHARS:
            if DT == 0:
                DT = DT_INPUT_CHARS[third_char]
            elif (cần_PAC == 2 and not PAC) or DT != 0:
                return apply_case_and_return(sini)

        if cần_PAC == 2 and not PAC:
            return apply_case_and_return(sini)

        if not PAC and DT == 0 and third_char not in PAC_RULES and third_char not in DT_INPUT_CHARS:
            return apply_case_and_return(sini)

    if len(nhập) > 3:
        fourth_char = nhập[3]

        if not PAC:
            temp_pac = PAC_RULES.get(fourth_char)
            if temp_pac:
                PAC = temp_pac
            elif cần_PAC == 2:
                return apply_case_and_return(sini)

        if DT == 0:
            if fourth_char in DT_INPUT_CHARS:
                DT = DT_INPUT_CHARS[fourth_char]
            else:
                if cần_PAC != 2:
                    return apply_case_and_return(sini)
                elif PAC:
                    pass
                elif not PAC and not fourth_char in PAC_RULES:
                    return apply_case_and_return(sini)
    if cần_PAC == 2 and not PAC:
        return apply_case_and_return(sini)

    final_word_part = ''
    mavan_key = NA_val_XLV_global
    if PAC != '':
        mavan_key += PAC

    van_info = VAN_RULES.get(mavan_key)

    if van_info:
        van_text, vtdd_from_rules = van_info
        final_word_part = add_tone_mark(van_text, DT, vtdd_from_rules)
    else:
        return apply_case_and_return(sini)

    pini = final_pad + final_word_part

    return apply_case_and_return(pini)

# region Gõ Outpput
def typing(word):
    keyboard.send('backspace')
    keyboard.write(word, delay=0)
    print('│Output: '+word+(' ' * (64-len(word)-10)+'')+'│')
    print('│                                                              │')

# region Khi Nhấn Phím
def on_key_event(event):
    global sini, pini, typed_word, is_active

    # Chỉ xử lý sự kiện nếu chế độ đang hoạt động
    if not is_active:
        return

    if event.event_type == keyboard.KEY_DOWN:
        is_modifier_pressed = (
            keyboard.is_pressed('ctrl') or
            #keyboard.is_pressed('shift') or
            keyboard.is_pressed('alt') or
            keyboard.is_pressed('windows')
        )

        non_typable_keys = [
            'esc', 'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12',
            'home', 'end', 'page up', 'page down', 'insert', 'delete', 'caps lock', 'tab',
            'up', 'down', 'left', 'right',
            'print screen', 'scroll lock', 'pause',
            'num lock' # Enter được giữ trong WORD_DELIMITERS để xử lý ngắt từ
        ]

        # Nếu là phím điều khiển đang được giữ HOẶC phím đó nằm trong danh sách non_typable_keys
        if is_modifier_pressed or event.name in non_typable_keys:
            pass
        elif event.name in WORD_DELIMITERS:
            global num
            num += 1
            print('│>>'+str(num)+(' ' * (64-len(str(num))-4))+'│')
            print('│Input: '+typed_word+(' ' * (64-len(typed_word)-9)+'│'))
            pini_result = XLV(typed_word)
            typing(pini_result)
            typed_word = ''
            keyboard.send(event.name)
            update_popup_text()
        elif event.name == 'backspace':
            typed_word = typed_word[:-1] if typed_word else ''
            # Không cần keyboard.send('backspace') ở đây nếu hook tự xử lý
        elif event.name == '\\':
            typed_word = typed_word[:-1] if typed_word else ''
            keyboard.send('backspace')
        elif event.name == '|':
            typed_word = ''
            keyboard.send('backspace')
        elif len(event.name) == 1 and event.name.isalpha() == True:
            if (event.name.isalpha() or event.name.isdigit() or event.name in r"!@#$%^&*()-_=+[{]}\|;:',<.>/?`~"):
                typed_word += event.name
                keyboard.send('backspace')
            else:
                pass
        else:
            pass

    sini = typed_word
    pini = XLV(typed_word)

    update_popup_text()

# region Update Popup
def update_popup_text():
    global t1_var, t2_var
    '''Hàm này sẽ cập nhật nội dung của T1 và T2 trong popup.'''
    if t1_var and t2_var:
        t1_var.set(sini)
        t2_var.set(pini)

def simulate_data_update():
    '''Hàm này chỉ làm nhiệm vụ gọi update_popup_text để làm mới hiển thị.'''
    update_popup_text()

# region Auto Update
def auto_update_data():
    '''Hàm này sẽ tự động cập nhật dữ liệu và lên lịch cho lần cập nhật tiếp theo.'''
    global popup_window
    if popup_window and popup_window.winfo_exists():
        simulate_data_update()
        popup_window.after(100, auto_update_data)
    else:
        pass


def update_titles():
    '''Cập nhật tiêu đề cửa sổ chính và popup dựa trên tên người dùng chọn.'''
    global popup_window, main_window_title_var, user_chosen_name_var
    chosen_name = user_chosen_name_var.get()
    new_title = f'{chosen_name} + key' if chosen_name else 'Bàn Phím Tiếng Việt Nhanh'
    main_window_title_var.set(new_title)
    if popup_window and popup_window.winfo_exists():
        popup_window.title(new_title)

# region Link URL
def show_more_info():
    webbrowser.open_new_tab('https://procyony.mmm.page/bptvn')



#

# region Update Hotkey
def update_hotkey_button_text():
    global hotkey_button, is_active
    chosen_hotkey_display = selected_hotkey_var.get()
    current_status = 'Bật' if is_active else 'Tắt'
    if chosen_hotkey_display == 'Chọn Hotkey': # Nếu chưa chọn hotkey, hiển thị mặc định
        hotkey_button.config(text=f'Chọn Hotkey ({current_status})')
    else:
        hotkey_button.config(text=f'Hotkey: {chosen_hotkey_display} ({current_status})')


# region Chọn Hotkey
def set_hotkey(*args):
    global selected_hotkey
    current_selection = selected_hotkey_var.get()

    # Hủy bind hotkey cũ nếu có
    if selected_hotkey:
        keyboard.remove_hotkey(selected_hotkey)
        print(f'│Đã hủy bind hotkey cũ: {selected_hotkey}' + (' ' * (64 - len(f'Đã hủy bind hotkey cũ: {selected_hotkey}') - 2)) + '│')
        print('│                                                              │')


    # Bind hotkey mới
    hotkey_value = HOTKEYS.get(current_selection)
    if hotkey_value:
        keyboard.add_hotkey(hotkey_value, toggle_active_state)
        selected_hotkey = hotkey_value
        print(f'│Đã thiết lập hotkey: {current_selection} ({hotkey_value})' + (' ' * (64 - len(f'Đã thiết lập hotkey: {current_selection} ({hotkey_value})') - 2)) + '│')
        print('│                                                              │')
    else:
        selected_hotkey = None
        print(f'│Không có hotkey nào được chọn hoặc hotkey không hợp lệ.' + (' ' * (64 - len(f'Không có hotkey nào được chọn hoặc hotkey không hợp lệ.') - 2)) + '│')
        print('│                                                              │')
    update_hotkey_button_text()


# region Tạo popup gõ
def create_topmost_popup():
    global t1_var, t2_var, popup_window, main_window_title_var

    if popup_window and popup_window.winfo_exists():
        popup_window.focus_set()
        return

    popup_window = tk.Toplevel()
    popup_window.configure(bg='#FFFFFF')
    popup_window.title(main_window_title_var.get())
    popup_window.geometry(f'{250}x{100}+{160}+{0}')
    popup_window.resizable(False, False)

    # THÊM DÒNG NÀY ĐỂ ĐẶT LOGO CHO TAB CỦA POPUP
    try:
        popup_window.iconbitmap('viqkey.ico') 
    except tk.TclError:
        print("Lỗi: Không tìm thấy file icon 'viqkey.ico' hoặc file không hợp lệ cho popup.")
    except Exception as e:
        print(f"Lỗi không xác định khi tải icon cho popup: {e}")
    # KẾT THÚC THÊM DÒNG NÀY

    popup_window.attributes('-topmost', True)

    popup_window.grid_rowconfigure(0, weight=1)
    popup_window.grid_rowconfigure(1, weight=1)

    t1_var = tk.StringVar(value=sini)
    t2_var = tk.StringVar(value=pini)

    label_t1 = ttk.Label(popup_window, textvariable=t1_var, font=('Segoe UI', 25))
    label_t1.grid(row=0, column=0, padx=5, pady=(0, 0), sticky='sw')

    label_t2 = ttk.Label(popup_window, textvariable=t2_var, font=('Segoe UI', 10))
    label_t2.grid(row=1, column=0, padx=5, pady=(0, 0), sticky='nw')

    popup_window.focus_set()

    auto_update_data()

# region Trạng Thái
def toggle_active_state():
    global is_active, typed_word
    typed_word = ''
    is_active = not is_active
    status_text = 'BẬT' if is_active else 'TẮT'
    print(f'│Trạng thái bộ gõ: {status_text}' + (' ' * (64 - len(f'Trạng thái bộ gõ: {status_text}') - 2)) + '│')
    print('│                                                              │')
    # Cập nhật trạng thái hiển thị trên giao diện (nếu có)
    update_hotkey_button_text()
    update_status_dot() # <--- GỌI HÀM NÀY KHI TRẠNG THÁI THAY ĐỔI

# === HÀM MỚI: CẬP NHẬT MÀU DẤU CHẤM TRẠNG THÁI ===
def update_status_dot():
    global is_active, status_dot_label
    if status_dot_label:
        if is_active:
            status_dot_label.config(foreground='green') # Màu xanh khi bật
        else:
            status_dot_label.config(foreground='red')   # Màu đỏ khi tắt

# === HÀM MỚI: TỰ ĐỘNG CẬP NHẬT DẤU CHẤM TRẠNG THÁI ===
def auto_update_status_dot():
    global root, status_dot_label
    if root and root.winfo_exists() and status_dot_label:
        update_status_dot()
        root.after(500, auto_update_status_dot) # Cập nhật sau mỗi 500ms (0.5 giây)
    else:
        pass

def close_application():
    """Hàm này sẽ đóng cửa sổ chính của ứng dụng."""
    root.destroy()

# region Main
if __name__ == '__main__':
    is_active = False
    keyboard.hook(on_key_event)

    root = tk.Tk()
    style = ttk.Style()
    style.theme_use('clam')
    root.configure(bg='#FFFFFF')
    
    try:
        root.iconbitmap('viqkey.ico') 
    except tk.TclError:
        # Lỗi thường xảy ra nếu file .ico không tồn tại hoặc không hợp lệ
        print("Lỗi: Không tìm thấy file icon 'viqkey.ico' hoặc file không hợp lệ.")
    except Exception as e:
        # Các lỗi khác có thể xảy ra
        print(f"Lỗi không xác định khi tải icon: {e}")

    user_chosen_name_var = tk.StringVar(value='')
    main_window_title_var = tk.StringVar(value='') # Set default title
    root.title(main_window_title_var.get())
    root.geometry(f'{170}x{100}+{-10}+{0}') # Tăng chiều cao để chứa nút hotkey và dấu chấm
    root.resizable(False, False)

    root.attributes('-topmost', True)

    style = ttk.Style()
    style.theme_use('clam')

    root.configure(bg='#FFFFFF')

    style.configure('TLabel', background='#FFFFFF', foreground='#000000')

    style.configure('Slogan.TLabel', font=('Segoe UI', 12), foreground='#000000')
    style.configure('Version.TLabel', font=('Segoe UI', 7), foreground='#000000')

    # Điều chỉnh style cho TButton nói chung (ảnh hưởng đến các nút 'Mở Popup', 'Tìm hiểu thêm')
    style.configure('TButton', font=('Segoe UI', 7), foreground='black', background='#e1f0ff', padding=0, relief='flat', focusthickness=0)
    style.map('TButton', background=[('active', '#beddff')], relief=[('pressed', 'groove'), ('!pressed', 'flat')])

    # ĐIỀU CHỈNH CỠ CHỮ CỦA OptionMenu
    style.configure('TMenubutton', font=('Segoe UI', 7)) 

    # THÊM STYLE CHO DẤU CHẤM TRẠNG THÁI
    style.configure('Status.TLabel', font=('Segoe UI', 15, 'bold')) # Cỡ chữ và in đậm cho dấu chấm

    style.configure('Placeholder.TEntry', foreground='white')
    style.configure('Normal.TEntry', foreground='white')

    style.configure('White.TFrame', background='#FFFFFF')
    logo_frame = ttk.Frame(root, style='White.TFrame')
    logo_frame.pack(pady=0, side=tk.TOP, padx=0)
    
    image_path = 'viqkey.png'
    desired_width = int(596/15)
    desired_height = int(655/15)

    try:
        pil_image = Image.open(image_path)
        pil_image_scaled = pil_image.resize((desired_width, desired_height), Image.LANCZOS)
        tk_image = ImageTk.PhotoImage(pil_image_scaled)
        label_with_image = tk.Label(logo_frame, image=tk_image, bg='#FFFFFF')
        label_with_image.pack(pady=0, side=tk.LEFT, padx=0)
        label_with_image.image = tk_image
    except FileNotFoundError:
        error_label = tk.Label(root, text=f'Không tìm thấy file ảnh: {image_path}')
        error_label.pack(pady=0)
    except Exception as e:
        error_label = tk.Label(root, text=f'Lỗi khi tải hoặc hiển thị ảnh: {e}')
        error_label.pack(pady=0)

    text_frame = ttk.Frame(logo_frame, style='White.TFrame')
    text_frame.pack(pady=0, side=tk.LEFT, padx=0)

    label_slogan = ttk.Label(text_frame, text='by pcyndev           ', style='Slogan.TLabel')
    label_slogan.pack(pady=(0, 0), side=tk.TOP, padx=0)

    label_version = ttk.Label(text_frame, text='ver 3.4.5 alpha: Hotkey                ', style='Version.TLabel')
    label_version.pack(pady=(0, 0), side=tk.BOTTOM, padx=0)

    button_frame = ttk.Frame(root, style='White.TFrame')
    button_frame.pack(pady=0)

    open_popup_button = ttk.Button(button_frame, text='POPUP', command=create_topmost_popup)
    open_popup_button.pack(pady=0, side=tk.LEFT, padx=0)

    learn_more_button = ttk.Button(button_frame, text='WEB', command=show_more_info)
    learn_more_button.pack(pady=0, side=tk.LEFT, padx=0)

    # Tạo một nút "Đóng ứng dụng"
    close_button = ttk.Button(button_frame, text="ĐÓNG", command=close_application)
    close_button.pack(pady=0)

    # Khung mới để chứa nút Hotkey và dấu chấm trạng thái
    hotkey_frame = ttk.Frame(root, style='White.TFrame')
    hotkey_frame.pack(pady=0, side=tk.TOP, padx=0)

    # Nút Dropdown cho Hotkey
    selected_hotkey_var = tk.StringVar(root)
    selected_hotkey_var.set('') # Giá trị mặc định

    hotkey_options = list(HOTKEYS.keys())

    hotkey_button = ttk.OptionMenu(hotkey_frame, selected_hotkey_var, selected_hotkey_var.get(), *hotkey_options, command=set_hotkey)
    hotkey_button.config(width=22)  # Đặt chiều rộng theo số ký tự
    hotkey_button.pack(pady=0, side=tk.LEFT, padx=(0,0)) # Đặt hotkey_button bên trái trong hotkey_frame
    
    # === THÊM CÁC BIẾN VÀ WIDGET CHO DẤU CHẤM TRẠNG THÁI ===
    status_dot_color_var = tk.StringVar(value='●') # Biến lưu màu của dấu chấm
    status_dot_label = ttk.Label(hotkey_frame, text='•', textvariable=status_dot_color_var, style='Status.TLabel', foreground='red')
    status_dot_label.pack(pady=0, side=tk.LEFT, padx=(0,0)) # Đặt dấu chấm bên phải trong hotkey_frame

    # === CẬP NHẬT TRẠNG THÁI NÚT VÀ DẤU CHẤM BAN ĐẦU ===
    update_hotkey_button_text()
    update_status_dot() # Gọi hàm cập nhật dấu chấm lần đầu

    # === BẮT ĐẦU VÒNG LẶP CẬP NHẬT DẤU CHẤM ===
    auto_update_status_dot()
    
    root.mainloop()
print('╰──────────────────────────────────────────────────────────────╯')