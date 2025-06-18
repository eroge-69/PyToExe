from google.cloud import texttospeech
import subprocess
import time
from google.cloud import speech_v1
from google.cloud.speech_v1 import enums
from google.cloud.speech_v1 import types
import io
import soundfile
import sounddevice
import scipy
import subprocess
import time
from scipy.io.wavfile import write
import datetime
import webbrowser
import random
import keyboard
import time

#SST-
j_path2 = r'../assets/json/DrHahnchenflugel_STT_TTS.json'
client2 = speech_v1.SpeechClient.from_service_account_json(j_path2)


def VTT(time):
    sampleRate = 44100
    recDurationSeconds = time
    totalNumSamples = int(sampleRate * recDurationSeconds)

    print("Started Recording............")
    myRecording = sounddevice.rec(totalNumSamples, sampleRate, 1)
    sounddevice.wait()
    print("Finished")

    write("Luigi_Rec.wav", sampleRate, myRecording)
    data, recordingSampleRate = soundfile.read("Luigi_Rec.wav")
    soundfile.write("Luigi_Rec.flac", data, sampleRate)
    encoding = enums.RecognitionConfig.AudioEncoding.FLAC
    language_code = 'en-CA'
    config = {'encoding': encoding, 'sample_rate_hertz': sampleRate, 'language_code': language_code}
    myAduiFile = r"Luigi_Rec.flac"


    with io.open(myAduiFile, 'rb') as audio_file:
        content = audio_file.read()
        audio = types.RecognitionAudio(content=content)
        response= client2.recognize(config, audio)
    try:
        return response.results[0].alternatives[0].transcript.lower()
    except:
        return None
#-SST

#TTS-
j_path = r'../assets/json/speech_creds.json'
client = texttospeech.TextToSpeechClient.from_service_account_json(j_path)
language_code = 'en-CA'  #'es-MX'  'ru-RU' 'en-GB'
gender = texttospeech.SsmlVoiceGender.MALE  # gender = texttospeech.SsmlVoiceGender.FEMALE #gender = texttospeech.SsmlVoiceGender.NEUTRAL

voice = texttospeech.VoiceSelectionParams(language_code=language_code, ssml_gender=gender)

audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

def textToSpeech(text, delay=None):
    if (delay==None):
        delay = len(text)*0.1
    synthesis_input = texttospeech.SynthesisInput(text=text)
    response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
    with open("soundfile.mp3", "wb") as out:
        out.write(response.audio_content)
    path_to_player = r"C:\Program Files (x86)\Windows Media Player\wmplayer.exe"
    path_to_file= r"C:\Users\Admin\mu_code\Ai Assistant\Ai Assistant_main\C4\soundfile.mp3"
    process = subprocess.Popen([path_to_player, path_to_file])
    time.sleep(delay)
    process.kill()
#-TTS

#Main-
print("loaded")
running = True
textToSpeech("Hello I am Eddie 1 point o. How can I help you today?")
print("check point")
password = 'def life(torah):'
num = random.randint(0,1)
'''
if (num == 0):
    textToSpeech("Head's Win")
if (num == 1):
    textToSpeech("Tail's Win")
'''
while(running):

    variable = VTT(5)
    print(str(variable))






    '''if("eddie" in variable and "open youtube" ):
        webbrowser.open_new_tab("https://www.youtube.com/")'''
    if("eddie open my website" in variable or "open my website" in variable ):
        webbrowser.open_new_tab("https://www.tiny.cc/mbsites")
    if("eddie play chess" in variable or "eddie let's play chess" in variable and "play chess" in variable ):
        webbrowser.open_new_tab("https://www.coolmathgames.com/0-chess")
    if("eddie let's play checkers" in variable or"eddie play checkers" in variable or "play checkers" in variable ):
        webbrowser.open_new_tab("https://www.coolmathgames.com/0-checkers")
    if("today date" in variable or "eddie" in variable and "today date" in variable):
        dateToday = datetime.datetime.now()
        dateText = dateToday.strftime("%A") + " " + dateToday.strftime("%B") + " " + dateToday.strftime("%C")
        textToSpeech(dateText)
    if("eddie play head or tail" in variable or "play head or tail" in variable):
        webbrowser.open_new_tab("https://www.google.com/search?client=firefox-b-d&channel=entpr&q=flip+a+coin")
    if('eddie flip a coin' in variable or "flip a coin" in variable):
        webbrowser.open_new_tab("https://www.google.com/search?client=firefox-b-d&channel=entpr&q=flip+a+coin")
    if("eddie open google" in variable or "open google" in variable ):
        webbrowser.open_new_tab("https://www.google.com")
    if('eddie open my mail' in variable or "open my mail" in variable):
        webbrowser.open_new_tab("https://mail.google.com/mail/u/1/?hl=en#inbox")
    if('eddie open email' in variable or "open email" in variable):
        webbrowser.open_new_tab("https://mail.google.com/mail/u/1/?hl=en#inbox")
    if('eddie open gmail' in variable or "open gmail" in variable):
        webbrowser.open_new_tab("https://mail.google.com/mail/u/1/?hl=en#inbox")
    if("eddie open number one youtube channel" in variable or "open number one youtube channel" in variable):
        webbrowser.open_new_tab("https://www.youtube.com/@rabbidavidelmaleh6365")
    if("eddie open cool math game" in variable or "open cool math game" in variable ):
        webbrowser.open_new_tab("https://www.coolmathgames.com/")
    if("eddie email mom" in variable or "email mom" in variable ):
        counter = 1
        counter2 = 1
        counter3 = 1
        webbrowser.open_new_tab("https://mail.google.com/mail/u/1/?hl=en#inbox")
        time.sleep(5)

        while(counter < 13):
            keyboard.press_and_release('tab')
            counter += 1
            time.sleep(0.5)

        time.sleep(1)
        keyboard.press_and_release('enter')
        time.sleep(1)
        keyboard.write('jsbitton@gmail.com')
        keyboard.press_and_release('enter')
        time.sleep(3)
        keyboard.press_and_release('tab')
        time.sleep(3)
        keyboard.write("To MOM - I Love You (This email was made from code!!!!!)")
        time.sleep(3)
        keyboard.press_and_release('tab')
        time.sleep(3)
        while(counter3 < 11):
            keyboard.write("This is coded, YAAAAAA!!")
            keyboard.write("Baruch Hashem")
            keyboard.write('\n')
            counter3 += 1
        keyboard.write('This email was made from code!!!!!')
        keyboard.press_and_release('tab')
        keyboard.press_and_release('enter')

    if('eddie repeat after me' in variable or 'repeat after me' in variable):
        time.sleep(3)
        textToSpeech("Ok                             ")
        variable4 = VTT(5)
        textToSpeech(variable4+"                              ")

    if('eddie search up' in variable or 'search up' in variable):
        textToSpeech("What do you want to search up?")
        textToSpeech("Please wait 20 seconds")
        variable2 = VTT(5)
        keyboard.press_and_release('win+r')
        time.sleep(1)
        keyboard.write('firefox')
        keyboard.press_and_release('enter')
        time.sleep(1)
        keyboard.write(variable2)
        keyboard.press_and_release('enter')

    if('eddie creates with ai' in variable or 'creates with ai' in variable):
        textToSpeech("What do you want to create with ai?")
        variable3 = VTT(5)
        textToSpeech("Please wait 20 seconds")
        keyboard.press_and_release('win+r')
        time.sleep(1)
        keyboard.write('firefox')
        time.sleep(5)
        keyboard.press_and_release('enter')
        time.sleep(3)
        keyboard.write('chatgpt.com')
        keyboard.press_and_release('enter')
        time.sleep(3)
        keyboard.write(variable3)
        keyboard.press_and_release('enter')
# and 'eddie or 'eddy' in variable



    time.sleep(1)
textToSpeech("program is ending")
print("program ended")






