from main_init import initialize_voice_assistant, initialize_gui

state = "initial"
state_changed = True  # Start mit True, damit der State beim ersten Mal ausgegeben wird
active_job = [123213, ["step1", "step2", "step3"]]
current_step = 0


def main():
    global state, state_changed, active_job, current_step

    # initialize_gui()
    # initialize_voice_assistant()

    # Main loop to handle state transitions
    while True:
        if state == "initial":
            if state_changed:
                print("Initial state")
                # update GUI with message and options
                message = "Pioneering HSBI - AI powered by Jarvis"
                options = ["start_new_job", "load_job"]
                # Hier könntest du die GUI aktualisieren
                state_changed = False

            # check for user input - replace with actual input
            gesture_control = [True, "start_new_job"]
            voice_control = [False, ""]
            hmi_control = [False, ""]

            # Eingabe auswerten
            if gesture_control[0]:
                user_input = gesture_control[1]
            elif voice_control[0]:
                user_input = voice_control[1]
            elif hmi_control[0]:
                user_input = hmi_control[1]
            else:
                user_input = None

            if user_input == "start_new_job":
                state = "scan_job"
                state_changed = True
            elif user_input == "load_job":
                # Hier könntest du einen anderen State setzen
                pass

        elif state == "scan_job":
            if state_changed:
                message = "QR-Code scannen für Auftrags-ID"
                options = ["", "cancel"]
                print("Scan job state")
                # update GUI etc.
                state_changed = False
            # Perform actions for scan job state
            job_id = 123213  # Simulate job ID
            print(f"Job ID: {job_id} detected")
            state = "run_job"
            state_changed = True

        elif state == "run_job":
            if state_changed:
                print("Run job state")
                # load job data
                active_job = [123213, ["step1", "step2", "step3"]]  # Simulate loaded job
                current_step = 0

                message = "Auftrag: {active_job[0]}: {active_job[1][current_step]}, Schritt: {current_step+1} von {len(active_job[1])}"
                options = ["next", "back", "finish", "save_current_job", "cancel_job"]
                print(message)
                print(options)
                
                # Hier könntest du die GUI aktualisieren
                state_changed = False
            # Perform actions for run job state
            
            # Simulate job step processing

            
            if current_step < len(active_job[1]):
                # Simulate job step processing
                print(f"Processing step: {active_job[1][current_step]}")
                current_step += 1
            else:
                print("All steps completed")
                state = "finish_job"
                state_changed = True

        elif state == "finish_job":
            if state_changed:
                print("Finish job state")
                state_changed = False
            # Perform finish job actions
            state = "initial"
            state_changed = True

        elif state == "cancel_job":
            if state_changed:
                print("Cancel job state")
                state_changed = False
            # Handle cancel job state
            message = "Auftrag abbrechen?"
            options = ["yes", "no"]
            print(message)
            print(options)
            
            if gesture_control[0]:
                user_input = gesture_control[1]
            state = "cancel_job_confirm" if user_input == "yes" else "run_job"
        elif state == "cancel_job_confirm":
            if state_changed:
                print("Cancel job confirm state")
                state_changed = False
            # Handle cancel job confirm state
            if gesture_control[0]:
                user_input = gesture_control[1]
            state = "initial" if user_input == "yes" else "run_job"
            state_changed = True

        elif state == "save_current_job":
            if state_changed:
                print("Save current job state")
                state_changed = False
            # Handle save current job state
            state = "initial"
            state_changed = True

if __name__ == "__main__":
    main()