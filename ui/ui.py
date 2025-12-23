import gradio as gr
import requests
import os
import json

# URL du backend FastAPI
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

def format_summary(data):
    """Formate le résumé de manière lisible avec design moderne."""
    if "error" in data:
        return f" {data['error']}"
    
    summary_text = ""
    
    # Informations de contact
    if data.get("contact"):
        contact = data["contact"]
        contact_lines = []
        if contact.get("nom"):
            contact_lines.append(f"**Nom**: {contact['nom']}")
        if contact.get("email"):
            contact_lines.append(f"📧 **Email**: {contact['email']}")
        if contact.get("telephone"):
            contact_lines.append(f"📱 **Téléphone**: {contact['telephone']}")
        if contact.get("linkedin"):
            contact_lines.append(f"💼 **LinkedIn**: {contact['linkedin']}")
        if contact.get("localisation"):
            contact_lines.append(f"📍 **Localisation**: {contact['localisation']}")
        if contact_lines:
            summary_text += "## 👤 Informations de Contact\n" + "\n\n".join(contact_lines) + "\n\n---\n\n"
    
    # Résumé structuré
    if data.get("summary"):
        summary_data = data["summary"]
        
        # Profil professionnel
        if summary_data.get("profil"):
            summary_text += "## 💼 Profil Professionnel\n\n"
            summary_text += f"{summary_data['profil']}\n\n---\n\n"
        
        # Formation
        if summary_data.get("formation"):
            summary_text += "## 🎓 Formation\n\n"
            for formation in summary_data["formation"]:
                lines = []
                if formation.get("diplome"):
                    line = f"**{formation['diplome']}**"
                    if formation.get("annee"):
                        line += f" ({formation['annee']})"
                    lines.append(line)
                if formation.get("etablissement"):
                    lines.append(f"*{formation['etablissement']}*")
                summary_text += "\n".join(lines) + "\n\n"
            summary_text += "---\n\n"
        
        # Expériences professionnelles
        if summary_data.get("experiences"):
            summary_text += "## 💼 Expériences Professionnelles\n\n"
            for i, exp in enumerate(summary_data["experiences"], 1):
                lines = []
                if exp.get("poste"):
                    line = f"### {i}. {exp['poste']}"
                    if exp.get("periode"):
                        line += f" • *{exp['periode']}*"
                    lines.append(line)
                if exp.get("description"):
                    desc_lines = exp['description'].split('\n')
                    lines.extend([f"- {line.strip()}" for line in desc_lines[:5] if line.strip()])
                summary_text += "\n".join(lines) + "\n\n"
            summary_text += "---\n\n"
        
        # Projets
        if summary_data.get("projets"):
            summary_text += "## 🚀 Projets\n\n"
            for i, projet in enumerate(summary_data["projets"], 1):
                lines = []
                if projet.get("titre"):
                    line = f"### {i}. {projet['titre']}"
                    if projet.get("periode"):
                        line += f" • *{projet['periode']}*"
                    lines.append(line)
                if projet.get("description"):
                    desc_lines = projet['description'].split('\n')
                    lines.extend([f"- {line.strip()}" for line in desc_lines[:4] if line.strip()])
                summary_text += "\n".join(lines) + "\n\n"
            summary_text += "---\n\n"
        
        # Langues
        if summary_data.get("langues"):
            summary_text += "## 🌍 Langues\n\n"
            summary_text += "\n".join([f"- {langue}" for langue in summary_data["langues"]]) + "\n\n---\n\n"
        
        # Certifications
        if summary_data.get("certifications"):
            summary_text += "## 🏆 Certifications\n\n"
            summary_text += "\n".join([f"- {cert}" for cert in summary_data["certifications"]]) + "\n\n"
    
    # Sections détectées
    if data.get("sections_detected"):
        summary_text += f"*Sections détectées: {', '.join(data['sections_detected'])}*"
    
    return summary_text

def format_skills(data):
    """Formate les compétences avec un affichage moderne en colonnes."""
    if "error" in data or not data.get("skills"):
        return "❌ Aucune compétence technique détectée"
    
    skills_text = ""
    skills = data["skills"]
    category_info = {
        "langages": "💻 Langages",
        "frameworks": "🔧 Frameworks & Bibliothèques",
        "databases": "🗄️ Bases de Données",
        "devops": "☁️ DevOps & Cloud",
        "data_science": "📊 Data Science & IA",
        "outils": "🔨 Outils & Technologies",
        "methodologies": "📋 Méthodologies",
        "networking": "🌐 Réseau & Infrastructure"
    }
    
    for category, skills_list in skills.items():
        if skills_list:
            skills_text += f"## {category_info.get(category, category.title())}\n\n"
            if len(skills_list) > 4:
                skills_text += "| | | |\n|---|---|---|\n"
                for i in range(0, len(skills_list), 3):
                    row = skills_list[i:i+3]
                    skills_text += "| " + " | ".join(row) + " |\n"
            else:
                skills_text += "\n".join([f"- {skill}" for skill in skills_list])
            skills_text += "\n\n---\n\n"
    
    return skills_text

def format_raw_json(data):
    return json.dumps(data, indent=2, ensure_ascii=False)

def analyze_cv(pdf):
    if pdf is None:
        return "❌ Veuillez télécharger un fichier PDF", "", ""
    
    try:
        with open(pdf, "rb") as f:
            response = requests.post(
                f"{BACKEND_URL}/analyze-cv",
                files={"file": f},
                timeout=30
            )
        
        response.raise_for_status()
        data = response.json()
        
        return format_summary(data), format_skills(data), format_raw_json(data)
    
    except Exception as e:
        return f"❌ Erreur: {str(e)}", "", ""

# Interface Gradio
with gr.Blocks(title="AI CV Analyzer") as demo:
    gr.Markdown("# 🤖 AI CV Analyzer")
    gr.Markdown("### Analyse automatique des CV avec visualisation moderne et structurée")
    
    with gr.Row():
        file_input = gr.File(label="📤 Télécharger un CV (PDF)", file_types=[".pdf"])
    
    with gr.Row():
        analyze_btn = gr.Button("🔍 Analyser le CV", variant="primary")
    
    with gr.Tab("Résumé 📄"):
        summary_output = gr.Markdown("Téléchargez un CV pour voir le résumé...")
    
    with gr.Tab("Compétences 🛠️"):
        skills_output = gr.Markdown("Les compétences apparaîtront ici...")
    
    with gr.Tab("Données JSON 🔍"):
        json_output = gr.Code(language="json", value="{}", lines=20)
    
    analyze_btn.click(
        fn=analyze_cv,
        inputs=[file_input],
        outputs=[summary_output, skills_output, json_output]
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
