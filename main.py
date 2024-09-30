from flet import *
import cv2
import speech_recognition as sr
import pyttsx3
import threading
import time
import imaplib
import email

# Initialize speech recognition and text-to-speech engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# Set voice to English
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen_command():
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        command = ""
        try:
            command = recognizer.recognize_google(audio)
            print(f"You said: {command}")
        except sr.UnknownValueError:
            speak("I didn't understand that.")
        except sr.RequestError:
            speak("Check your network connection.")
        return command.lower()

def open_camera():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        speak("Could not open camera.")
        return None
    else:
        speak("Camera opened successfully.")
        return cap

def capture_image(cap):
    ret, frame = cap.read()
    if ret:
        image_filename = f"captured_image.png"
        cv2.imwrite(image_filename, frame)
        speak(f"Picture taken and saved as {image_filename}.")
        return frame
    return None

def check_email(email_user, email_pass):
    try:
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(email_user, email_pass)
        mail.select('inbox')
        result, data = mail.search(None, 'UNSEEN')
        if data[0]:
            mail_ids = data[0].split()
            for mail_id in mail_ids:
                result, msg_data = mail.fetch(mail_id, '(RFC822)')
                msg = email.message_from_bytes(msg_data[0][1])
                subject = msg['subject']
                from_ = msg['from']
                speak(f"You have a new email from {from_}: {subject}.")
        mail.logout()
    except Exception as e:
        print(f"Error checking email: {e}")

def notification_thread(email_user, email_pass):
    while True:
        check_email(email_user, email_pass)
        time.sleep(60)

def start_notifications(email_user, email_pass):
    threading.Thread(target=notification_thread, args=(email_user, email_pass), daemon=True).start()

def start_listening_for_input(input_type):
    if input_type == "email":
        speak("Please say your email address.")
        email_user = listen_command()
        return email_user
    elif input_type == "password":
        speak("Please say your email password.")
        email_pass = listen_command()
        return email_pass
    return ""

def main(page: Page):
    page.title = "Voice Assistant"

    email_user = ""
    email_pass = ""

    def on_start(e):
        nonlocal email_user, email_pass
        email_user = start_listening_for_input("email")
        email_pass = start_listening_for_input("password")
        
        if email_user and email_pass:
            start_notifications(email_user, email_pass)  # Start the notification thread
            page.add(Text("Notifications started successfully."))

    def on_open_camera(e):
        cap = open_camera()
        if cap:
            capture_image(cap)
            cap.release()

    # Create buttons for various functionalities
    page.add(
        Column(
            controls=[
                ElevatedButton("Start Listening for Email", on_click=on_start),
                ElevatedButton("Open Camera", on_click=on_open_camera),
                Text("مرحبًا بك في مساعد الصوت!")  # Welcome text in Arabic
            ]
        )
    )

if __name__ == "__main__":
    app(target=main)
