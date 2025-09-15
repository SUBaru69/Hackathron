import requests
from langdetect import detect, DetectorFactory

# Ensure consistent detection
DetectorFactory.seed = 0

# Hugging Face API setup
API_TOKEN = "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"
headers = {"Authorization": f"Bearer {API_TOKEN}"}

# Language codes and names
LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "fr": "French",
    "es": "Spanish",
    "kn": "Kannada",
    "de": "German",
    "it": "Italian",
    "ru": "Russian",
    "ja": "Japanese",
    "zh": "Chinese",
    "ar": "Arabic",
    "pt": "Portuguese",
    "nl": "Dutch",
    "ta": "Tamil"
}

MODELS = {
    # Existing pairs
    ("en", "hi"): "Helsinki-NLP/opus-mt-en-hi",
    ("hi", "en"): "Helsinki-NLP/opus-mt-hi-en",
    ("en", "fr"): "Helsinki-NLP/opus-mt-en-fr",
    ("fr", "en"): "Helsinki-NLP/opus-mt-fr-en",
    ("en", "es"): "Helsinki-NLP/opus-mt-en-es",
    ("es", "en"): "Helsinki-NLP/opus-mt-es-en",
    ("en", "kn"): "Helsinki-NLP/opus-mt-en-kn",
    ("kn", "en"): "Helsinki-NLP/opus-mt-kn-en",
    
    # New languages (English ↔ others)
    ("en", "de"): "Helsinki-NLP/opus-mt-en-de",
    ("de", "en"): "Helsinki-NLP/opus-mt-de-en",
    ("en", "it"): "Helsinki-NLP/opus-mt-en-it",
    ("it", "en"): "Helsinki-NLP/opus-mt-it-en",
    ("en", "ru"): "Helsinki-NLP/opus-mt-en-ru",
    ("ru", "en"): "Helsinki-NLP/opus-mt-ru-en",
    ("en", "ja"): "Helsinki-NLP/opus-mt-en-ja",
    ("ja", "en"): "Helsinki-NLP/opus-mt-ja-en",
    ("en", "zh"): "Helsinki-NLP/opus-mt-en-zh",
    ("zh", "en"): "Helsinki-NLP/opus-mt-zh-en",
    ("en", "ar"): "Helsinki-NLP/opus-mt-en-ar",
    ("ar", "en"): "Helsinki-NLP/opus-mt-ar-en",
    ("en", "pt"): "Helsinki-NLP/opus-mt-en-pt",
    ("pt", "en"): "Helsinki-NLP/opus-mt-pt-en",
    ("en", "nl"): "Helsinki-NLP/opus-mt-en-nl",
    ("nl", "en"): "Helsinki-NLP/opus-mt-nl-en",
    ("en", "ta"): "Helsinki-NLP/opus-mt-en-ta",
    ("ta", "en"): "Helsinki-NLP/opus-mt-ta-en",
}


SUPPORTED_LANGUAGES = set(LANGUAGE_NAMES.keys())

# Function to check if API token is valid
def check_api_token():
    test_model = "Helsinki-NLP/opus-mt-en-fr"
    try:
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{test_model}",
            headers=headers,
            json={"inputs": "Hello"},
            timeout=10
        )
        if response.status_code == 401:
            print("❌ Invalid Hugging Face API token. Please check your API_TOKEN.")
            return False
        return True
    except requests.exceptions.RequestException as e:
        print(f"Network error while checking API token: {e}")
        return False

# Translate function
def translate(text, src_lang, tgt_lang):
    model_id = MODELS.get((src_lang, tgt_lang))
    if not model_id:
        return f"Translation model not available for {LANGUAGE_NAMES.get(src_lang, src_lang)} → {LANGUAGE_NAMES.get(tgt_lang, tgt_lang)}"
    url = f"https://api-inference.huggingface.co/models/{model_id}"
    payload = {"inputs": text}
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        result = response.json()
        if "error" in result:
            return "Error: " + result["error"]
        return result[0]['translation_text']
    except requests.exceptions.RequestException as e:
        return f"Network error: {e}"
    except ValueError as e:
        return f"Error decoding response: {e}\nRaw response: {response.text}"

# Language detection
def detect_language(text):
    try:
        return detect(text)
    except:
        return "unknown"

# Get supported targets
def get_supported_targets(src_lang):
    return [tgt for (s, tgt) in MODELS.keys() if s == src_lang]

# Show target languages
def show_target_languages(targets):
    print("Available languages to translate to:")
    for idx, lang in enumerate(targets, 1):
        print(f"{idx}. {LANGUAGE_NAMES.get(lang, lang)}")

# Get multiple language choices from user
def get_user_target_choices(targets):
    print("Enter the numbers of the target languages separated by commas (e.g., 1,3): ")
    choice = input("Your choice: ").strip()
    selected = set()
    entries = choice.split(",")
    for entry in entries:
        entry = entry.strip()
        if entry.isdigit():
            idx = int(entry)
            if 1 <= idx <= len(targets):
                selected.add(targets[idx - 1])
    return list(selected)

# Let user choose correct language if detection fails
def choose_language():
    print("Please select the correct language from the list:")
    for idx, (code, name) in enumerate(LANGUAGE_NAMES.items(), 1):
        print(f"{idx}. {name} ({code})")
    choice = input("Enter the number of the language: ").strip()
    if choice.isdigit():
        index = int(choice)
        if 1 <= index <= len(LANGUAGE_NAMES):
            lang_code = list(LANGUAGE_NAMES.keys())[index - 1]
            return lang_code
    print("Invalid choice.")
    return None

# Main loop
if __name__ == "__main__":
    # Check API token before starting
    if not check_api_token():
        exit()

    print("🌍 Multi-language Translator – Translate into multiple languages!")
    print("Type 'exit' or 'quit' to stop.")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        src_lang = detect_language(user_input)

        if src_lang not in SUPPORTED_LANGUAGES:
            print(f"Detected language '{src_lang}' is unsupported or unrecognized.")
            src_lang = choose_language()
            if not src_lang:
                print("Could not select language. Please try again.")
                continue

        print(f"Detected language: {LANGUAGE_NAMES[src_lang]}")

        targets = get_supported_targets(src_lang)
        if not targets:
            print(f"No available translations from {LANGUAGE_NAMES[src_lang]}.")
            continue

        show_target_languages(targets)

        selected_languages = get_user_target_choices(targets)
        if not selected_languages:
            print("No valid languages selected. Please try again.")
            continue

        print("Translations:")
        for tgt_lang in selected_languages:
            translated = translate(user_input, src_lang, tgt_lang)
            print(f"{LANGUAGE_NAMES[tgt_lang]}: {translated}")
        print()  # blank line for readability

