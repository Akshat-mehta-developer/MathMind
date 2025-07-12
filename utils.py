import json
import os
from datetime import datetime

USER_DATA_FILE = "users.json"

# Load user data
def load_users():
    if not os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "w") as f:
            json.dump({}, f)
    with open(USER_DATA_FILE, "r") as f:
        return json.load(f)

# Save user data
def save_users(data):
    with open(USER_DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Update cumulative score for a user
def update_score(username, score, data):
    if username in data:
        data[username]["score"] += score
        save_users(data)

# Get topics by grade
def get_topics_by_grade(grade):
    if grade <= 2:
        return ["Addition", "Subtraction", "Counting", "Shapes"]
    elif grade <= 5:
        return ["Multiplication", "Division", "Fractions", "Measurements"]
    elif grade <= 8:
        return ["Algebra", "Percentages", "Geometry", "Decimals"]
    elif grade <= 10:
        return ["Linear Equations", "Mensuration", "Statistics", "Polynomials"]
    elif grade == 11:
        return ["Sets", "Functions", "Quadratic Equations", "Sequence and Series"]
    elif grade == 12:
        return ["Trigonometry", "Integration", "Differentiation", "Probability"]
    else:
        return ["General Math"]

# Save quiz attempt in user history


def log_quiz_result(username, grade, topic, level, score, user_answers):
    data = load_users()
    if username not in data:
        data[username] = {"score": 0, "grade": 1, "history": []}
    if "history" not in data[username]:
        data[username]["history"] = []

    data[username]["history"].append({
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "grade": grade,
        "topic": topic,
        "level": level,
        "score": score,
        "user_answers": user_answers
    })

    save_users(data)