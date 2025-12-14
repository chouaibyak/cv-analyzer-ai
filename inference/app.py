from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import fitz
import re
from typing import Dict, List

app = FastAPI(title="CV Analyzer API")

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Dictionnaire de compétences techniques (étendu)
# ---------------------------
TECHNICAL_SKILLS = {
    "langages": [
        "python", "java", "javascript", "typescript", "c++", "c#", "c", "php", 
        "ruby", "go", "rust", "swift", "kotlin", "scala", "r", "matlab"
    ],
    "frameworks": [
        "react", "angular", "vue", "django", "flask", "fastapi", "spring", 
        "node.js", "express", "laravel", "symfony", "asp.net", "next.js", 
        "nest.js", "svelte", "blazor", "gin", "fiber"
    ],
    "databases": [
        "sql", "mysql", "postgresql", "mongodb", "oracle", "redis", "cassandra", 
        "elasticsearch", "sqlite", "mariadb", "dynamodb", "neo4j", "couchdb"
    ],
    "devops": [
        "docker", "kubernetes", "jenkins", "gitlab ci", "github actions", 
        "ansible", "terraform", "aws", "azure", "gcp", "heroku", "vercel",
        "circleci", "travis ci", "prometheus", "grafana"
    ],
    "data_science": [
        "machine learning", "deep learning", "tensorflow", "pytorch", 
        "scikit-learn", "pandas", "numpy", "keras", "opencv", "nlp", "ai"
    ],
    "outils": [
        "git", "jira", "confluence", "postman", "swagger", "selenium", 
        "junit", "pytest", "maven", "gradle", "npm", "yarn", "vscode", 
        "intellij", "eclipse", "figma", "adobe xd"
    ],
    "methodologies": [
        "agile", "scrum", "kanban", "devops", "ci/cd", "tdd", "bdd", 
        "waterfall", "lean", "safe"
    ],
    "networking": [
        "tcp/ip", "http", "https", "dns", "dhcp", "nat", "vlan", "vpn",
        "cisco", "packet tracer", "lan", "wan", "switching", "routing", "rip"
    ]
}

# ---------------------------
# Extraire texte PDF
# ---------------------------
def extract_text_from_pdf(file_bytes):
    text = ""
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text.strip()

# ---------------------------
# Nettoyer et normaliser le texte
# ---------------------------
def clean_text(text: str) -> str:
    """Nettoie le texte en préservant la structure."""
    # Remplacer les multiples espaces par un seul
    text = re.sub(r'\s+', ' ', text)
    # Remplacer les multiples retours à la ligne par un seul
    text = re.sub(r'\n\s*\n', '\n\n', text)
    return text.strip()

# ---------------------------
# Segmenter le CV avec patterns améliorés
# ---------------------------
def segment_cv(text: str) -> Dict[str, str]:
    """Segmente le CV en sections avec des patterns plus robustes."""
    sections = {}
    
    # Normaliser le texte pour la recherche (garder l'original pour extraction)
    text_upper = text.upper()
    
    # Patterns améliorés pour détecter les sections
    section_patterns = {
        "PROFIL": [
            r"(PROFIL|RÉSUMÉ|OBJECTIF|À PROPOS|ABOUT|SUMMARY|OBJECTIVE)",
            r"(FORMATION|EXPERIENCE|COMPÉTENCES|EDUCATION|SKILLS|PROJECTS|PROJETS)"
        ],
        "FORMATION": [
            r"(FORMATION|ÉDUCATION|EDUCATION|DIPLÔMES|ACADEMIC|STUDIES)",
            r"(EXPERIENCE|EXPÉRIENCE|COMPÉTENCES|SKILLS|PROJECTS|PROJETS|PROFIL)"
        ],
        "EXPERIENCE": [
            r"(EXPÉRIENCE PROFESSIONNELLE|EXPÉRIENCE|EXPERIENCE|WORK EXPERIENCE|PROFESSIONAL EXPERIENCE|PARCOURS)",
            r"(FORMATION|EDUCATION|COMPÉTENCES|SKILLS|PROJECTS|PROJETS|PROFIL)"
        ],
        "COMPETENCES": [
            r"(COMPÉTENCES|COMPÉTENCES TECHNIQUES|SKILLS|TECHNICAL SKILLS|TECHNOLOGIES|OUTILS)",
            r"(FORMATION|EDUCATION|EXPERIENCE|EXPÉRIENCE|PROJECTS|PROJETS|PROFIL)"
        ],
        "PROJETS": [
            r"(PROJETS|PROJECTS|RÉALISATIONS|ACHIEVEMENTS|PORTFOLIO)",
            r"(FORMATION|EDUCATION|EXPERIENCE|EXPÉRIENCE|COMPÉTENCES|SKILLS|PROFIL|LANGUES|LANGUAGES|CERTIFICATIONS)"
        ],
        "LANGUES": [
            r"(LANGUES|LANGUAGES)",
            r"(CERTIFICATIONS|HOBBIES|LOISIRS|INTERESTS)"
        ],
        "CERTIFICATIONS": [
            r"(CERTIFICATIONS|CERTIFICATES|DIPLÔMES)",
            r"(HOBBIES|LOISIRS|INTERESTS)"
        ]
    }
    
    for section_name, (start_pattern, end_pattern) in section_patterns.items():
        # Trouver le début de la section
        start_match = re.search(start_pattern, text_upper)
        if start_match:
            start_pos = start_match.end()
            
            # Trouver la fin de la section (début de la suivante)
            end_match = re.search(end_pattern, text_upper[start_pos:])
            if end_match:
                end_pos = start_pos + end_match.start()
                section_text = text[start_pos:end_pos].strip()
            else:
                # Si pas de section suivante, prendre jusqu'à la fin
                section_text = text[start_pos:].strip()
            
            # Nettoyer et sauvegarder
            if section_text and len(section_text) > 10:
                sections[section_name] = clean_text(section_text)
    
    return sections

# ---------------------------
# Extraire les informations de contact
# ---------------------------
def extract_contact_info(text: str) -> Dict[str, str]:
    """Extrait les informations de contact du CV."""
    contact = {}
    
    # Nom (première ligne généralement)
    lines = text.split('\n')
    if lines:
        first_line = lines[0].strip()
        # Si la première ligne n'est pas trop longue et contient des mots en majuscules
        if len(first_line) < 50 and first_line.isupper():
            contact["nom"] = first_line.title()
    
    # Email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_match = re.search(email_pattern, text)
    if email_match:
        contact["email"] = email_match.group(0)
    
    # Téléphone (plusieurs formats)
    phone_patterns = [
        r'(\+?\d{1,3}[\-.\s]?)?(\(?\d{2,3}\)?[\-.\s]?)?\d{2,4}[\-.\s]?\d{2,4}[\-.\s]?\d{2,4}',
        r'\+?[0-9]{10,13}',
    ]
    for pattern in phone_patterns:
        phone_match = re.search(pattern, text)
        if phone_match:
            contact["telephone"] = phone_match.group(0)
            break
    
    # LinkedIn
    linkedin_patterns = [
        r'linkedin\.com/in/[\w-]+',
        r'(linkedin|LinkedIn)[\s:]+[\w\-]+',
    ]
    for pattern in linkedin_patterns:
        linkedin_match = re.search(pattern, text, re.IGNORECASE)
        if linkedin_match:
            contact["linkedin"] = linkedin_match.group(0)
            break
    
    # Localisation
    location_pattern = r'(Paris|Lyon|Marseille|Toulouse|Bordeaux|Lille|Nice|Nantes|Strasbourg|Montpellier|Casablanca|Rabat|Marrakech|Tanger|Fès)'
    location_match = re.search(location_pattern, text, re.IGNORECASE)
    if location_match:
        contact["localisation"] = location_match.group(0)
    
    return contact

# ---------------------------
# Extraire les compétences avec contexte
# ---------------------------
def extract_skills(text: str) -> Dict[str, List[str]]:
    """Extrait les compétences techniques avec une meilleure détection."""
    text_lower = text.lower()
    found_skills = {category: set() for category in TECHNICAL_SKILLS.keys()}
    
    for category, skills_list in TECHNICAL_SKILLS.items():
        for skill in skills_list:
            # Recherche avec word boundaries pour éviter les faux positifs
            # Mais aussi recherche sans boundaries pour des termes comme "node.js"
            patterns = [
                r'\b' + re.escape(skill) + r'\b',
                re.escape(skill),
            ]
            
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    # Capitaliser correctement
                    skill_display = skill.replace(".", ".").title()
                    # Cas spéciaux
                    if skill == "node.js":
                        skill_display = "Node.js"
                    elif skill == "express":
                        skill_display = "Express"
                    elif skill == "mongodb":
                        skill_display = "MongoDB"
                    elif skill == "mysql":
                        skill_display = "MySQL"
                    elif skill == "postgresql":
                        skill_display = "PostgreSQL"
                    elif "sql" in skill and skill != "sql":
                        skill_display = skill.upper()
                    
                    found_skills[category].add(skill_display)
                    break
    
    # Convertir les sets en listes et filtrer les catégories vides
    found_skills = {k: sorted(list(v)) for k, v in found_skills.items() if v}
    
    return found_skills

# ---------------------------
# Extraire les expériences avec meilleure structure
# ---------------------------
def extract_experiences(experience_text: str) -> List[Dict]:
    experiences = []
    if not experience_text:
        return experiences

    blocks = re.split(r'\n\s*\n', experience_text)
    
    for block in blocks:
        block = block.strip()
        if len(block) < 10:
            continue
        
        exp = {}
        block = clean_unicode_bullets(block)
        # Extraire la période
        date_match = re.search(r'(\d{1,2}/\d{4}|\d{4})\s*[-–—]\s*(présent|present|\d{1,2}/\d{4}|\d{4})', block, re.IGNORECASE)
        if date_match:
            exp["periode"] = date_match.group(0)
        
        # Poste = première partie avant la période
        if exp.get("periode"):
            exp["poste"] = block.split(exp["periode"])[0].strip()
            exp["description"] = block.split(exp["periode"])[1].strip()
        else:
            # Sinon première ligne = poste, reste = description
            lines = block.split('\n')
            exp["poste"] = lines[0].strip()
            exp["description"] = ' '.join(lines[1:]).strip()
        
        experiences.append(exp)
    
    return experiences


# ---------------------------
# Extraire les formations
# ---------------------------
def extract_education(education_text: str) -> List[Dict]:
    formations = []
    if not education_text:
        return formations
    
    # Diviser par double saut de ligne ou par point/année
    blocks = re.split(r'\n\s*\n|(?=\d{4})', education_text)
    
    for block in blocks:
        block = block.strip()
        if len(block) < 10:
            continue
        lines = [l.strip() for l in block.split('\n') if l.strip()]
        formation = {}
        # Diplôme = première ligne
        formation["diplome"] = lines[0] if lines else ""
        # Établissement = deuxième ligne si existante
        formation["etablissement"] = lines[1] if len(lines) > 1 else ""
        # Année = chercher un nombre 19xx ou 20xx
        year_match = re.search(r'\b(19|20)\d{2}\b', block)
        if year_match:
            formation["annee"] = year_match.group(0)
        if formation.get("diplome"):
            formations.append(formation)
    return formations



# ---------------------------
# Extraire les projets
# ---------------------------
def extract_projects(projects_text: str) -> List[Dict]:
    projects = []
    if not projects_text:
        return projects
    
    blocks = re.split(r'\n\s*\n', projects_text)
    
    for block in blocks:
        block = clean_unicode_bullets(block)
        lines = [l.strip() for l in block.split('\n') if l.strip()]
        if not lines:
            continue
        
        project = {}
        # Titre = première ligne jusqu'à première date
        date_match = re.search(r'(Janvier|Février|Mars|Avril|Mai|Juin|Juillet|Août|Septembre|Octobre|Novembre|Décembre)\s*\d{4}', block)
        if date_match:
            project["periode"] = date_match.group(0)
            project["titre"] = block.split(project["periode"])[0].strip()
            project["description"] = block.split(project["periode"])[1].strip()
        else:
            project["titre"] = lines[0]
            project["description"] = ' '.join(lines[1:]).strip()
        
        projects.append(project)
    
    return projects



def clean_unicode_bullets(text: str) -> str:
    text = text.replace("\uf0b7", "-")  # remplacer par tiret
    text = re.sub(r'\s+', ' ', text)  # supprimer espaces multiples
    return text.strip()



# ---------------------------
# Créer un résumé structuré amélioré
# ---------------------------
def create_structured_summary(sections: Dict[str, str], text: str) -> Dict:
    """Crée un résumé structuré et bien formaté."""
    summary = {}
    
    # Profil
    if "PROFIL" in sections:
        profile_text = sections["PROFIL"]
        # Prendre les premières phrases significatives
        sentences = re.split(r'[.!?]+', profile_text)
        meaningful_sentences = [s.strip().capitalize() for s in sentences if len(s.strip()) > 30]
        if meaningful_sentences:
            summary["profil"] = '. '.join(meaningful_sentences[:3]) + '.'
    
    # Formation
    if "FORMATION" in sections:
        summary["formation"] = extract_education(sections["FORMATION"])
    
    # Expériences
    if "EXPERIENCE" in sections:
        summary["experiences"] = extract_experiences(sections["EXPERIENCE"])
    
    # Compétences
    summary["competences"] = extract_skills(text)
    
    # Projets
    if "PROJETS" in sections:
        summary["projets"] = extract_projects(sections["PROJETS"])
    
    # Langues
    if "LANGUES" in sections:
        langues_text = sections["LANGUES"]
        langues = []
        for line in langues_text.split('\n'):
            line = re.sub(r'^[•\-\*]\s*', '', line.strip())
            if line and len(line) < 50:
                langues.append(line.title())
        if langues:
            summary["langues"] = langues[:5]
    
    # Certifications
    if "CERTIFICATIONS" in sections:
        cert_text = sections["CERTIFICATIONS"]
        certifications = []
        for line in cert_text.split('\n'):
            line = re.sub(r'^[•\-\*]\s*', '', line.strip())
            if line and len(line) < 100:
                certifications.append(line.title())
        if certifications:
            summary["certifications"] = certifications[:5]
    
    return summary

# ---------------------------
# Endpoint FastAPI
# ---------------------------
@app.post("/analyze-cv")
async def analyze_cv(file: UploadFile = File(...)):
    try:
        pdf_bytes = await file.read()
        text = extract_text_from_pdf(pdf_bytes)
        
        if not text or len(text) < 50:
            return {"error": "PDF vide ou texte non extrait. Assurez-vous que le PDF contient du texte extractible."}
        
        # Nettoyer le texte
        text = clean_text(text)
        
        # Segmenter le CV
        sections = segment_cv(text)
        
        # Extraire les informations de contact
        contact_info = extract_contact_info(text)
        
        # Créer le résumé structuré
        structured_summary = create_structured_summary(sections, text)
        
        # Extraire les compétences (déjà dans le summary mais on le garde pour compatibilité)
        skills = structured_summary.get("competences", {})
        
        return {
            "contact": contact_info,
            "summary": structured_summary,
            "skills": skills,
            "sections_detected": list(sections.keys())
        }
        
    except Exception as e:
        return {"error": f"Erreur lors de l'analyse: {str(e)}"}

@app.get("/")
async def root():
    return {"message": "CV Analyzer API is running", "version": "2.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)