# ai_question_generator.py

import google.generativeai as genai
from google.api_core.exceptions import GoogleAPIError
import random
import json
import re
import os

# Set your Gemini API key
# genai.configure(api_key="AIzaSyB9G5a3bS08iWv1Dnor-ySgknXvovS9tGo")
genai.configure(api_key="AIzaSyBTnIxeeI2IbOdlxbG1trcbZOMvxQ946cA")

# Use a valid model from your list
# MODEL = genai.GenerativeModel("models/gemini-1.5-flash")
MODEL = genai.GenerativeModel("models/gemini-2.5-flash-lite")


# List of Gemini models to try in order
# GEMINI_MODELS = [
#     "models/gemini-1.5-flash",
#     "models/gemini-1.5-pro",
#     "models/gemini-2.5-pro-preview-06-05",
#     "models/gemini-2.5-pro-preview-03-25",
#     "models/gemini-2.5-flash",
#     "models/gemini-2.5-flash-preview-05-20",
#     "models/gemini-2.0-flash",
#     "models/gemini-1.5-flash-002",
#     "models/gemini-1.5-flash-latest",
#     "models/gemini-2.5-pro"
# ]
GEMINI_MODELS = ['models/gemini-1.0-pro-vision-latest',
'models/gemini-pro-vision',
'models/gemini-1.5-pro-latest',
'models/gemini-1.5-pro-002',
'models/gemini-1.5-pro',
'models/gemini-1.5-flash-latest',
'models/gemini-1.5-flash',
'models/gemini-1.5-flash-002',
'models/gemini-1.5-flash-8b',
'models/gemini-1.5-flash-8b-001',
'models/gemini-1.5-flash-8b-latest',
'models/gemini-2.5-pro-preview-03-25',
'models/gemini-2.5-flash-preview-04-17',
'models/gemini-2.5-flash-preview-05-20',
'models/gemini-2.5-flash',
'models/gemini-2.5-flash-preview-04-17-thinking',
'models/gemini-2.5-flash-lite-preview-06-17',
'models/gemini-2.5-pro-preview-05-06',
'models/gemini-2.5-pro-preview-06-05',
'models/gemini-2.5-pro',
'models/gemini-2.0-flash-exp',
'models/gemini-2.0-flash',
'models/gemini-2.0-flash-001',
'models/gemini-2.0-flash-exp-image-generation',
'models/gemini-2.0-flash-lite-001',
'models/gemini-2.0-flash-lite',
'models/gemini-2.0-flash-preview-image-generation',
'models/gemini-2.0-flash-lite-preview-02-05',
'models/gemini-2.0-flash-lite-preview',
'models/gemini-2.0-pro-exp',
'models/gemini-2.0-pro-exp-02-05',
'models/gemini-exp-1206',
'models/gemini-2.0-flash-thinking-exp-01-21',
'models/gemini-2.0-flash-thinking-exp',
'models/gemini-2.0-flash-thinking-exp-1219',
'models/gemini-2.5-flash-preview-tts',
'models/gemini-2.5-pro-preview-tts',
'models/learnlm-2.0-flash-experimental',
'models/gemma-3-1b-it',
'models/gemma-3-4b-it',
'models/gemma-3-12b-it',
'models/gemma-3-27b-it',
'models/gemma-3n-e4b-it',
'models/gemma-3n-e2b-it'
]

# MCQ Prompt Template
PROMPT_TEMPLATE = """
Generate one multiple choice math question for:
- Grade: {grade}
- Topic: {topic}
- Difficulty: {level}

Requirements:
- Only ONE correct answer
- Provide 3 plausible but incorrect options
- Return output ONLY in this format (JSON):
{{
  "question": "...",
  "correct_option": "...",
  "wrong_options": ["...", "...", "..."]
}}
"""



# def generate_questions(grade, topic, level):
#     prompt = PROMPT_TEMPLATE.format(grade=grade, topic=topic, level=level)
#
#     try:
#         response = MODEL.generate_content(prompt)
#         raw_text = response.text
#
#         # Try to safely evaluate JSON-like text
#         import json
#         import re
#
#         json_text = re.search(r'\{.*\}', raw_text, re.DOTALL)
#         if json_text:
#             question_data = json.loads(json_text.group())
#         else:
#             raise ValueError("No JSON block found in Gemini output.")
#
#         # Sanity checks
#         if not all(k in question_data for k in ["question", "correct_option", "wrong_options"]):
#             raise ValueError("Missing keys in Gemini response.")
#
#         return question_data
#
#     except Exception as e:
#         print("Gemini generation error:", e)
#         # Return a fallback question
#         return {
#             "question": f"[Failed to generate] {topic} (Grade {grade}, {level})",
#             "correct_option": "42",
#             "wrong_options": ["10", "24", "36"]
#         }


def generate_questions(grade, topic, level):
    prompt = PROMPT_TEMPLATE.format(grade=grade, topic=topic, level=level)

    for model_name in GEMINI_MODELS:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            raw_text = response.text.strip()

            json_text = re.search(r'\{.*\}', raw_text, re.DOTALL)
            if not json_text:
                continue  # Try next model

            question_data = json.loads(json_text.group())

            if all(k in question_data for k in ["question", "correct_option", "wrong_options"]):
                return question_data  # Success!

        except Exception as e:
            print(f"[{model_name}] Gemini generation error:", e)
            continue  # Try next model

    # Fallback if all models fail
    return {
        "question": f"[Failed to generate] {topic} (Grade {grade}, {level})",
        "correct_option": "42",
        "wrong_options": ["10", "24", "36"]
    }
# print(generate_questions(5, "addition", "easy"))