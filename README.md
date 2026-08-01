\# AI Resume Analyzer Pro

An intelligent resume screening application that analyzes resumes against job descriptions using advanced NLP techniques.

## Features

- **Resume Analysis**: Upload PDF/DOCX files or paste resume text
- **Job Description Matching**: Compare against job requirements
- **Skill Extraction**: Automatic identification of technical skills
- **Experience Analysis**: Years of experience extraction and matching
- **NLP Processing**: Named entity recognition for candidate information
- **Model Evaluation**: Accuracy, Precision, Recall, and F1-Score metrics
- **Advanced Visualizations**: ROC curves, Precision-Recall curves, feature importance, learning curves
- **Model Architecture Graphs**: Detailed pipeline visualization with TF-IDF and cosine similarity
- **Performance Analytics**: Multi-dimensional model performance analysis

## Model Performance

Based on evaluation with sample data:
- **Accuracy**: 60.0%
- **Precision**: 50.0%
- **Recall**: 100.0%
- **F1-Score**: 66.67%

### Confusion Matrix
- **True Positives**: 2 (Correctly passed good candidates)
- **False Positives**: 2 (Incorrectly passed poor candidates)
- **True Negatives**: 1 (Correctly rejected poor candidates)
- **False Negatives**: 0 (Incorrectly rejected good candidates)

## Technology Stack

- **Backend**: Flask, Python
- **NLP**: spaCy (en_core_web_sm)
- **ML**: scikit-learn (TF-IDF, Cosine Similarity)
- **Frontend**: React, Tailwind CSS
- **File Processing**: pdfplumber, python-docx

## Installation

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python app.py
```

## Model Architecture

The system uses a multi-stage pipeline:

1. **Input Processing**: Text extraction from PDF/DOCX or direct text input
2. **Preprocessing**: Text cleaning, normalization, and tokenization
3. **Feature Extraction**:
   - TF-IDF vectorization for semantic similarity
   - Skill matching with synonym support
   - Experience extraction using regex patterns
4. **Scoring Algorithm**:
   - Cosine similarity for text matching (50% weight)
   - Skill match percentage (30% weight)
   - Experience match percentage (20% weight)
5. **Decision Making**: Pass/Fail based on 60% threshold

## Evaluation

Run the evaluation script to see model performance metrics:

```bash
python evaluate_model.py
```

