import React, { useState } from "react";
import axios from "axios";
import { motion } from "framer-motion";

import {
  Upload,
  Target,
  BookOpen,
  TrendingUp,
  AlignLeft,
  Activity,
  Type,
  Loader2
} from "lucide-react";

import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);

    try {
      const response = await axios.post(
        "http://127.0.0.1:8001/analyze",
        formData
      );

      console.log("Backend Response:", response.data);
      setResult(response.data);

    } catch (error) {
      console.error(error);
      alert("Backend not running");
    }

    setLoading(false);
  };

  // Confidence Handler
  const getConfidence = () => {
    if (!result) return "0%";

    const conf =
      result.confidence ??
      result.confidence_score ??
      result.avg_confidence ??
      result.accuracy ??
      0;

    if (conf > 1) {
      return Math.round(conf) + "%";
    } else {
      return Math.round(conf * 100) + "%";
    }
  };

  return (
    <div className="app">

      <div className="bg-glow"></div>

      {/* Hero */}
      <motion.div
        className="hero"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        <span className="badge">Next-Gen Graphology</span>

        <h1 className="title">ScriptSense AI</h1>

        <p className="subtitle">
          Decoding Personality Through Intelligent Handwriting Analysis
        </p>

        {/* Upload */}
        <div className="upload-row">

          <label className="upload">
            <Upload size={18} />
            Upload Handwriting
            <input
              type="file"
              onChange={(e) => setFile(e.target.files[0])}
              hidden
            />
          </label>

          <motion.button
            whileHover={{ scale: 1.05 }}
            className="analyze"
            onClick={handleUpload}
          >
            Analyze
          </motion.button>

        </div>

        {loading && (
          <div className="loading">
            <Loader2 className="spin" />
            Analyzing handwriting...
          </div>
        )}

      </motion.div>

      {/* Results */}
      {result && (
        <motion.div
          className="grid"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >

          <Card icon={<Type />} title="Detected Text">
            {result.text || result.detected_text || "No text"}
          </Card>

          <Card icon={<Target />} title="Confidence">
            {getConfidence()}
          </Card>

          <Card icon={<BookOpen />} title="Readability">
            {result.readability || "Unknown"}
          </Card>

          <Card icon={<TrendingUp />} title="Slant">
            {result.slant || "Unknown"}
          </Card>

          <Card icon={<AlignLeft />} title="Alignment">
            {result.alignment || "Unknown"}
          </Card>

          <Card icon={<Activity />} title="Spacing">
            {result.spacing || "Auto Detected"}
          </Card>

        </motion.div>
      )}

      {/* Footer */}
      <footer className="footer">
        Crafted with Precision — Built by <span>Ridhi Garg</span>
      </footer>

    </div>
  );
}

const Card = ({ icon, title, children }) => (
  <motion.div
    className="card"
    whileHover={{ scale: 1.03 }}
  >
    <div className="icon">{icon}</div>
    <h3>{title}</h3>
    <p>{children}</p>
  </motion.div>
);

export default App;