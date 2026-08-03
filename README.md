# AI Resume Screener using NLP

An intelligent resume screening application that analyzes resumes against job descriptions using Natural Language Processing (NLP) and Machine Learning techniques. The application evaluates resumes based on semantic similarity, technical skills, and experience to generate an ATS-style score and provide personalized feedback.

## Live Demo

Live Application: https://resumeai-nlp.up.railway.app/

GitHub Repository: https://github.com/Gopi-410/AI-Resume-Screener-NLP

## Features

- Upload resumes in PDF and DOCX formats
- Analyze resumes against any job description
- Semantic similarity using Sentence Transformers
- TF-IDF based text similarity
- Automatic technical skill extraction
- Skill matching with synonym support
- Candidate information extraction
- Experience extraction and comparison
- ATS score generation
- Pass/Reject recommendation
- Resume improvement suggestions
- Missing skills detection

## Technology Stack

### Backend
- Python
- Flask
- Flask-CORS

### Natural Language Processing
- spaCy
- Sentence Transformers
- Scikit-learn
- TF-IDF
- Cosine Similarity
- RapidFuzz

### Frontend
- HTML
- CSS
- JavaScript

### File Processing
- pdfplumber
- python-docx

### Deployment
- Railway
- GitHub

## Project Workflow

1. Upload a resume in PDF or DOCX format.
2. Enter a job description.
3. Extract text from both documents.
4. Clean and preprocess the text.
5. Extract technical skills and candidate information.
6. Calculate semantic similarity using Sentence Transformers.
7. Calculate keyword similarity using TF-IDF and Cosine Similarity.
8. Compare required skills with resume skills.
9. Evaluate experience requirements.
10. Generate the final ATS score and recommendations.

## Scoring Method

The final score is calculated using multiple evaluation parameters:

- Semantic Similarity
- TF-IDF Similarity
- Skill Match Percentage
- Experience Match

Based on the final score, the application classifies the candidate as either **Passed** or **Rejected** and provides suggestions for improvement.

## Project Structure

```text
AI-Resume-Screener-NLP/
│
├── app.py
├── evaluate_model.py
├── requirements.txt
├── Procfile
├── runtime.txt
├── templates/
├── static/
├── uploads/
└── README.md
```

## Installation

Clone the repository

```bash
git clone https://github.com/Gopi-410/AI-Resume-Screener-NLP.git
```

Move into the project directory

```bash
cd AI-Resume-Screener-NLP
```

Create a virtual environment

```bash
python -m venv venv
```

Activate the virtual environment

Windows

```bash
venv\Scripts\activate
```

Linux/macOS

```bash
source venv/bin/activate
```

Install the required packages

```bash
pip install -r requirements.txt
```

Download the spaCy language model

```bash
python -m spacy download en_core_web_sm
```

Run the application

```bash
python app.py
```

Open the application in your browser

```text
http://127.0.0.1:5000
```

## Output

The application provides:

- ATS Score
- Resume Similarity Score
- Skill Match Percentage
- Experience Match
- Matched Skills
- Missing Skills
- Resume Suggestions
- Candidate Information
- Final Recommendation (Passed/Rejected)

## Future Improvements

- User authentication
- Resume history
- Recruiter dashboard
- Support for multiple languages
- AI-powered resume suggestions
- Interview question generation
- Resume ranking for multiple candidates

## Author

**Gopichandu T**

B.Tech Computer Science Engineering

GitHub: https://github.com/Gopi-410

LinkedIn: https://www.linkedin.com/in/t-gopichandu-1ab407327/