# filepath: /home/ferdinand/facereconagtion/translate_to_voice.py

import os
import json
from googletrans import Translator
from gtts import gTTS
import speech_recognition as sr

# Global settings with default values
default_settings = {
    "theme": "light",  # light or dark
    "volume": 1.0,  # Volume level (0.0 to 1.0)
    "preferred_languages": {"source": "id-ID", "target": "en"},
    "audio_quality": "high",  # high, medium, low
    "output_format": "mp3",  # mp3 or wav
    "privacy_mode": False,  # If True, logs will be deleted after session
    "microphone_sensitivity": 300,  # Sensitivity level for noise reduction
    "speech_speed": 1.0,  # Speed of TTS (0.5 for slow, 1.0 for normal, 1.5 for fast)
    "multi_language_targets": ["en", "fr"],  # List of target languages for multi-language mode
    "power_saving_mode": False,  # If True, reduces processing intensity
    "tts_accent": "en",  # Accent for TTS (e.g., 'en', 'us', 'uk')
    "speech_pause": 0.5,  # Pause duration between sentences in seconds
    "accessibility_mode": False,  # If True, enables accessibility features
    "audio_input_support": True,  # If True, allows processing audio files as input
    "log_format": "json",  # Format for logs (json or plain text)
}

settings = default_settings.copy()

def save_settings():
    """Save user settings to a JSON file."""
    try:
        with open("settings.json", "w") as f:
            json.dump(settings, f, indent=4)
        print("Pengaturan berhasil disimpan.")
    except Exception as e:
        print(f"Error menyimpan pengaturan: {e}")

def load_settings():
    """Load user settings from a JSON file."""
    global settings
    if os.path.exists("settings.json"):
        try:
            with open("settings.json", "r") as f:
                loaded_settings = json.load(f)
                # Update settings with loaded values, fallback to defaults if missing
                for key, value in default_settings.items():
                    settings[key] = loaded_settings.get(key, value)
        except Exception as e:
            print(f"Error memuat pengaturan: {e}")
            settings = default_settings.copy()
    else:
        settings = default_settings.copy()

def translate_and_speak(text, src_lang, dest_lang, speed=1.0):
    """Translate text and convert it to speech."""
    try:
        translator = Translator()
        translation = translator.translate(text, src=src_lang, dest=dest_lang)
        translated_text = translation.text
        print(f"Translated Text: {translated_text}")

        # Convert translated text to speech
        tts = gTTS(translated_text, lang=dest_lang, slow=(speed < 1.0))
        audio_file = f"output.{settings['output_format']}"
        tts.save(audio_file)

        # Adjust volume and play audio
        os.system(f"ffmpeg -i {audio_file} -filter:a 'volume={settings['volume']}' output_adjusted.{settings['output_format']} -y")
        os.system(f"mpg123 output_adjusted.{settings['output_format']}")
    except Exception as e:
        print(f"Error dalam translate_and_speak: {e}")

def recognize_and_translate(src_lang, dest_lang, speed=1.0, noise_reduction=False, duration="medium"):
    """Recognize speech, translate it, and speak the result."""
    recognizer = sr.Recognizer()

    # Configure noise reduction
    if noise_reduction:
        recognizer.energy_threshold = settings["microphone_sensitivity"]
        recognizer.dynamic_energy_threshold = False
    else:
        recognizer.dynamic_energy_threshold = True

    # Configure recording duration
    duration_mapping = {"short": 5, "medium": 10, "long": 15}
    record_duration = duration_mapping.get(duration, 10)

    with sr.Microphone() as source:
        print(f"Silakan bicara dalam bahasa {src_lang} (durasi: {record_duration} detik)...")
        try:
            audio = recognizer.listen(source, timeout=record_duration)
            text = recognizer.recognize_google(audio, language=src_lang)
            print(f"Anda mengatakan: {text}")

            # Translate and speak the result
            translate_and_speak(text, src_lang, dest_lang, speed)
        except sr.UnknownValueError:
            print("Maaf, suara tidak dikenali.")
        except sr.RequestError as e:
            print(f"Error pada layanan pengenalan suara: {e}")
        except sr.WaitTimeoutError:
            print("Waktu rekaman habis tanpa input suara.")
        except Exception as e:
            print(f"Error dalam recognize_and_translate: {e}")

def process_audio_file(file_path, src_lang, dest_lang):
    """Process an audio file for translation."""
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(file_path) as source:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio, language=src_lang)
            print(f"Teks dari file audio: {text}")
            translate_and_speak(text, src_lang, dest_lang, settings["speech_speed"])
    except Exception as e:
        print(f"Error dalam memproses file audio: {e}")

def privacy_cleanup():
    """Delete logs and temporary files if privacy mode is enabled."""
    if settings.get("privacy_mode", False):
        try:
            if os.path.exists("output.mp3"):
                os.remove("output.mp3")
            if os.path.exists("output_adjusted.mp3"):
                os.remove("output_adjusted.mp3")
            print("Log dan file sementara telah dihapus (Mode Privasi).")
        except Exception as e:
            print(f"Error dalam privacy_cleanup: {e}")

if __name__ == "__main__":
    load_settings()
    print("=== Voice-to-Voice Translator ===")
    print("Pilih mode:")
    print("1. Input teks")
    print("2. Input suara langsung")
    print("3. Mode penerjemahan cepat")
    print("4. Mode belajar bahasa")
    print("5. Mode multi-bahasa")
    print("6. Proses file audio")
    print("7. Pengaturan aplikasi")
    choice = input("Masukkan pilihan (1/2/3/4/5/6/7): ")

    if choice == "1":
        input_text = input("Masukkan teks untuk diterjemahkan: ")
        source_language = input("Masukkan bahasa sumber (contoh: 'id' untuk Indonesia): ")
        target_language = input("Masukkan bahasa target (contoh: 'en' untuk Inggris): ")
        translate_and_speak(input_text, source_language, target_language, speed=settings["speech_speed"])

    elif choice == "2":
        source_language = input("Masukkan bahasa sumber (contoh: 'id-ID' untuk Indonesia): ")
        target_language = input("Masukkan bahasa target (contoh: 'en' untuk Inggris): ")
        recognize_and_translate(source_language, target_language, speed=settings["speech_speed"], noise_reduction=True, duration="medium")

    elif choice == "3":
        print("=== Mode Penerjemahan Cepat ===")
        recognize_and_translate(settings["preferred_languages"]["source"], settings["preferred_languages"]["target"], speed=settings["speech_speed"], noise_reduction=True, duration="short")

    elif choice == "4":
        print("=== Mode Belajar Bahasa ===")
        src_lang = input("Masukkan bahasa yang ingin Anda pelajari (contoh: 'en'): ")
        dest_lang = settings["preferred_languages"]["source"]
        recognize_and_translate(src_lang, dest_lang, speed=settings["speech_speed"], noise_reduction=True, duration="medium")

    elif choice == "5":
        print("=== Mode Multi-Bahasa ===")
        src_lang = settings["preferred_languages"]["source"]
        targets = settings["multi_language_targets"]
        for target_lang in targets:
            recognize_and_translate(src_lang, target_lang, speed=settings["speech_speed"], noise_reduction=True, duration="medium")

    elif choice == "6":
        if settings["audio_input_support"]:
            file_path = input("Masukkan path file audio: ")
            source_language = input("Masukkan bahasa sumber (contoh: 'id-ID' untuk Indonesia): ")
            target_language = input("Masukkan bahasa target (contoh: 'en' untuk Inggris): ")
            process_audio_file(file_path, source_language, target_language)
        else:
            print("Dukungan file audio tidak diaktifkan.")

    elif choice == "7":
        print("=== Pengaturan Aplikasi ===")
        print("1. Ubah tema (light/dark)")
        print("2. Atur volume (0.0 - 1.0)")
        print("3. Atur preferensi bahasa")
        print("4. Atur kualitas audio (high/medium/low)")
        print("5. Atur format output audio (mp3/wav)")
        print("6. Aktifkan/Nonaktifkan mode privasi")
        print("7. Atur aksen TTS")
        print("8. Atur jeda bicara")
        print("9. Aktifkan/Nonaktifkan mode aksesibilitas")
        print("10. Aktifkan/Nonaktifkan dukungan file audio")
        setting_choice = input("Masukkan pilihan (1-10): ")

        if setting_choice == "1":
            settings["theme"] = input("Masukkan tema baru (light/dark): ")
        elif setting_choice == "2":
            settings["volume"] = float(input("Masukkan level volume (0.0 - 1.0): "))
        elif setting_choice == "3":
            settings["preferred_languages"]["source"] = input("Masukkan bahasa sumber default (contoh: 'id-ID'): ")
            settings["preferred_languages"]["target"] = input("Masukkan bahasa target default (contoh: 'en'): ")
        elif setting_choice == "4":
            settings["audio_quality"] = input("Masukkan kualitas audio (high/medium/low): ")
        elif setting_choice == "5":
            settings["output_format"] = input("Masukkan format output audio (mp3/wav): ")
        elif setting_choice == "6":
            settings["privacy_mode"] = not settings["privacy_mode"]
            print(f"Mode privasi: {'Aktif' if settings['privacy_mode'] else 'Nonaktif'}")
        elif setting_choice == "7":
            settings["tts_accent"] = input("Masukkan aksen TTS (contoh: 'en', 'us', 'uk'): ")
        elif setting_choice == "8":
            settings["speech_pause"] = float(input("Masukkan jeda bicara dalam detik (contoh: 0.5): "))
        elif setting_choice == "9":
            settings["accessibility_mode"] = not settings["accessibility_mode"]
            print(f"Mode aksesibilitas: {'Aktif' if settings['accessibility_mode'] else 'Nonaktif'}")
        elif setting_choice == "10":
            settings["audio_input_support"] = not settings["audio_input_support"]
            print(f"Dukungan file audio: {'Aktif' if settings['audio_input_support'] else 'Nonaktif'}")

        save_settings()

    else:
        print("Pilihan tidak valid. Program dihentikan.")

    privacy_cleanup()