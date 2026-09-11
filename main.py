import json
import os
import subprocess
import time
import ollama
import pyaudio
import requests
from dotenv import load_dotenv

load_dotenv()
url = str(os.getenv("url"))
path = os.getenv("path")


def say(text: str):
    subprocess.run(["RHVoice-test", "-p", "aleksandr"], input=text.encode("utf-8"))


# from ollama import  chat
from vosk import KaldiRecognizer, Model

model = Model(path)
potok = False
recognizer = KaldiRecognizer(model, 48000)
mic = pyaudio.PyAudio()
stream = mic.open(
    format=pyaudio.paInt16, channels=1, rate=48000, input=True, frames_per_buffer=8192
)  #
stream.start_stream()
timefromepoch = 0
def askp(text : str):
    payload = {
        "model": "gemma3:4b",
        "messages": [
            {
                "role": "system",
                "content": " Ты - голосовой помощник по имени сырок.отвечай кратко и по делу,максимум - одно предложение,и не говори и так понятных вещей, и будь приветлив",
            },
            {"role": "user", "content": text},
        ],
        "stream": True,
    }
    response = requests.post(url, json=payload, stream=True)

    # Iterate over the response line by line as tokens are sent over the network
    #
    tosay = ""
    stopchars = {" ", ".", "," , ";", ":", "?", "!","", "-"}
    for line in response.iter_lines():
        if line:
            # Decode the byte line into a string and load the JSON payload
            chunk = json.loads(line.decode("utf-8"))
            content = chunk.get("message", {}).get("content", "")
            tosay += content
            if stopchars.__contains__(tosay[-1]):
                say(tosay)
                tosay = ""
def ask(text: str) -> str:  # функция для обработки запросов на сервер
    payload = {
        "model": "gemma3:4b",
        "messages": [
            {
                "role": "system",
                "content": " Ты - голосовой помощник по имени сырок.отвечай кратко и по делу, и будь приветлив",
            },
            {"role": "user", "content": text},
        ],
        "stream": False,
    }
    # try:
    print("strt")
    response = requests.post(url, json=payload, timeout=100)
    print("otp")
    response.raise_for_status()
    print("osh")
    print(response)
    print(response.status_code)
    if len(response.json().get("message", {}).get("content")) < 2:
        say("с серверами связаться не удалось,простите")
        return ""
    else:
        txt = response.json().get("message", {}).get("content")
        print(txt)
        return txt


def filteroutput(text):
    ot = ""
    ot = text.replace("**", "")
    ot = ot.replace("*  ", "")
    return ot


try:
    txt = ask("привет")
    print(txt)
    withoutemojis = filteroutput(txt)
    say(withoutemojis)
    # tts = gTTS(text=txt, lang="ru")
    # tts.save("speech.mp3")
    # os.system("mpg123 speech.mp3")
    # engine.say(txt)
    # engine.runAndWait()
    timefromepoch = time.time()
except:
    os.system("#mpg123 offline.mp3")
print("говорите")
while True:
    data = stream.read(4096, exception_on_overflow=False)
    if recognizer.AcceptWaveform(data):
        res = json.loads(recognizer.Result())
        text = res.get("text", "")
        print(text)
        if text.startswith("сырок") and (len(text) >= 6):
            # client = ollama.Client(host='index-ahead.gl.at.ply.gg:10989')
            promptunedited = text[5 : len(text)]
            promptedited = f"{promptunedited}"
            if potok:
                askp(promptedited)
            else:
                try:
                    txt = ask(promptedited)
                    print(txt)
                    withoutemojis = filteroutput(txt)
                    say(withoutemojis)
                    # tts = gTTS(text=txt, lang="ru")
                    # tts.save("speech.mp3")
                    # os.system("mpg123 speech.mp3")
                    # engine.say(txt)
                    # engine.runAndWait()
                    timefromepoch = time.time()
                except:
                    os.system("#mpg123 offline.mp3")

        elif len(text) > 5 and time.time() - timefromepoch < 20:
            promptunedited = text
            promptedited = f"{promptunedited}"
            if potok:
                askp(promptedited)
            else:
                try:
                    txt = ask(promptedited)
                    print(txt)
                    withoutemojis = filteroutput(txt)
                    say(withoutemojis)
                    # tts = gTTS(text=txt, lang="ru")
                    # tts.save("speech.mp3")
                    # os.system("#mpg123 speech.mp3")

                    # engine.say(txt)
                    # engine.runAndWait() helloex
                    timefromepoch = time.time()
                except:
                    os.system("#mpg123 offline.mp3")

        else:
            print("запрос не прошел")
