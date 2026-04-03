🧠 ScriptSense AI — Handwriting Analyzer

AI-powered handwriting analysis system that extracts handwritten text and evaluates handwriting quality using OCR and computer vision techniques. The system provides confidence scoring, readability detection, slant analysis, alignment evaluation, and intelligent feedback.

⸻

✨ Features
	•	📝 Handwritten Text Detection (OCR)
	•	🎯 Confidence Score
	•	📖 Readability Analysis
	•	📐 Slant Detection
	•	📏 Alignment Detection
	•	📊 Spacing Analysis
	•	🔠 Letter Size Detection
	•	🧠 Intelligent Feedback
	•	🌙 Luxury Dark Theme UI

⸻

🛠 Tech Stack

Frontend
	•	React.js
	•	CSS
	•	JavaScript

Backend
	•	FastAPI
	•	Python
	•	OpenCV
	•	Tesseract OCR
	•	NumPy
	•	Pillow

⸻
📁 Project Structure
Handwriting-Analyzer-OCR
│
├── backend
│   ├── main.py
│   ├── requirements.txt
│
├── frontend
│   ├── public
│   ├── src
│   ├── package.json
│   ├── package-lock.json
│
└── README.md
🚀 How to Run Project

Step 1 — Clone Repository
git clone https://github.com/RidhiGarg22/ScriptSense-AI.git
cd Handwriting-Analyzer-OCR
⚙️ Run Backend

Go to backend folder
Step 1 — Activate virtual environment
cd /Users/ridhig/Desktop/Handwriting-Analyzer-OCR/backend
source venv/bin/activate

Check you see (venv) at the start of the prompt.

Step 2 — Kill any process on port 8001
lsof -iTCP:8001 -sTCP:LISTEN
You’ll see output like: Python 4550 ... TCP localhost:8001 (LISTEN)
Note the PID (4550) and kill it:
kill -9 4550

If multiple PIDs are there, kill all of them.

Step 3 — Start FastAPI backend
uvicorn main:app --reload --port 8001

✅ You should see:

INFO:     Uvicorn running on http://127.0.0.1:8001 (Press CTRL+C to quit)

Now your backend is running.

2️⃣ Frontend
Step 1 — Open a new terminal

Do not stop backend, keep it running.

Step 2 — Install dependencies (only first time)
npm install
Step 3 — Start React frontend
npm start

✅ You should see:

Compiled successfully!
You can now view in browser: http://localhost:3000
🎯 Output

The system provides:
	•	Extracted Text
	•	Confidence Score
	•	Readability
	•	Slant Detection
	•	Alignment Detection
	•	Spacing Analysis
	•	Handwriting Feedback

⸻

💡 Future Improvements
	•	PDF Upload Support
	•	Multi-page Analysis
	•	Graph Visualization
	•	AI Personality Analysis
	•	Cloud Deployment

⸻

👩‍💻 Author

Ridhi Garg
Built with ❤️ using AI & Computer Vision

GitHub:
https://github.com/RidhiGarg22

