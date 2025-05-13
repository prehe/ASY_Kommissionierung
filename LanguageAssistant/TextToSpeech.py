from gtts import gTTS
from playsound import playsound
import os

def text_to_speech(text, lang="de"):
    tts = gTTS(text=text, lang=lang)
    tts.save("output.mp3")
    playsound("output.mp3")
    os.remove("output.mp3")