import speech_recognition as sr
import datetime
import wikipedia
import webbrowser
from gtts import gTTS
import os
import random

recognizer = sr.Recognizer()
recognizer.pause_threshold = 1
recognizer.energy_threshold = 300


def speak(text):
    print("Assistant:", text)
    tts = gTTS(text=text, lang="en")
    tts.save("voice.mp3")
    os.system("start voice.mp3")


# ---------------- SYSTEM APPS ----------------

system_apps = {
    "notepad": "notepad",
    "calculator": "calc",
    "cmd": "start cmd",
    "paint": "mspaint",
    "task manager": "taskmgr",
    "control panel": "control",
    "file explorer": "explorer",
    "settings": "start ms-settings:",
}


# ---------------- WEBSITES ----------------

websites = {

    # search
    "google": "https://google.com",
    "youtube": "https://youtube.com",
    "wikipedia": "https://wikipedia.org",

    # social
    "facebook": "https://facebook.com",
    "instagram": "https://instagram.com",
    "twitter": "https://twitter.com",
    "reddit": "https://reddit.com",

    # coding
    "github": "https://github.com",
    "stackoverflow": "https://stackoverflow.com",

    # email
    "gmail": "https://mail.google.com",

    # shopping
    "amazon": "https://amazon.com",
    "flipkart": "https://flipkart.com",

    # entertainment
    "netflix": "https://netflix.com",
    "spotify": "https://spotify.com",

    # AI
    "chatgpt": "https://chat.openai.com",
    "gemini": "https://gemini.google.com",
    "claude": "https://claude.ai"
}


def process_command(command):

    command = command.lower()

    # greetings
    if "hello" in command or "hi" in command:
        speak(random.choice([
            "Hello",
            "Hi, how can I help you?",
            "Nice to hear from you"
        ]))

    # time
    elif "time" in command:
        now = datetime.datetime.now()
        speak("The time is " + now.strftime("%H:%M"))

    # date
    elif "date" in command:
        today = datetime.date.today()
        speak("Today's date is " + str(today))

    # wikipedia
    elif "who is" in command:
        person = command.replace("who is","").strip()

        try:
            info = wikipedia.summary(person,2)
            speak(info)

        except:
            speak("I could not find information")

    # open websites
    elif "open" in command:

        for site in websites:
            if site in command:
                speak("Opening " + site)
                webbrowser.open(websites[site])
                return

        for app in system_apps:
            if app in command:
                speak("Opening " + app)
                os.system(system_apps[app])
                return

        speak("I cannot find that")

    # youtube play
    elif "play" in command:

        song = command.replace("play","").strip()

        speak("Playing " + song)

        webbrowser.open(
            "https://www.youtube.com/results?search_query=" + song
        )

    # google search
    elif "search" in command:

        query = command.replace("search","").strip()

        speak("Searching for " + query)

        webbrowser.open(
            "https://google.com/search?q=" + query
        )

    # shutdown
    elif "shutdown" in command:
        speak("Shutting down computer")
        os.system("shutdown /s /t 5")

    # restart
    elif "restart" in command:
        speak("Restarting computer")
        os.system("shutdown /r /t 5")

    # stop assistant
    elif "stop" in command or "exit" in command:
        speak("Goodbye")
        exit()

    else:
        speak("I did not understand")


def listen():

    with sr.Microphone() as source:

        print("Listening...")

        recognizer.adjust_for_ambient_noise(source, duration=1)

        audio = recognizer.listen(source, timeout=5, phrase_time_limit=6)

    try:

        command = recognizer.recognize_google(audio)

        print("You said:", command)

        return command.lower()

    except:
        return ""


def run_assistant():

    speak("Assistant started")

    while True:

        command = listen()

        if command == "":
            continue

        process_command(command)


if __name__ == "__main__":
    run_assistant()