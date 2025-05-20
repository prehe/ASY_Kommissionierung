from LanguageAssistant.SpeechToText import initialize_listener, start_listener, on_command
from LanguageAssistant.TextToSpeech import text_to_speech

def handle_command(command):
    if command == "activate":
        text_to_speech("Jarvis, dein persönlicher Sprachassistent ist bereit")
        print("Aktiviert...")
    elif command == "deactivate":
        text_to_speech("Jarvis wird deaktiviert")
        print("Deaktiviert...")
    elif command:
        print(command)

dictionary = {
    "activate": ["hey jarvis", "start jarvis"],
    "deactivate": ["jarvis stop", "stop jarvis"],
    "next": ["weiter"],
    "back": ["zurück"],
    "exit": ["beenden"],
}

on_command(handle_command)
initialize_listener(inputLanguage="de-DE", inputPrefixSuffix="jarvis", inputFixCommands=["activate", "deactivate"], inputDictionary=dictionary)
start_listener()

try:
    while True:
        pass
except KeyboardInterrupt:
    print("Program terminated.")