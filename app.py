# === Flask API Backend for CEFR Reading Ease Checker ===
# Save this as app.py

from flask import Flask, request, jsonify
from flask_cors import CORS
import textstat
import re
from collections import Counter

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests for frontend

# --- Load CEFR wordlists (A1–C2) ---
# Replace with actual CEFR word files later
CEFR_LEVELS = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
cefr_words = {level: set() for level in CEFR_LEVELS}

# Example: Load word lists from local .txt files like data/a1.txt, data/b1.txt, etc.
for level in CEFR_LEVELS:
    try:
        with open(f"data/{level.lower()}.txt", "r", encoding="utf-8") as f:
            cefr_words[level] = set(word.strip().lower() for word in f.readlines())
    except FileNotFoundError:
        pass

# Example idioms/phrasal verbs (you can expand this)
phrasal_verbs = ["give up", "look after", "put off", "take off", "come across"]

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    text = data.get("text", "")

    # Basic cleaning
    words = re.findall(r"\\b[a-zA-Z'-]+\\b", text.lower())
    total_words = len(words)
    sentences = re.split(r"[.!?]+", text)
    sentence_lengths = [len(re.findall(r"\\b[a-zA-Z'-]+\\b", s)) for s in sentences if s.strip()]
    avg_sentence_length = round(sum(sentence_lengths) / len(sentence_lengths), 2) if sentence_lengths else 0

    # Count words per CEFR level
    level_counts = {level: 0 for level in CEFR_LEVELS}
    for word in words:
        for level in CEFR_LEVELS:
            if word in cefr_words[level]:
                level_counts[level] += 1
                break

    # Estimate CEFR level based on dominant level of words
    dominant_level = max(level_counts.items(), key=lambda x: x[1])[0] if total_words else "Unknown"

    # Find phrasal verbs/idioms
    found_phrases = [phrase for phrase in phrasal_verbs if phrase in text.lower()]

    # Readability
    flesch_score = round(textstat.flesch_reading_ease(text), 2)
    flesch_grade = round(textstat.flesch_kincaid_grade(text), 2)

    return jsonify({
        "cefr_level": dominant_level,
        "vocab_levels": level_counts,
        "avg_sentence_length": avg_sentence_length,
        "flesch_reading_ease": flesch_score,
        "flesch_grade_level": flesch_grade,
        "difficult_phrases": found_phrases
    })

if __name__ == "__main__":
    app.run(debug=True)
