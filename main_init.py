def initialize_voice_assistant():
    global state
    import sys
    sys.path.append("../LanguageAssistant")
    from LanguageAssistant.LanguageHandler import on_command, initialize_listener, start_listener

    def handle_voice_command(command):
        global state
        if command == "next":
            print("Next command recognized")
            state = "run_job"
        elif command == "back":
            print("Back command recognized")
            state = "initial"
        elif command == "exit":
            print("Programm wird beendet.")
            exit(0)
        elif command == "save_current_job":
            print("Save current job command recognized")
            state = "save_current_job"
        elif command == "cancel_job":
            print("Cancel job command recognized")
            state = "cancel_job"
        elif command == "scan_job":
            print("Scan job command recognized")
            state = "scan_job"
        elif command == "finish_job":
            print("Finish job command recognized")
            state = "finish_job"

    on_command(handle_voice_command)
    initialize_listener(
        inputLanguage="de-DE",
        inputPrefixSuffix="jarvis",
        inputFixCommands=["activate", "deactivate"],
        inputDictionary={
            "activate": ["hey jarvis", "start jarvis"],
            "deactivate": ["jarvis stop", "stop jarvis"],
            "next": ["weiter"],
            "back": ["zurück"],
            "exit": ["beenden"],
            "save_current_job": ["speichern"],
            "cancel_job": ["abbrechen"],
            "scan_job": ["scan job"],
            "finish_job": ["fertig"]
        }
    )
    start_listener()
    


def initialize_gui():
    import sys
    import tkinter as tk
    sys.path.append("../HMI")
    from HMI.HMI_Base import App

    root = tk.Tk()
    app = App(root)
    root.mainloop()