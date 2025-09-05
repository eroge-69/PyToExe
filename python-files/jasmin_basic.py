Python 3.13.7 (tags/v3.13.7:bcee1c3, Aug 14 2025, 14:15:11) [MSC v.1944 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
...     try:
...         query = r.recognize_google(audio, language="en-in")
...         print("You:", query)
...         return query.lower()
...     except:
...         return ""
...
... def chat_with_gpt(prompt):
...     try:
...         response = openai.ChatCompletion.create(
...             model="gpt-3.5-turbo",
...             messages=[{"role": "user", "content": prompt}]
...         )
...         return response["choices"][0]["message"]["content"]
...     except Exception as e:
...         return "Sorry, I could not connect to AI."
...
... if __name__ == "__main__":
...     speak("Hello, I am Jasmin. How can I help you?")
...     while True:
...         query = listen()
...         if query == "":
...             continue
...         if "stop" in query or "exit" in query or "quit" in query:
...             speak("Goodbye, have a nice day!")
...             break
...         else:
...             reply = chat_with_gpt(query)
...             speak(reply)

Traceback (most recent call last):
  File "<python-input-0>", line 4, in <module>
    import speech_recognition as sr
ModuleNotFoundError: No module named 'speech_recognition'
>>>
