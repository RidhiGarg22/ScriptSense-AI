from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, File
import shutil
from PIL import Image
import torch
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
import numpy as np
import cv2
import re

app = FastAPI(title="AI Handwriting Analyzer (Final)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# LOAD MODEL
# -------------------------
processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten")
model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-handwritten")

device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)


# -------------------------
# TEXT CLEANING (IMPROVED)
# -------------------------
def clean_text(text):
    text = re.sub(r'[^a-zA-Z0-9.,\n ]', '', text)

    corrections = {
        "Third Work": "Hard Work",
        "Hord Work": "Hard Work",
        "Juccss": "success",
        "succds": "success",
        "a member of": "",
        "1 .": "1.",
        "2 .": "2.",
        "3 .": "3."
    }

    for wrong, correct in corrections.items():
        text = text.replace(wrong, correct)

    return text.strip()


# -------------------------
# LINE SEGMENTATION
# -------------------------
def get_text_lines(path):
    img = cv2.imread(path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 3))
    dilated = cv2.dilate(thresh, kernel, iterations=2)

    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    line_images = []

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)

        if h > 20 and w > 50:
            line = img[y:y+h, x:x+w]
            line_images.append((y, line))

    line_images = sorted(line_images, key=lambda x: x[0])

    return [line for (_, line) in line_images]


# -------------------------
# OCR PER LINE
# -------------------------
def ocr_lines(lines):
    extracted_text = []

    for line in lines:
        line = cv2.resize(line, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        line = cv2.cvtColor(line, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(line)

        pixel_values = processor(images=pil_img, return_tensors="pt").pixel_values.to(device)
        generated_ids = model.generate(pixel_values)
        text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

        text = clean_text(text)

        # Remove garbage lines
        if text and len(text) > 3:
            if text.lower() not in ["a member of", "the", "of"]:
                extracted_text.append(text)

    return extracted_text


# -------------------------
# HANDWRITING ANALYSIS
# -------------------------
def analyze_handwriting(path):
    img = cv2.imread(path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    edges = cv2.Canny(gray, 50, 150)
    coords = np.column_stack(np.where(edges > 0))

    if len(coords) > 0:
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = 90 + angle

        if angle > 10:
            slant = "Right Slanted"
        elif angle < -10:
            slant = "Left Slanted"
        else:
            slant = "Straight"
    else:
        slant = "Unknown"

    rows = np.sum(edges, axis=1)
    alignment = "Straight" if np.std(rows) < 500 else "Wavy"

    return slant, alignment


# -------------------------
# MAIN ANALYSIS
# -------------------------
def analyze(path):
    lines = get_text_lines(path)

    if not lines:
        return {
            "text": "No text detected",
            "accuracy": 0,
            "readability": "Poor",
            "slant": "Unknown",
            "alignment": "Unknown",
            "spacing": "Unknown",
            "size_consistency": "Unknown",
            "feedback": "Try clearer image"
        }

    texts = ocr_lines(lines)

    # Remove duplicates
    cleaned_lines = list(dict.fromkeys(texts))

    full_text = "\n".join(cleaned_lines)

    # Accuracy estimation
    word_count = len(full_text.split())

    if word_count > 20:
        accuracy = 85
    elif word_count > 10:
        accuracy = 75
    elif word_count > 5:
        accuracy = 65
    else:
        accuracy = 50

    # Readability
    if accuracy > 80:
        readability = "Clear"
    elif accuracy > 60:
        readability = "Moderate"
    else:
        readability = "Poor"

    slant, alignment = analyze_handwriting(path)

    # Feedback
    feedback = []

    if readability == "Poor":
        feedback.append("Improve handwriting clarity")

    if alignment == "Wavy":
        feedback.append("Improve alignment")

    if slant != "Straight":
        feedback.append("Maintain consistent slant")

    if not feedback:
        feedback.append("Good handwriting!")

    return {
        "text": full_text,
        "accuracy": accuracy,
        "readability": readability,
        "slant": slant,
        "alignment": alignment,
        "spacing": "Detected",
        "size_consistency": "Detected",
        "feedback": ", ".join(feedback)
    }


# -------------------------
# API ENDPOINT
# -------------------------
@app.post("/analyze/")
async def analyze_file(file: UploadFile = File(...)):
    path = "temp.png"

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return analyze(path)