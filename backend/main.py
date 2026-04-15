from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, File
import shutil
from PIL import Image
import torch
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
import cv2
import numpy as np
import re

# NLP Libraries
import language_tool_python
import yake
import textstat

app = FastAPI(title="Handwriting Analyzer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# LOAD AI MODEL (TrOCR)
# -------------------------
processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten")
model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-handwritten")

device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

# -------------------------
# LOAD NLP TOOLS
# -------------------------
tool = language_tool_python.LanguageTool('en-US')
kw_extractor = yake.KeywordExtractor(top=5)

# -------------------------
# IMAGE PREPROCESSING
# -------------------------
def preprocess_image(path):
    img = cv2.imread(path)

    # Resize for better OCR
    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    return Image.fromarray(img)

# -------------------------
# CLEAN TEXT
# -------------------------
def clean_text(text):
    text = re.sub(r'[^a-zA-Z0-9., \n]', '', text)
    return text.strip()

# -------------------------
# NLP: CORRECT TEXT
# -------------------------
def correct_text(text):
    matches = tool.check(text)
    corrected = language_tool_python.utils.correct(text, matches)
    return corrected

# -------------------------
# NLP: STRUCTURE TEXT
# -------------------------
def structure_text(text):
    sentences = text.split(".")
    formatted = "\n".join([s.strip().capitalize() for s in sentences if s.strip()])
    return formatted

# -------------------------
# NLP: KEYWORDS
# -------------------------
def extract_keywords(text):
    keywords = kw_extractor.extract_keywords(text)
    return [kw[0] for kw in keywords]

# -------------------------
# NLP: READABILITY
# -------------------------
def get_readability(text):
    score = textstat.flesch_reading_ease(text)

    if score > 70:
        return "Easy"
    elif score > 50:
        return "Moderate"
    else:
        return "Difficult"

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
# MAIN ANALYSIS FUNCTION
# -------------------------
def analyze(path):
    image = preprocess_image(path)

    # GenAI OCR
    pixel_values = processor(images=image, return_tensors="pt").pixel_values.to(device)
    generated_ids = model.generate(pixel_values)
    raw_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

    # NLP pipeline
    cleaned = clean_text(raw_text)
    corrected = correct_text(cleaned)
    structured = structure_text(corrected)

    if not structured:
        structured = "Could not clearly detect text"

    # Accuracy (approx logic)
    accuracy = min(95, max(60, len(structured) * 1.5))

    # NLP features
    readability = get_readability(structured)
    keywords = extract_keywords(structured)

    # Handwriting analysis
    slant, alignment = analyze_handwriting(path)

    # Feedback
    feedback = []

    if readability == "Difficult":
        feedback.append("Improve handwriting clarity")

    if alignment == "Wavy":
        feedback.append("Improve baseline alignment")

    if slant != "Straight":
        feedback.append("Maintain consistent slant")

    if not feedback:
        feedback.append("Good handwriting!")

    return {
        "text": structured,
        "accuracy": accuracy,
        "readability": readability,
        "keywords": keywords,
        "slant": slant,
        "alignment": alignment,
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
