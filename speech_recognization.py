import pyttsx3
from googletrans import Translator, LANGUAGES
import speech_recognition as sr

# Initialize translator and TTS engine
translator = Translator()
tts_engine = pyttsx3.init()

def speak(text):
    tts_engine.say(text)
    tts_engine.runAndWait()

def translate_text(text, target_lang, src_lang='auto'):
    try:
        if src_lang == 'auto':
            detected = translator.detect(text)
            src_lang = detected.lang
        
        result = translator.translate(text, src=src_lang, dest=target_lang)
        src_lang_name = LANGUAGES.get(result.src, 'unknown').capitalize()
        target_lang_name = LANGUAGES.get(target_lang, 'unknown').capitalize()
        output = f"[{src_lang_name}] to [{target_lang_name}]: {result.text}"
        print(f"Translated: {output}")
        speak(output)
        return output
    except Exception as e:
        error_msg = f"Translation failed: {str(e)}"
        print(error_msg)
        speak(error_msg)
        return error_msg

def listen_speech(language='en-US'):
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        print(f"Listening... Please speak clearly in {language}.")
        speak(f"Listening. Please speak clearly in {language}.")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio, language=language)
        print(f"You said: {text}")
        speak(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        msg = "Sorry, I could not understand the audio."
        print(msg)
        speak(msg)
        return None
    except sr.RequestError as e:
        msg = f"Could not request results from speech service; {e}"
        print(msg)
        speak(msg)
        return None

def confirm_recognized_text(text):
    print(f"\nYou said: {text}")
    speak(f"You said: {text}. If you want to edit, please type it now, or press Enter to keep as is.")
    edited_text = input("Edit text (press Enter to keep as is): ").strip()
    if edited_text:
        speak(f"Text updated to: {edited_text}")
        return edited_text
    speak("Text kept as is.")
    return text

if __name__ == "__main__":
    welcome_msg = "Welcome to Free Translation Bot with Speech Recognition and narration!"
    print(welcome_msg)
    speak(welcome_msg)
    print("Supported languages include Japanese (ja).")
    speak("Supported languages include Japanese. To translate, enter language code like hi, en, kn, ja.")
    print("All supported languages:", ', '.join([f"{code}({name})" for code, name in LANGUAGES.items()]))

    while True:
        mode = input("\nEnter 's' for speech input, 't' for text input, or 'quit' to exit: ").strip().lower()
        if mode == "quit":
            goodbye_msg = "Goodbye!"
            print(goodbye_msg)
            speak(goodbye_msg)
            break
        
        if mode == 's':
            lang_spoken = input("Enter spoken language code for recognition (e.g., hi-IN for Hindi, ja-JP for Japanese): ").strip()
            text = listen_speech(language=lang_spoken)
            if not text:
                continue
            text = confirm_recognized_text(text)
        elif mode == 't':
            text = input("Enter text to translate: ").strip()
            speak(f"You entered: {text}")
        else:
            err_msg = "Invalid input mode. Please enter 's', 't', or 'quit'."
            print(err_msg)
            speak(err_msg)
            continue

        target_lang = input("Enter target language code (e.g., hi, en, kn, ja for Japanese): ").strip()
        translated = translate_text(text, target_lang, src_lang='auto')
