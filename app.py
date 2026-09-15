PCM AI Tutor
------------
A small Flask website for Class 11 & 12 PCM (Physics, Chemistry, Maths) students.
The student picks a subject + chapter (or types one), types a question,
and the app sends a well-structured prompt to Google Gemini and shows the answer.
"""

import os
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder=".")

API_KEY = os.environ.get("GEMINI_API_KEY")
MODEL_NAME = "gemini-2.5-flash"

if API_KEY:
    genai.configure(api_key=API_KEY)

CHAPTERS = {
    "Physics": {
        "Class 11": [
            "Physical World", "Units and Measurements", "Motion in a Straight Line",
            "Motion in a Plane", "Laws of Motion", "Work, Energy and Power",
            "System of Particles and Rotational Motion", "Gravitation",
            "Mechanical Properties of Solids", "Mechanical Properties of Fluids",
            "Thermal Properties of Matter", "Thermodynamics",
            "Kinetic Theory", "Oscillations", "Waves",
        ],
        "Class 12": [
            "Electric Charges and Fields", "Electrostatic Potential and Capacitance",
            "Current Electricity", "Moving Charges and Magnetism",
            "Magnetism and Matter", "Electromagnetic Induction",
            "Alternating Current", "Electromagnetic Waves", "Ray Optics and Optical Instruments",
            "Wave Optics", "Dual Nature of Radiation and Matter", "Atoms",
            "Nuclei", "Semiconductor Electronics",
        ],
    },
    "Chemistry": {
        "Class 11": [
            "Some Basic Concepts of Chemistry", "Structure of Atom",
            "Classification of Elements and Periodicity in Properties",
            "Chemical Bonding and Molecular Structure", "States of Matter",
            "Thermodynamics", "Equilibrium", "Redox Reactions",
            "Organic Chemistry - Some Basic Principles and Techniques",
            "Hydrocarbons",
        ],
        "Class 12": [
            "Solutions", "Electrochemistry", "Chemical Kinetics",
            "d and f Block Elements", "Coordination Compounds",
            "Haloalkanes and Haloarenes", "Alcohols, Phenols and Ethers",
            "Aldehydes, Ketones and Carboxylic Acids", "Amines",
            "Biomolecules",
        ],
    },
    "Maths": {
        "Class 11": [
            "Sets", "Relations and Functions", "Trigonometric Functions",
            "Complex Numbers and Quadratic Equations",
            "Linear Inequalities", "Permutations and Combinations",
            "Binomial Theorem", "Sequences and Series",
            "Straight Lines", "Conic Sections",
            "Introduction to Three Dimensional Geometry", "Limits and Derivatives",
            "Statistics", "Probability",
        ],
        "Class 12": [
            "Relations and Functions", "Inverse Trigonometric Functions",
            "Matrices", "Determinants", "Continuity and Differentiability",
            "Application of Derivatives", "Integrals",
            "Application of Integrals", "Differential Equations",
            "Vector Algebra", "Three Dimensional Geometry",
            "Linear Programming", "Probability",
        ],
    },
}


@app.route("/")
def index():
    return render_template("index.html", chapters=CHAPTERS)


@app.route("/api/ask", methods=["POST"])
def ask():
    if not API_KEY:
        return jsonify({
            "error": "Server has no GEMINI_API_KEY set. "
                     "Set the environment variable and restart the app."
        }), 500

    data = request.get_json(force=True) or {}
    subject = (data.get("subject") or "").strip()
    grade = (data.get("grade") or "").strip()
    chapter = (data.get("chapter") or "").strip()
    question = (data.get("question") or "").strip()

    if not chapter or not question:
        return jsonify({"error": "Please provide both a chapter and a question."}), 400

    prompt = f"""You are a friendly, expert tutor for Indian Class 11-12 PCM
(Physics, Chemistry, Maths) students following the NCERT curriculum.

Subject: {subject or "Not specified"}
Grade: {grade or "Not specified"}
Chapter: {chapter}

Student's question: {question}

Instructions for your answer:
- Answer strictly in the context of the chapter "{chapter}" and the NCERT syllabus.
- Explain step by step, in simple language a school student can follow.
- Use proper formulas/equations where relevant.
- If it is a numerical problem, show the full solution with units.
- Keep it exam-oriented and concise, but complete.
"""

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        answer = response.text
    except Exception as exc:
        return jsonify({"error": f"AI request failed: {exc}"}), 500

    return jsonify({"answer": answer})


if __name__ == "__main__":
    app.run(debug=True)
