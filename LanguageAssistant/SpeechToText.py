import speech_recognition as sr
import threading
import re

activated = False
prefixSuffix = ""
fixCommands = []
language = "de-DE"
dictionary = {}

rec = sr.Recognizer()
with sr.Microphone() as mic:
    print("Microphone calibration running...")
    rec.adjust_for_ambient_noise(mic, duration=1)
    print(f"Set energy_threshold: {rec.energy_threshold}")

_event_callbacks = []
def on_command(callback):
    _event_callbacks.append(callback)
def fire_command(command_text):
    for callback in _event_callbacks:
        callback(command_text)

def speech_to_text(voiceLanguage="de-DE"):
    with sr.Microphone() as mic:
        print("Waiting for speech input...")
        audio = rec.listen(mic)

    try:
        text = rec.recognize_google(audio, language=voiceLanguage)
        return text
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        return ""

def match_command_prefix_suffix(text, prefixSuffix, phrases):
    text = text.lower()
    for phrase in phrases:
        prefix_pattern = r'\b' + re.escape(prefixSuffix) + r'\s+' + re.escape(phrase) + r'\b'
        if re.search(prefix_pattern, text):
            return True        
        pattern_suffix = r'\b' + re.escape(phrase) + r'\s+' + re.escape(prefixSuffix) + r'\b'
        if re.search(pattern_suffix, text):
            return True
    return False

def listener():
    global activated, language, prefixSuffix, fixCommands, dictionary
    while True:
        spoken_text = speech_to_text(language).lower()
        if not spoken_text:
            continue
        # Aktivieren
        if not activated and any(phrase in spoken_text for phrase in dictionary["activate"]):
            activated = True
            fire_command("activate")
        # Deaktivieren
        elif activated and any(phrase in spoken_text for phrase in dictionary["deactivate"]):
            activated = False
            fire_command("deactivate")
        # Andere Kommandos
        elif activated and spoken_text:
            for key, phrases in dictionary.items():
                if key in fixCommands:
                    continue
                elif match_command_prefix_suffix(spoken_text, prefixSuffix, phrases):
                    fire_command(key)
                    break

def initialize_listener(inputLanguage="de-DE", inputPrefixSuffix="jarvis", inputFixCommands=[], inputDictionary={}):
    global language, prefixSuffix, fixCommands, dictionary
    language = inputLanguage
    prefixSuffix = inputPrefixSuffix
    fixCommands = inputFixCommands
    dictionary = inputDictionary

def start_listener():
    jarvis_thread = threading.Thread(target=listener, daemon=True)
    jarvis_thread.start()
