from Frontend.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus
)
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import os

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
DefaultMessage = f'''{Username} : Hello {Assistantname}! How are you?
{Assistantname} : Hello {Username} I'm doing well, how can I help you today?
'''
subprocesses = []
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]

def ShowDefaultChatIfNoChats():
    try:
        with open(r"Data\ChatLog.json", "r", encoding="utf-8") as file:
            if len(file.read().strip()) < 5:
                with open(TempDirectoryPath("Database.data"), "w", encoding="utf-8") as db_file:
                    db_file.write("")
                with open(TempDirectoryPath("Responses.data"), "w", encoding="utf-8") as resp_file:
                    resp_file.write(DefaultMessage)
    except FileNotFoundError:
        print("ChatLog.json not found. Creating default chat logs.")
        os.makedirs(os.path.dirname(r"Data\ChatLog.json"), exist_ok=True)
        with open(r"Data\ChatLog.json", "w", encoding="utf-8") as file:
            json.dump([], file)
        ShowDefaultChatIfNoChats()

def ReadChatLogJson():
    try:
        with open(r"Data\ChatLog.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        print("Error reading ChatLog.json. Returning empty data.")
        return []

def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""

    for entry in json_data:
        if entry["role"] == "user":
            formatted_chatlog += f"User: {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"Assistant: {entry['content']}\n"

    formatted_chatlog = formatted_chatlog.replace("User", Username + " ")
    formatted_chatlog = formatted_chatlog.replace("Assistant", Assistantname + " ")

    try:
        with open(TempDirectoryPath("Database.data"), "w", encoding="utf-8") as file:
            file.write(AnswerModifier(formatted_chatlog))
    except Exception as e:
        print(f"Error writing to Database.data: {e}")

def ShowChatsOnGUI():
    try:
        with open(TempDirectoryPath("Database.data"), "r", encoding="utf-8") as file:
            data = file.read()

        if data.strip():
            with open(TempDirectoryPath("Responses.data"), "w", encoding="utf-8") as resp_file:
                resp_file.write(data)
    except FileNotFoundError:
        print("Database.data not found.")

def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatsOnGUI()

InitialExecution()

def MainExecution():
    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""

    SetAssistantStatus("Listening...")
    Query = SpeechRecognition()
    ShowTextToScreen(f"{Username} : {Query}")
    SetAssistantStatus("*Proccessing*")
    Decision = FirstLayerDMM(Query)

    print(f"\nDecision: {Decision}\n")

    G = any(i.startswith("general") for i in Decision)
    R = any(i.startswith("realtime") for i in Decision)

    Merged_query = " and ".join(
        [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
    )

    for queries in Decision:
        if "generate" in queries:
            ImageGenerationQuery = str(queries)
            ImageExecution = True

    for queries in Decision:
        if not TaskExecution and any(queries.startswith(func) for func in Functions):
            run(Automation(list(Decision)))
            TaskExecution = True

    if ImageExecution:
        try:
            with open(r"Frontend\Files\ImageGeneration.data", "w") as file:
                file.write(f"{ImageGenerationQuery},True")

            p1 = subprocess.Popen(
                ["python", r"Backend\ImageGeneration.py"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                stdin=subprocess.PIPE, shell=True
            )
            subprocesses.append(p1)
        except Exception as e:
            print(f"Error Generating Image: {e}")

    if G and R:
        SetAssistantStatus("Searching...")
        Answer = RealtimeSearchEngine(QueryModifier(Merged_query))
        ShowTextToScreen(f"{Assistantname} : {Answer}")
        SetAssistantStatus("Answering...")
        TextToSpeech(Answer)
        return True
    else:
        for Queries in Decision:
            if "general " in Queries:
                SetAssistantStatus("*Proccessing*")
                QueryFinal = Queries.replace("general ", "")
                Answer = ChatBot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering...")
                TextToSpeech(Answer)
                return True
            elif "realtime" in Queries:
                SetAssistantStatus("*Proccessing*")
                QueryFinal = Queries.replace("realtime ", "")
                Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering...")
                TextToSpeech(Answer)
                return True
            elif "exit" in Queries:
                QueryFinal = "Okay, Bye!"
                Answer = ChatBot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering...")
                TextToSpeech(Answer)
                os._exit(1)

def FirstThread():
    while True:
        CurrentStatus = GetMicrophoneStatus()

        if CurrentStatus == "True":
            MainExecution()
        else:
            AIStatus = GetAssistantStatus()
            if "Available..." in AIStatus:
                sleep(0.1)
            else:
                SetAssistantStatus("Available...")

def SecondThread():
    GraphicalUserInterface()

if __name__ == "__main__":
    thread2 = threading.Thread(target=FirstThread, daemon=True)
    thread2.start()
    SecondThread()
