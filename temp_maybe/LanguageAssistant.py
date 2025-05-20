import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
import os

r = sr.Recognizer()

def text_to_speech(text, lang="de",):
    tts = gTTS(text=text, lang=lang)
    tts.save("output.mp3")
    playsound("output.mp3")
    os.remove("output.mp3")

def speech_to_text(voiceLanguage="en-US"):
    with sr.Microphone() as source:
        print("Waiting for speech input...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)

        try:
            text = r.recognize_google(audio, language=voiceLanguage)
            return text
        except sr.UnknownValueError:
            return "Voice input could not be interpreted."
        except sr.RequestError:
            return "Connection error with the speech recognition service."
        
def check_input(expected, spoken_text):
    if spoken_text.lower() == expected.lower():
        return True
    else:
        return False

inputs = [
    ["Sage das Wort Next zu mir", "next"],
    ["Sprich den Begriff Back aus", "back"],
    ["Gib mir das Sprachsignal Start", "start"],
    ["Beende mich mit dem Stichwort Stop", "stop"]
]

for prompt, expected in inputs:
    print(prompt)
    text_to_speech(prompt)
    spoken_text = speech_to_text()
    if check_input(expected, spoken_text):        
        text_to_speech("Eingabe richtig erkannt")
        print(f"Richtig erkannt! Erwartet: {expected}, Gesprochen: {spoken_text}")
    else:
        text_to_speech("Keine erwartete Eingabe erkannt")
        print(f"Keine erwartete Eingabe erkannt! Erwartet: {expected}, Gesprochen: {spoken_text}")