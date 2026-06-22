import os
import datetime
import pandas as pd

# SERVICES
SERVICES = {
    "Happy": "Keep smiling! Share your happiness!",
    "Sad": "Stay strong! Listen to calm music.",
    "Angry": "Take deep breaths! Relax yourself.",
    "Fearful": "You are safe. Stay calm and breathe.",
    "Excited": "Great energy! Plan something big!",
    "Neutral": "Stay balanced! Keep going!"
}

# STOP_WORDS
STOP_WORDS = {
    "i", "am", "is", "are", "was", "were",
    "the", "a", "an",
    "to", "of", "for", "in", "on", "at",
    "with", "and", "or", "but",
    "that", "this", "it", "be", "been",
    "being", "my", "me", "we", "our",
    "you", "your", "they", "their",
    "he", "she", "him", "her",
    "have", "has", "had",
    "do", "does", "did",
    "so", "just", "very", "can"
}

# clean raw text from input
def clean_text(text):
    text = text.lower().strip()

    for ch in ["'", ".", ",", "!", "?", ":", ";", "“", "”", '"']:
        text = text.replace(ch, " ")

    words = text.split()
    cleaned = []

    for word in words:
        word = word.strip(":-;()[]{}\"")
        if word not in STOP_WORDS and word != "":
            cleaned.append(word)

    return cleaned

def check_phrase(text, PHRASES):
    for phrase, emotion in PHRASES.items():
        if phrase in text:
            return emotion
    return None

def detect_emotion(text, kmap):

    PHRASES = {
        "not feeling well": "Sad",
        "feeling down": "Sad",
        "very sad": "Sad",
        "so happy": "Happy",
        "very happy": "Happy",
        "really excited": "Excited",
        "so scared": "Fearful",
        "very angry": "Angry",
        "feeling great": "Happy",
        "now i am calm": "Neutral",
        "now i am fine": "Neutral"
    }

    STRONG_WORDS = {
        "Happy": ["happy", "amazing", "best", "great", "dream", "won", "success", "finally"],
        "Sad": ["sad", "tired", "depressed", "hopeless", "down", "bad", "miss"],
        "Fearful": ["scared", "afraid", "worried", "nervous"],
        "Angry": ["angry", "mad", "hate", "frustrated"],
        "Excited": ["excited", "thrilled", "wow"]
    }

    NEGATIONS = {"not", "no", "never", "dont", "cannot", "cant"}

    words = clean_text(text)
    text_joined = " ".join(words)

    # 1. phrase check
    result = check_phrase(text_joined, PHRASES)
    if result:
        return result

    # 2. scoring
    scores = {
        "Happy": 0,
        "Sad": 0,
        "Angry": 0,
        "Fearful": 0,
        "Excited": 0,
        "Neutral": 0
    }

    negate = 0

    for word in words:

        if word in NEGATIONS:
            negate = 2
            continue

        matched = False

        for emotion, word_list in STRONG_WORDS.items():
            if word in word_list:
                matched = True

                if negate:
                    if emotion == "Happy":
                        scores["Sad"] += 2
                    elif emotion == "Sad":
                        scores["Happy"] += 2
                    elif emotion == "Angry":
                        scores["Sad"] += 2
                    elif emotion == "Fearful":
                        scores["Neutral"] += 1
                    else:
                        scores[emotion] += 1
                else:
                    scores[emotion] += 2
                break

        if not matched and word in kmap:
            for emotion in kmap[word]:
                scores[emotion] += 0.5

        if negate:
            negate -= 1

    # 3. final decision
    total = sum(scores.values())

    if total == 0:
        return "Neutral"

    emotion = max(scores, key=scores.get)

    if scores[emotion] / total < 0.35:
        return "Neutral"

    return emotion

def get_time():
    return str(datetime.datetime.now())

# USER CLASS
class User:
    def __init__(self, username, age):
        self.username = username
        self.age = age
        self.folder = "users"
        self.file = os.path.join(self.folder, f"{username}.txt")

    def create_file(self):
        try:
            if not os.path.exists(self.folder):
                os.makedirs(self.folder)

            if not os.path.exists(self.file):
                with open(self.file, "w") as f:
                    f.write(f"User: {self.username}\nAge: {self.age}\n\n")

        except Exception as e:
            print("File error:", e)

    def save_emotion(self, emotion, text):
        try:
            with open(self.file, "a") as f:
                f.write(f"{get_time()} | {text} | {emotion}\n")
        except Exception as e:
            print("Save error:", e)

    def load_history(self):
        try:
            with open(self.file, "r") as f:
                lines = f.readlines()

            # Log entries start from index 3 onward
            log_lines = [line for line in lines[3:] if line.strip() != ""]

            if not log_lines:
                return "No history found yet."

            header = f"User: {self.username}\nAge: {self.age}\n\n"
            return header + "".join(log_lines)

        except:
            return "No history found."

    def emotion_warning(self):
        try:
            with open(self.file, "r") as f:
                lines = f.readlines()

            # Log lines start at index 3; format: timestamp | text | emotion
            log_lines = [line.strip() for line in lines[3:] if line.strip() != ""]

            if not log_lines:
                return "No emotional data yet."

            sad_count = 0
            angry_count = 0

            for line in log_lines:
                parts = line.split("|")
                if len(parts) == 3:
                    detected_emotion = parts[2].strip().lower()
                    if detected_emotion == "sad":
                        sad_count += 1
                    elif detected_emotion == "angry":
                        angry_count += 1

            if sad_count >= 5:
                return "You are frequently sad. Consider talking to someone or taking a break."

            if angry_count >= 5:
                return "You are frequently angry. Try relaxation techniques."

            return "Not enough emotional patterns yet to analyze."

        except:
            return "No data for analysis."

# LOGIN SYSTEM
def login_system():
    print("\n===== LOGIN SYSTEM =====")

    username = input("Enter username: ").strip()

    while True:
        try:
            age = int(input("Enter age: "))
            if age <= 0:
                print("Please enter a valid age.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter a number for age.")

    user = User(username, age)
    user.create_file()

    print("\nWelcome", username)

    age_group = (
        "Teen" if age < 18 else
        "Adult" if age < 40 else
        "Senior"
    )

    print("Age Group:", age_group)

    return user

# MAIN SYSTEM
def main():
    if not os.path.exists("processed_emotions.csv"):
        print("Error: 'processed_emotions.csv' not found.")
        print("Please make sure the file is in the same folder as this script.")
        return

    user = login_system()

    df = pd.read_csv("processed_emotions.csv")

    keyword_map = (
        df.groupby("keyword")["emotion"]
          .apply(list)
          .to_dict()
    )

    while True:
        print("\n===== MENU =====")
        print("1. Enter Text")
        print("2. View History")
        print("3. Emotion Warning")
        print("4. Exit")

        choice = input("Choose option: ").strip()

        if choice == "1":
            text = input("\nEnter text: ")

            emotion = detect_emotion(text, keyword_map)

            print("\nDetected Emotion:", emotion)
            print("Service:", SERVICES.get(emotion, "Stay balanced"))

            user.save_emotion(emotion, text)

        elif choice == "2":
            print(user.load_history())

        elif choice == "3":
            print(user.emotion_warning())

        elif choice == "4":
            print("Goodbye")
            break

        else:
            print("Invalid option!")

main()