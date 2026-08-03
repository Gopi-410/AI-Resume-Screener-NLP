from flask import Flask, render_template, request, jsonify  # type: ignore
from flask_cors import CORS  # type: ignore
import re
from sklearn.metrics.pairwise import cosine_similarity  # type: ignore
from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore

import spacy  # type: ignore  
from sentence_transformers import SentenceTransformer, util  # type: ignore
from rapidfuzz import fuzz# type: ignore

# Load models
try:
    nlp_model = spacy.load("en_core_web_sm")
except OSError:
    print("WARNING: spacy en_core_web_sm model is missing. NLP features will be limited.")
    nlp_model = None

try:
    model = None

    def get_model():
        global model
        if model is None:
         model = SentenceTransformer('all-MiniLM-L6-v2')
        return model
except Exception as e:
    print("WARNING: SentenceTransformer model failed to load:", str(e))
    st_model = None

# File handling
import pdfplumber  # type: ignore
from docx import Document  # type: ignore

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend
def semantic_similarity(text1, text2):
    doc1 = nlp_model(text1)
    doc2 = nlp_model(text2)
    return doc1.similarity(doc2)

# -------------------------------
# Preprocess
# -------------------------------
def preprocess(text):
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s+#.]', ' ', text)
    return text
def is_valid_text(text):
    words = text.split()
    
    if len(words) < 3:
        return False
    
    avg_len = sum(len(w) for w in words) / len(words)
    if avg_len > 12:
        return False
    
    if not re.search(r'[aeiou]', text):
        return False
    
    return True

try:
    import importlib
    spacy_lang_en = importlib.import_module("spacy.lang.en")
    English = getattr(spacy_lang_en, "English", None)
    ENGLISH_STOP_WORDS = English.Defaults.stop_words if English is not None else set()
except Exception:
    ENGLISH_STOP_WORDS = set()

def remove_stopwords(text):
    return " ".join([w for w in text.split() if w not in ENGLISH_STOP_WORDS])

# -------------------------------
# SKILLS DATABASE
# -------------------------------
SKILLS_DB = [
"python","java","c","c++","c#","javascript","typescript","rust","kotlin","swift","php","ruby","matlab",
"html","css","sass","bootstrap","tailwind","react","angular","vue","nextjs","nodejs","express","django","flask","spring boot",
"mysql","postgresql","mongodb","sqlite","oracle","redis","firebase","dynamodb","cassandra",
"machine learning","deep learning","nlp","computer vision","data science","data analysis","data mining",
"pandas","numpy","scikit-learn","tensorflow","keras","pytorch","xgboost","lightgbm",
"aws","azure","google cloud","gcp","docker","kubernetes","jenkins","terraform","ansible","ci cd","github actions",
"git","github","gitlab","bitbucket","jira","postman","linux","unix","bash","powershell",
"android","ios","react native","flutter","dart","swiftui",
"hadoop","spark","kafka","hive","pig",
"cybersecurity","penetration testing","ethical hacking","network security","cryptography",
"data structures","algorithms","object oriented programming","oop","system design","design patterns",
"microservices","rest api","graphql",
"unit testing","integration testing","selenium","cypress","jest","pytest",
"communication","teamwork","leadership","problem solving","critical thinking","time management",
"excel","power bi","tableau","matplotlib","seaborn"
]

# -------------------------------
# SKILL SYNONYMS
# -------------------------------
SKILL_SYNONYMS = {
    "machine learning": ["ml"],
    "deep learning": ["dl"],
    "javascript": ["js"],
    "typescript": ["ts"],
    "nodejs": ["node.js"],
    "react": ["reactjs"],
    "postgresql": ["postgres"],
    "ci cd": ["ci/cd"],
}

# Skill Extraction
# -------------------------------
def _build_pattern(term):
    escaped = re.escape(term)
    return re.compile(rf'(?<![a-z0-9]){escaped}(?![a-z0-9])')

COMPILED_SKILLS = {skill: _build_pattern(skill) for skill in SKILLS_DB}
COMPILED_SYNONYMS = {skill: [_build_pattern(syn) for syn in syns] for skill, syns in SKILL_SYNONYMS.items()}

def extract_skills(text):
    found = set()
    for skill, pattern in COMPILED_SKILLS.items():
        if pattern.search(text):
            found.add(skill)
    for skill, patterns in COMPILED_SYNONYMS.items():
        if any(p.search(text) for p in patterns):
            found.add(skill)
    return list(found)

# -------------------------------
# Experience Extraction
# -------------------------------
def extract_experience(text):
    matches = re.findall(r'(\d+)\s*(years|year)', text)
    if matches:
        return max(int(m[0]) for m in matches)
    return 0

# -------------------------------
# File Extraction
# -------------------------------
def extract_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def extract_docx(file):
    document = Document(file)
    return "\n".join([para.text for para in document.paragraphs])

# -------------------------------
# Links Extraction (NEW)
# -------------------------------
def extract_links(text):
    """Extract LinkedIn, GitHub, portfolio, and other URLs from resume text."""
    links = []
    
    # General URL pattern
    url_pattern = re.compile(
        r'https?://[^\s<>"\')\],;]+|www\.[^\s<>"\')\],;]+',
        re.IGNORECASE
    )
    
    found_urls = url_pattern.findall(text)
    
    for url in found_urls:
        # Clean trailing punctuation
        url = url.rstrip('.,;:!?')
        
        url_lower = url.lower()
        if 'linkedin.com' in url_lower:
            links.append({"type": "LinkedIn", "url": url})
        elif 'github.com' in url_lower:
            links.append({"type": "GitHub", "url": url})
        elif 'portfolio' in url_lower or 'behance' in url_lower or 'dribbble' in url_lower:
            links.append({"type": "Portfolio", "url": url})
        else:
            links.append({"type": "Website", "url": url})
    
    return links

# -------------------------------
# Suggestions Generation (NEW)
# -------------------------------
def generate_suggestions(missing_skills, final_score=100):
    """Generate improvement suggestions based on missing skills and overall score."""
    if not missing_skills:
        if final_score < 60:
            return "You matched the required skills, but your overall similarity score is low. Try detailing your experience and using phrasing closer to the job description."
        return "Great job! Your resume covers all the key skills required for this role."
    
    skills_text = ", ".join(missing_skills)
    suggestion = f"Add these skills to improve your resume: {skills_text}. "
    
    if len(missing_skills) >= 5:
        suggestion += "Consider taking online courses or working on projects that demonstrate these competencies."
    elif len(missing_skills) >= 2:
        suggestion += "Focus on gaining practical experience with these technologies to strengthen your profile."
    else:
        suggestion += "You're almost there! A little upskilling will make your resume a perfect match."
    
    return suggestion

# -------------------------------
# Candidate NLP Extraction
# -------------------------------
def extract_candidate_info(raw_text):
    info = {
        "name": "Not Found",
        "email": "Not Found",
        "phone": "Not Found",
        "organizations": [],
        "education": []
    }
    
    # Email
    email_match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', raw_text)
    if email_match:
        info["email"] = email_match.group(0)
        
    # Phone (Indian format)
    phone_match = re.search(r'(\+91[\-\s]?)?[6-9]\d{9}', raw_text)
    if phone_match:
        info["phone"] = phone_match.group(0)

    tech_skills = set(skill.lower() for skill in SKILLS_DB)
    noise_words = {"bachelor","master","university","college","school","kalasala","b. tech","m. tech","b.tech","mpc","github pages","dom manipulation","crud","html5","css3","vs code","developer","engineer","manager","git","bash","email","web app","web development","internship","deployed","html","css","workshop","frontend","backend","full stack","live","project","education","skills","experience","certifications","objective","career","tools","platforms","hackerrank","hcl","guvi"}

    lines = [line.strip() for line in raw_text.split('\n') if len(line.strip()) > 3]

    # Check first 5 lines for name
    if lines:
        for line in lines[:5]:
            clean_line = re.split(r'Mobile:|Email:|Phone:|\+91|\||—|-', line, flags=re.IGNORECASE)[0].strip()
            lower_line = clean_line.lower()

            # Skip sentences
            if len(clean_line.split()) > 5:
                continue

            # Skip lines ending with dot
            if clean_line.endswith("."):
                continue

            # Skip common resume headings
            if any(word in lower_line for word in [
                "objective", "experience", "seeking", "looking", "undergraduate",
                "developer", "engineer", "internship"
            ]):
                continue

            if 2 <= len(clean_line.split()) <= 5 and re.match(r'^[A-Za-z\s.-]+$', clean_line):
                if not any(noise in lower_line for noise in noise_words):
                    info["name"] = clean_line.title()
                    break

    # Education
    for line in lines:
        line_lower = line.lower()
        if any(edu in line_lower for edu in ["college","university","kalasala","institute","school","b. tech","intermediate","ssc"]):
            info["education"].append(line.strip())

    # SpaCy fallback
    if nlp_model:
        doc = nlp_model(raw_text)
        for ent in doc.ents:
            clean_text = ent.text.strip()
            clean_lower = clean_text.lower()

            if clean_lower in tech_skills or any(noise in clean_lower for noise in noise_words):
                continue

            if ent.label_ == "PERSON" and info["name"] == "Not Found":
                info["name"] = clean_text

    # Email fallback for name
    if info["name"] == "Not Found" and info["email"] != "Not Found":
        possible_name = info["email"].split("@")[0]
        possible_name = re.sub(r'[^a-zA-Z]', ' ', possible_name)
        if len(possible_name.split()) >= 1:
            info["name"] = possible_name.title()

    return info

# Semantic similarity using sentence embeddings
def semantic_similarity_embeddings(text1, text2):
    embeddings = st_model.encode([text1, text2], convert_to_tensor=True)
    score = util.pytorch_cos_sim(embeddings[0], embeddings[1])
    return float(score) * 100  # scale 0-100

# Fuzzy skill matching
def fuzzy_skill_match(resume_skills, jd_skills):
    matched = []
    for jd_skill in jd_skills:
        for r_skill in resume_skills:
            if fuzz.ratio(jd_skill, r_skill) >= 85:
                matched.append(jd_skill)
    return list(set(matched))

# -------------------------------
# Routes
# -------------------------------
@app.route("/")
def home():
    # Try to render the rich frontend template. If it's missing or fails to
    # render for any reason, fall back to a simple inline landing page so the
    # root path never returns a bare 404/500 to visitors.
    try:
        return render_template("index.html")
    except Exception as e:
        print("WARNING: Failed to render index.html template:", str(e))
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8" />
            <title>AI Resume Screener &amp; NLP</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: #060913;
                    color: #f8fafc;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    min-height: 100vh;
                    margin: 0;
                    text-align: center;
                }
                .container { max-width: 600px; padding: 40px 20px; }
                h1 { font-size: 2.2rem; margin-bottom: 12px; }
                p { color: #94a3b8; line-height: 1.6; }
                code {
                    background: rgba(255,255,255,0.08);
                    padding: 2px 8px;
                    border-radius: 6px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 AI Resume Screener &amp; NLP</h1>
                <p>The API is up and running. Submit a resume and job description via
                <code>POST /analyze</code> to get a match analysis.</p>
            </div>
        </body>
        </html>
        """

@app.route("/graphs")
def graphs():
    return app.send_static_file("graphs.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        resume_text = request.form.get("resume_text", "")
        resume_file = request.files.get("resume_file")

        if resume_file and resume_file.filename != "":
            if resume_file.filename.endswith(".pdf"):
                resume = extract_pdf(resume_file)
            elif resume_file.filename.endswith(".docx"):
                resume = extract_docx(resume_file)
            else:
                return jsonify({"error": "Unsupported file format. Please upload a PDF or DOCX file."}), 400
        else:
            resume = resume_text

        jd = request.form.get("jd_text", "")
        jd_exp = int(request.form.get("jd_exp", 0))

        # Validate inputs
        if not resume.strip():
            return jsonify({"error": "Please provide a resume — either upload a file or paste the text."}), 400
        if not jd.strip():
            return jsonify({"error": "Please provide a job description to compare against."}), 400

        # Extract candidate info from raw text
        nlp_profile = extract_candidate_info(resume)
        
        # Extract links from raw text (before preprocessing)
        links = extract_links(resume)

        # Preprocess for analysis
        resume_clean = preprocess(resume)
        jd_clean = preprocess(jd)

        resume_clean = remove_stopwords(resume_clean)
        jd_clean = remove_stopwords(jd_clean)

        # Limit size (speed fix)
        resume_clean = resume_clean[:2000]
        jd_clean = jd_clean[:1000]

        # TF-IDF Cosine Similarity
        if not jd_clean or not resume_clean:
            similarity_score = 0.0
            skill_match_score = 0.0
            matched = []
            missing = []
        else:
            # Extract skills
            resume_skills = extract_skills(resume_clean)
            jd_skills = extract_skills(jd_clean)
            
            # Fuzzy skill matching
            matched = fuzzy_skill_match(resume_skills, jd_skills)
            missing = sorted(list(set(jd_skills) - set(matched)))
            skill_match_score = (len(matched) / len(jd_skills) * 100) if jd_skills else 0
            
            # Semantic similarity using embeddings
            # Validate resume text
            if not is_valid_text(resume_clean):
                similarity_score = 0
            else:
                # Use skills instead of full text
                resume_keywords = " ".join(resume_skills)
                jd_keywords = " ".join(jd_skills)

                if resume_keywords and jd_keywords:
                    try:
                        vectorizer = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b")
                        vectors = vectorizer.fit_transform([resume_keywords, jd_keywords])
                        tfidf_score = cosine_similarity(vectors[0:1], vectors[1:2])[0][0] * 100
                    except ValueError:
                        tfidf_score = 0
                else:
                    tfidf_score = 0
                
                # Blend the fast keyword matching (TF-IDF) with the deep semantic model
                embeddings_score = semantic_similarity_embeddings(resume_clean, jd_clean)
                similarity_score = (tfidf_score + embeddings_score) / 2

        # Remove fake similarity
        if similarity_score < 15:
            similarity_score = 0
        
        # Experience
        resume_exp = extract_experience(resume_clean)

        if jd_exp > 0:
            exp_score = min((resume_exp / jd_exp) * 100, 100)
            final_score = (0.5 * similarity_score) + (0.3 * skill_match_score) + (0.2 * exp_score)
        else:
            exp_score = 0
            final_score = (0.6 * similarity_score) + (0.4 * skill_match_score)

        # Status
        status = "Passed" if final_score >= 60 else "Rejected"

        # Suggestions
        suggestions = generate_suggestions(missing, final_score)



        # Build flat response
        return jsonify({
            "name": nlp_profile.get("name", "Not Found"),
            "email": nlp_profile.get("email", "Not Found"),
            "phone": nlp_profile.get("phone", "Not Found"),
            "education": nlp_profile.get("education", []),
            "similarity_score": round(similarity_score, 2),
            "skill_match_score": round(skill_match_score, 2),
            "final_score": round(final_score, 2),
            "experience_match": round(exp_score, 2),
            "status": status,
            "matched_skills": matched,
            "missing_skills": missing,
            "suggestions": suggestions,
            "links": links
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500



# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)