from kannada_map import *  # Assuming this is your Kannada-to-Shreelipi mapping module
import sys
import re

kan_list = ['ಕ', 'ಖ', 'ಗ', 'ಘ', 'ಙ', 'ಚ', 'ಛ', 'ಜ', 'ಝ', 'ಞ', 'ಟ', 'ಠ', 'ಡ', 'ಢ', 'ಣ', 'ತ', 'ಥ', 'ದ', 'ಧ', 'ನ', 'ಪ', 'ಫ', 'ಬ', 'ಭ', 'ಮ', 'ಯ', 'ರ', 'ಲ', 'ವ', 'ಶ', 'ಷ', 'ಸ', 'ಹ', 'ಳ']
small_dict = {'ಕಿ': 'Q','ಖಿ': 'U','ಗಿ': 'X','ಘಿ': '\\','ಚಿ': 'b','ಛಿ': 'e','ಜಿ': 'i','ಝಿ': 'Äká','ಟಿ': 'q','ಠಿ': 't','ಡಿ': 'w','ಢಿ': '{','ಣಿ': '~','ತಿ': '£','ಥಿ': '¦','ದಿ': '©','ಧಿ': '˜','ನಿ': '¯','ಪಿ': '²','ಫಿ': 'µ','ಬಿ': '¹','ಭಿ': '¼','ವಿ': 'Ë','ಮಿ': 'Ëá','ಯಿ': 'Àá','ರಿ': 'Ä','ಲಿ': 'È','ಶಿ': 'Î','ಷಿ': 'Ñ','ಸಿ': 'Ô','ಹಿ': '×','ಳಿ': 'Ú','ಕ್ಷಿ': 'ü'}
big_dict = {'ಕೀ': 'Qà','ಖೀ': 'Uà','ಗೀ': 'Xà','ಘೀ': '\\à','ಚೀ': 'bà','ಛೀ': 'eà','ಜೀ': 'ià','ಝೀ': 'Äkáà','ಟೀ': 'qà','ಠೀ': 'tà','ಡೀ': 'wà','ಢೀ': '{à','ಣೀ': '~à','ತೀ': '£à','ಥೀ': '¦à','ದೀ': '©à','ಧೀ': '˜à','ನೀ': '¯à','ಪೀ': '²à','ಫೀ': 'µà','ಬೀ': '¹à','ಭೀ': '¼à','ಮೀ': 'Ëáà','ಯೀ': 'Àáà','ರೀ': 'Äà','ಲೀ': 'Èà','ವೀ': 'Ëà','ಶೀ': 'Îà','ಷೀ': 'Ñà','ಸೀ': 'Ôà','ಹೀ': '×à','ಳೀ': 'Úà','ಕ್ಷೀ': 'üà'}
ottakshara_dict = {'ಕ್ಷ': 'ûÜ','ಕ್ಷಿ': 'ü','ಕ್ಷೀ': 'üà','್ಷ': 'Ò','್ಕ': 'R','್': '…','್ಖ': 'V','್ಗ': 'Y','್ಘ': '^','್ಙ': '`','್ಚ': 'c','್ಛ': 'f','್ಜ': 'j','್ಝ': 'l','್ಞ': 'n','್ಟ': 'r','್ಠ': 'u','್ಡ': 'x','್ಢ': 'z','್ಣ': '¡','್ತ': '¤','್ಥ': '§','್ದ': 'ª','್ಧ': 'œ','್ನ': '°','್ಪ': '³','್ಫ' : '#','್ಬ': 'º','್ಭ': '½','್ಮ': '¾','್ಯ': 'Â','್ರ': 'Å','್ಲ': 'É','್ವ': 'Ì','್ಶ': 'Ï','್ಸ': 'Õ','್ಹ': 'Ø','್ಳ': 'Û','ರ್': 'ì','್ಕ್ರ': 'ð','್ಟೈ': 'ò','್ಟ್ರ': 'ó','್ತೈ': 'ô','್ಸ್ಕ' : 'ÕR', '್ತೃ': 'õ','್ತ್ಯ': 'ö','್ತ್ರ': '÷','್ರ್ಪ': 'ø','್ರೃ': 'ù','್ಸ್ರ': 'ú','ಜ್ಞ': 'ý'}
guni_list = ['Ý','æ','è']
#kan_dict= {'ಕ' : 'PÜ', 'ಖ' : 'S','ಗ' : 'WÜ','ಘ' : 'Z','ಙ' : '_','ಚ' : 'aÜ','ಛ' : 'dÜ','ಜ' : 'g','ಝ' : 'ÃÜká','ಞ' : 'm','ಟ' : 'o','ಠ' : 'sÜ','ಡ' : 'vÜ','ಢ' : 'yÜ','ಣ' : '|','ತ' : 'ñÜ','ಥ' : '¥Ü','ದ' : '¨Ü','ಧ' : '«Ü','ನ' : '®Ü','ಪ' : '±Ü','ಫ' : '¶Ü','ಬ' : 'Ÿ','ಭ' : '»Ü','ವ' : 'ÊÜ','ಮ' : 'ÊÜá','ಯ' : '¿á','ರ' : 'ÃÜ','ಲ' : 'Æ','ಶ' : 'ÍÜ','ಷ' : 'ÐÜ','ಸ' : 'ÓÜ','ಹ' : 'ÖÜ','ಳ' : 'ÙÜ'}

def kannada_to_shreelipi(kannada_text, dictionary):
    shreelipi_text = ""
    words = kannada_text.split()
    for word in words:
        #print(word)
        i = 0  # Initialize i to 0 for each word
        while i < len(word):  # Use while loop to control i
            char = word[i]

            # Handle "ಿ" for small_dict
            #print(char,shreelipi_text)
            if char == 'ರ' and i + 3 < len(word) and word[i + 1] == '್':
                #print("here",word[i+1],word[i+2])
                if word[i+2] == "\u200c" and word[i+2]!= len(word):
                    shreelipi_text+=dictionary[char][0]
                    shreelipi_text = shreelipi_text[:-1]+dictionary[word[i+1]][0]
                    i+=3
                    continue
                else:
                    a = char+word[i+1]
                    if word[i+3] == "ಿ":
                        b = word[i+2]+word[i+3]
                    elif word[i+3] == "್" and i+ 4 <len(word):
                            b = word[i+3]+word[i+4]
                            #print("Here",b)
                            shreelipi_text+=dictionary[word[i+2]][0]
                            if b in dictionary:
                                #print("Herre")
                                shreelipi_text+= dictionary[b][0]
                                if i+5 < len(word) and word[i+5] == "ು":
                                    shreelipi_text+=dictionary[word[i+5]][0]
                                    if a in dictionary:
                                        shreelipi_text+= dictionary[a][0]
                                        i+=6
                                        continue
                                if a in dictionary:
                                    shreelipi_text+= dictionary[a][0]
                                    i+=5
                                    continue

                            if a in dictionary:
                                shreelipi_text+= dictionary[a][0]
                                i+=4
                                continue
                    else:
                        b = word[i+2]
                    #print(b)
                    if b in dictionary:
                        shreelipi_text+=dictionary[b][0]
                    if a in dictionary:
                        shreelipi_text+= dictionary[a][0]
                    if word[i+3] == "ಿ":
                        i += 4
                        continue
                    else:
                        #print("here",char,word[i+3])
                        i += 3
                        continue
            elif char == 'ರ' and i + 2 < len(word) and word[i + 1] == '್':
                a = char+word[i+1]
                b = word[i+2]
                #print("Here")
                if b in dictionary:
                    shreelipi_text+=dictionary[b][0]
                if a in dictionary:
                    shreelipi_text+= dictionary[a][0]
                i += 3
                continue
            if char in kan_list and i + 1 < len(word) and word[i + 1] == "ಿ":
                #print('Here in "ಿ"')
                a = char + word[i + 1]
                if a in small_dict:
                    shreelipi_text += small_dict[a]
                i += 2  # Move to the next character after 'ಿ'
                continue
            else:
                if char == "ಿ" and word[i-1] in kan_list:
                    a = word[i-1]+char
                    #print(a)
                    if a in small_dict:
                        #print(small_dict[a])
                        shreelipi_text += small_dict[a]
                    i+=1
                    continue
            # Handle "ೀ" for big_dict
            if char in kan_list and i + 1 < len(word) and word[i + 1] == "ೀ":
                a = char + word[i + 1]
                if a in big_dict:
                    shreelipi_text += big_dict[a]
                i += 2  # Move to the next character after 'ೀ'
                continue
            else:
                if char == "ೀ" and word[i-1] in kan_list:
                    a = word[i-1]+char
                    if a in big_dict:
                        shreelipi_text += big_dict[a]
                    i+=1
                    continue
            if char == "ವ" and i + 3 < len(word) and word[i+1] == '್':
                a = char+word[i+3]
                b = word[i+1]+word[i+2]
                if a in dictionary.keys():
                    #print(a)
                    shreelipi_text += dictionary[a][0]
                    if b in ottakshara_dict.keys():
                        shreelipi_text += ottakshara_dict[b]
                        i+=4
                        continue
                    else:
                        i+=2
                        continue
            elif char == "ವ" and i + 1 < len(word):
                a = char+word[i+1]
                if a in dictionary.keys():
                    #print(a)
                    shreelipi_text += dictionary[a][0]
                    i+=2
                    continue
            
            # Handle "್" and ottakshara (conjunct consonants)
            if char == '್' and i + 2 < len(word) and word[i + 1] in kan_list and word[i+2] =="ಿ":
                a = char + word[i + 1]
                #print('here in"ಿ',a)
                b = word[i+1]+word[i+2]
                #print(b)
                if b in small_dict:
                    #print(word[i-1],word[i+1])
                    if word[i-1] == word[i+1]:
                        if "Ü" in shreelipi_text[-1]:
                            shreelipi_text = shreelipi_text[:-2]+small_dict[b]
                        else:
                            shreelipi_text = shreelipi_text[:-1]+small_dict[b]
                    else:
                        c = word[i-1]+word[i+2]
                        if "Ü" in shreelipi_text[-1]:
                            shreelipi_text = shreelipi_text[:-2]+small_dict[c]
                        else:
                            shreelipi_text = shreelipi_text[:-1]+small_dict[c]
                #print(shreelipi_text)
                if a in ottakshara_dict:
                    #print(ottakshara_dict[a])
                    shreelipi_text += ottakshara_dict[a]
                    
                i += 3  # Move to the next character after '್'
                continue
            if char in kan_list and i + 3 < len(word) and word[i+1] == '್' and word[i + 2] in kan_list and word[i+3] == "ೀ":
                a = char + word[i + 3]
                #print('here in ',a)
                b = word[i+1]+word[i+2]
                if a in big_dict:
                    #print(b)
                    if word[i-1] == word[i+1]:
                        if "Ü" in shreelipi_text[-1]:
                            shreelipi_text = shreelipi_text[:-2]+big_dict[a]
                        else:
                            shreelipi_text = shreelipi_text[:-1]+big_dict[a]
                    else:
                        #print(shreelipi_text)
                        if "Ü" in shreelipi_text[-1]:
                            shreelipi_text = shreelipi_text+big_dict[a]
                        else:
                            shreelipi_text = shreelipi_text+big_dict[a]
                if b in ottakshara_dict:
                    #print(ottakshara_dict[b])
                    shreelipi_text += ottakshara_dict[b]
                    
                i += 4  # Move to the next character after '್'
                continue
            elif char in kan_list and i + 5 < len(word) and word[i+1] == '್' and word[i + 2] in kan_list and word[i + 3] == '್' and word[i + 4] in kan_list and word[i+5] =="ಿ":
                a = char + word[i+5]
                b = word[i+1] + word[i+2]+word[i+3]+word[i+4]
                if a in small_dict:
                    #print(b)
                    if word[i-1] == word[i+1]:
                        if "Ü" in shreelipi_text[-1]:
                            shreelipi_text = shreelipi_text[:-2]+small_dict[a]
                        else:
                            shreelipi_text = shreelipi_text[:-1]+small_dict[a]
                    else:
                        if "Ü" in shreelipi_text[-1]:
                            shreelipi_text = shreelipi_text[:-1]+small_dict[a]
                        else:
                            shreelipi_text = shreelipi_text+small_dict[a]
                if b in ottakshara_dict:
                    #print(ottakshara_dict[b])
                    shreelipi_text += ottakshara_dict[b]
                i+=6
                continue
            elif char in kan_list and i + 5 < len(word) and word[i+1] == '್' and word[i + 2] in kan_list and word[i + 3] == '್' and word[i + 4] in kan_list and word[i+5] =="ೀ":
                a = char + word[i+5]
                b = word[i+1] + word[i+2]+word[i+3]+word[i+4]
                if a in big_dict:
                    #print(b)
                    if word[i-1] == word[i+1]:
                        if "Ü" in shreelipi_text[-1]:
                            shreelipi_text = shreelipi_text[:-2]+big_dict[a]
                        else:
                            shreelipi_text = shreelipi_text[:-1]+big_dict[a]
                    else:
                        #print(shreelipi_text)
                        if "Ü" in shreelipi_text[-1]:
                            shreelipi_text = shreelipi_text+big_dict[a]
                        else:
                            shreelipi_text = shreelipi_text+big_dict[a]
                if b in ottakshara_dict:
                    #print(ottakshara_dict[b])
                    shreelipi_text += ottakshara_dict[b]
                i+=6
                continue
            elif char == '್' and i + 1 < len(word) and word[i + 1] in kan_list:
                a = char + word[i + 1]
                #print("here in else",a)
                if a in ottakshara_dict:
                    #print(ottakshara_dict[a])
                    shreelipi_text += ottakshara_dict[a]
                    #print(shreelipi_text)
                i += 2  # Move to the next character after '್'
                continue

            # Handle individual character mapping
            if char in dictionary:
                shreelipi_text += dictionary[char][0]  # Get mapped value from dictionary
            else:
                #print("Here in else")
                # If no mapping, keep the character as is (or handle differently if needed)
                shreelipi_text += char

            i += 1  # Move to the next character
        shreelipi_text += " "  # Add space between words
    #print(shreelipi_text)
        
    final_text = ""
    i = 0
    while i < len(shreelipi_text):
        wor = shreelipi_text[i]
        #print(wor,final_text)
        if wor == "¿" and shreelipi_text[i+1]=="À":
            i+=1
            continue
#         if wor == "Ü" and i+3 < len(shreelipi_text) and shreelipi_text[i+1] == "ã" and shreelipi_text[i+2] == "ì" and shreelipi_text[i+3] == "æ":
#             final_text+=wor+shreelipi_text[i+1]+shreelipi_text[i+2]
#             i+=4
#             continue
        if wor == "Ü" and i + 2 < len(shreelipi_text) and " " not in shreelipi_text[i+1:i+3] and shreelipi_text[i+1] in ottakshara_dict.values() and shreelipi_text[i+2] == "…":
            #print("Here",shreelipi_text[i+1],shreelipi_text[i+2])
            if shreelipi_text[i+3] == " ":
                #print("Here")
                if shreelipi_text[i+1] == "ì":
                    final_text = final_text+shreelipi_text[i+2]+shreelipi_text[i+1]
                    i+=4
                    continue
                else:
                    final_text = final_text+shreelipi_text[i+1]+shreelipi_text[i+2]
                    i+=3
                    continue
            else:
                final_text = final_text+shreelipi_text[i+1]+shreelipi_text[i+2]
                i+=3
                continue
        if wor == "Ü" and i + 3 < len(shreelipi_text) and " " not in shreelipi_text[i+1:i+4] and shreelipi_text[i+1] in ottakshara_dict.values() and shreelipi_text[i+2] == "ì":
            #print("Here",final_text+shreelipi_text[i+1]+shreelipi_text[i+2])
            if shreelipi_text[i+3] == "…":
                final_text = final_text+shreelipi_text[i+3]+shreelipi_text[i+1]+shreelipi_text[i+2]
                i+=4
                continue
            else:
                final_text = final_text+wor+shreelipi_text[i+1]+shreelipi_text[i+2]
                i+=3
                continue
        elif wor == "Ü" and i + 1 < len(shreelipi_text) and shreelipi_text[i+1] == "…":
            final_text = final_text+shreelipi_text[i+1]
            i+=2
            continue
        elif wor == "Ü" and i + 1 < len(shreelipi_text) and shreelipi_text[i+1] in guni_list:
            #print("Here",wor,shreelipi_text[i+1])
            i += 1  # Skip the next character
            continue
            
        elif (wor == "Ê" and i + 4 < len(shreelipi_text) and " " not in shreelipi_text[i+1:i+5] and shreelipi_text[i+1] == "Ü" and shreelipi_text[i+2] == "á" and shreelipi_text[i+3] == 'æ'):
            #print("Here")
            if shreelipi_text[i+4] == "ã":
                final_text+=wor+shreelipi_text[i+3]+shreelipi_text[i+4]
                i+=5
                continue
            else:
                final_text += wor+shreelipi_text[i+3]
                shreelipi_text = shreelipi_text[:i+3] + shreelipi_text[i+4:]  # Update string
                i += 2  # Move index past the modified part
                continue
        elif wor == "Ê" and i + 4 < len(shreelipi_text) and " " not in shreelipi_text[i+1:i+5] and shreelipi_text[i+1] == "Ü" and shreelipi_text[i+2] == "á" and shreelipi_text[i+3] in ottakshara_dict.values() and shreelipi_text[i+4] == "æ":
            #print("Here")
            if i + 4 < len(shreelipi_text) and shreelipi_text[i+5] == "ã":
                final_text+= wor+shreelipi_text[i+4]+shreelipi_text[i+5]+shreelipi_text[i+3]
                i+=6
                continue
            else:
                final_text+=wor+shreelipi_text[i+3]+shreelipi_text[i+4]
                i+=5
                continue
        elif wor == "Ê" and i + 3 < len(shreelipi_text) and " " not in shreelipi_text[i+1:i+4] and shreelipi_text[i+1] == "Ü" and shreelipi_text[i+2] == "á" and shreelipi_text[i+3] == "æ":
            #print("Here")
            final_text+=wor+shreelipi_text[i+3]+shreelipi_text[i+2]
            i+=4
            continue
        elif wor == "Ã" and i+4 < len(shreelipi_text) and " " not in shreelipi_text[i+2:i+5] and "k" in shreelipi_text[i+2:i+5] and shreelipi_text[i+1] =="Ü" and shreelipi_text[i+4] == "æ":
            #print("here")
            final_text+= wor + shreelipi_text[i+4]
            shreelipi_text = shreelipi_text[:i+4]+shreelipi_text[i+5:]
            i+=2
            continue
        elif (wor == "Ü" and i + 2 < len(shreelipi_text) and shreelipi_text[i+1] in ottakshara_dict.values() and shreelipi_text[i+2] in guni_list):
            #print("here in skip")
            i += 1  # Skip the next two characters
            continue
        elif wor == "S" and i+2 < len(shreelipi_text) and shreelipi_text[i+1] in ottakshara_dict.values() and (shreelipi_text[i+2] == "Ý" or shreelipi_text[i+2] == "æ" or shreelipi_text[i+1] == "…"):
            final_text+="T"+shreelipi_text[i+2]+shreelipi_text[i+1]
            i+=3
            continue
        elif wor == "S" and i+1 < len(shreelipi_text) and (shreelipi_text[i+1] == "Ý" or shreelipi_text[i+1] == "æ" or shreelipi_text[i+1] == "…"):
            final_text+="T"+shreelipi_text[i+1]
            i+=2
            continue
        elif wor == "o" and i+2 < len(shreelipi_text) and shreelipi_text[i+1] in ottakshara_dict.values() and (shreelipi_text[i+2] == "Ý" or shreelipi_text[i+2] == "æ" or shreelipi_text[i+1] == "…"):
            #print("Here")
            if shreelipi_text[i+1] == "…":
                final_text+="p"+shreelipi_text[i+1]
                i+=2
                continue
            else:
                final_text+="p"+shreelipi_text[i+2]+shreelipi_text[i+1]
                i+=3
                continue
        elif wor == "o" and i+1 < len(shreelipi_text) and (shreelipi_text[i+1] == "Ý" or shreelipi_text[i+1] == "æ" or shreelipi_text[i+1] == "…"):
            #print("here")
            final_text+="p"+shreelipi_text[i+1]
            i+=2
            continue
        elif wor == "ì" and i + 1 < len(shreelipi_text) and (shreelipi_text[i+1] == "á" or shreelipi_text[i+1] == "ã"):
            #print("Here")
            final_text += shreelipi_text[i+1]+wor
            i+=2
            continue
        elif wor == "ì" and i + 2 < len(shreelipi_text) and shreelipi_text[i+1] in guni_list and (shreelipi_text[i+2] == "á" or shreelipi_text[i+2] == "ã"):
            #print("Here1",shreelipi_text[i:])
            final_text += shreelipi_text[i+1]+shreelipi_text[i+2]+wor
            i+=3
            continue
        elif wor == "ì" and i + 1 < len(shreelipi_text) and shreelipi_text[i+1] in guni_list:
            #print("Here2")
            final_text += shreelipi_text[i+1]+wor
            i+=2
            continue
        elif wor == "ì" and i + 1 < len(shreelipi_text) and shreelipi_text[i+1] == "…":
            #print("here3")
            final_text+= shreelipi_text[i+1]+wor
            i+=2
            continue
#         elif wor == "Ê" and i + 2 <len(shreelipi_text) and shreelipi_text[i+1] == "Ý" and shreelipi_text[i+2] == "á":
#             final_text+=wor+shreelipi_text[i+2]+shreelipi_text[i+1]
#             i+=3
#             continue
        elif wor == "¿" and i + 4 < len(shreelipi_text) and shreelipi_text[i+1] == "á" and " " not in shreelipi_text[i+1:i+5]:
            #print("here",shreelipi_text[i+2])
            if shreelipi_text[i+2] == "à":
                final_text+= "Ááà"
                i += 3
                continue
            elif shreelipi_text[i+2] == "æ":
                #print("here")
                if shreelipi_text[i+3] == "ã":
                    final_text+= "Áã"
                    i += 4
                    continue
                else:
                    final_text+= "Áá"
                    i += 3
                    continue
            elif shreelipi_text[i+2] == "ç":
                final_text+= "Ááç"
                i += 3
                continue
            if shreelipi_text[i+3] == "æ":
                if shreelipi_text[i+4] == "ã" and shreelipi_text[i+5] == "à":
                    final_text+= "Áãà"+ shreelipi_text[i+2]
                    i += 6
                    continue
                elif shreelipi_text[i+4] == "ã":
                    final_text+= "Áã"+ shreelipi_text[i+2]
                    i += 5
                    continue
                else:
                    final_text+= "Áá"+ shreelipi_text[i+2]
                    i += 4
                    continue
            else:
                final_text += wor
        elif wor == "¿" and i + 2 < len(shreelipi_text) and shreelipi_text[i+1] == "á":
            #print("here",shreelipi_text[i+2])
            if shreelipi_text[i+2] == "à":
                final_text+= "Ááà"
                i += 3
                continue
            elif shreelipi_text[i+2] == "æ":
                #print("here")
                if shreelipi_text[i+3] == "ã":
                    final_text+= "Áã"
                    i += 4
                    continue
                else:
                    final_text+= "Áá"
                    i += 3
                    continue
            elif shreelipi_text[i+2] == "ç":
                final_text+= "Ááç"
                i += 3
                continue
            else:
                final_text += wor
        elif (wor == "±" or wor == "¶")and i +1 < len(shreelipi_text):
            if shreelipi_text[i+1] == "Ü" and i + 2 < len(shreelipi_text) and shreelipi_text[i+2] in guni_list:
                #print("Here",wor,shreelipi_text[i+1])
                if shreelipi_text[i+2] == "ã":
                    final_text+=wor+"ä"
                    i+=2
                    continue
                elif i + 3 < len(shreelipi_text) and shreelipi_text[i+3] == "ã":
                    #print("here")
                    shreelipi_text = shreelipi_text[:i+3]+"ä"+shreelipi_text[i+4:]
                    final_text+=wor
                    i+=1
                    continue
                else:
                    final_text += wor
            elif shreelipi_text[i+1] == "Ü" and i + 2 < len(shreelipi_text) and shreelipi_text[i+2] == "á":
                    final_text+=wor+"Üâ"
                    i+=3
                    continue
            elif shreelipi_text[i+1] == "Ü" and i + 2 < len(shreelipi_text) and shreelipi_text[i+2] == "ã":
                    final_text+=wor+"Üä"
                    i+=3
                    continue
            else:
                final_text += wor
        else:
            final_text += wor
        
        i += 1 
    
    final_uni_text = ""
    i = 0
    while i < len(final_text):
        wo = final_text[i]
        if wo == "ì" and i+1<len(final_text) and final_text[i+1] == "à":
            final_uni_text+= final_text[i+1]+wo
            i+=2
            continue
        elif (wo == "¶" or wo == "±") and i+2 < len(final_text) and final_text[i+2] == "ã":
            final_uni_text+=wo+final_text[i+1]+"ä"
            i+=3
            continue
        elif (wo == "¶" or wo == "±") and i+2 < len(final_text) and final_text[i+2] == "á":
            final_uni_text+=wo+final_text[i+1]+"â"
            i+=3
            continue
        elif (wo == "¶" or wo == "±") and i+3 < len(final_text) and final_text[i+2] in ottakshara_dict.values() and final_text[i+3] == "á":
            final_uni_text+=wo+final_text[i+1]+"â"+final_text[i+2]
            i+=4
            continue
        elif (wo == "¶" or wo == "±") and i+3 < len(final_text) and final_text[i+2] in ottakshara_dict.values() and final_text[i+3] == "ã":
            final_uni_text+=wo+final_text[i+1]+"ä"+final_text[i+2]
            i+=4
            continue
        elif (wo == "¶" or wo == "±") and i+3 < len(final_text) and final_text[i+1] in ottakshara_dict.values() and final_text[i+3] == "á":
            final_uni_text+=wo+final_text[i+2]+"â"+final_text[i+1]
            i+=4
            continue
        elif (wo == "¶" or wo == "±") and i+3 < len(final_text) and final_text[i+1] in ottakshara_dict.values() and final_text[i+3] == "ã":
            final_uni_text+=wo+final_text[i+2]+"ä"+final_text[i+1]
            i+=4
            continue
        elif wo == "|" and i+2 < len(final_text) and final_text[i+1] in ottakshara_dict.values() and final_text[i+2] == "æ":
            final_uni_text+="O"+final_text[i+2]+final_text[i+1]
            i+=3
            continue
        elif wo == "|" and i+1 < len(final_text) and final_text[i+1] == "æ":
            final_uni_text+="O"+final_text[i+1]
            i+=2
            continue
        else:
            final_uni_text += wo
        i+=1
    return final_uni_text


def read_file(input_file_path):
    with open(input_file_path, 'r', encoding='utf-8') as file:
        return file.readlines()

def write_file(output_file_path, text):
    with open(output_file_path, 'w', encoding='utf-8') as file:
        for i in range(len(text)):
            line = text[i]+"\n"
            file.write(line)

# Example usage for reading input file, converting, and writing output file
input_file_path = sys.argv[1]
output_file_path = sys.argv[2]


# Read Kannada text from file
kannada_text = read_file(input_file_path)

# Convert to Shreelipi text
all_lines = []
for i in range(len(kannada_text)):
    line = str(kannada_text[i].strip())
    kannada_text_with_space = re.sub(r'(\S)([,.!?;:])', r'\1 \2', line)
    shreelipi_text = kannada_to_shreelipi(kannada_text_with_space, kannada_shreelipi)
    kannada_text_out = re.sub(r'\s+([,.!?;:])', r'\1', shreelipi_text)
    all_lines.append(kannada_text_out)

# Write the converted text to an output file
write_file(output_file_path, all_lines)

print(f"Conversion complete. Shreelipi text written to {output_file_path}.")

