#!/usr/bin/env python3
"""
Script de test pour l'API d'analyse de CV
"""

import requests
import json
import sys
from pathlib import Path

# Configuration
BACKEND_URL = "http://127.0.0.1:8000"
TEST_PDF = "test_cv.pdf"  # Remplacer par le chemin de votre PDF

def test_health():
    """Test 1: Vérifier que le serveur est en ligne"""
    print("🧪 Test 1: Vérification du serveur...")
    try:
        response = requests.get(f"{BACKEND_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Serveur en ligne: {data.get('message')}")
            return True
        else:
            print(f"❌ Erreur: Status code {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

def test_analyze_cv(pdf_path):
    """Test 2: Analyser un CV"""
    print(f"\n🧪 Test 2: Analyse du CV '{pdf_path}'...")
    
    # Vérifier que le fichier existe
    if not Path(pdf_path).exists():
        print(f"❌ Fichier non trouvé: {pdf_path}")
        return False
    
    try:
        with open(pdf_path, "rb") as f:
            response = requests.post(
                f"{BACKEND_URL}/analyze-cv",
                files={"file": f},
                timeout=30
            )
        
        if response.status_code == 200:
            data = response.json()
            
            # Vérifier les erreurs
            if "error" in data:
                print(f"❌ Erreur d'analyse: {data['error']}")
                return False
            
            print("✅ Analyse réussie!\n")
            
            # Afficher les résultats
            print("=" * 60)
            print("📊 RÉSULTATS DE L'ANALYSE")
            print("=" * 60)
            
            # Contact
            if data.get("contact"):
                print("\n👤 CONTACT:")
                for key, value in data["contact"].items():
                    print(f"  - {key.title()}: {value}")
            
            # Summary
            if data.get("summary"):
                summary = data["summary"]
                
                # Profil
                if summary.get("profil"):
                    print(f"\n💼 PROFIL:")
                    print(f"  {summary['profil'][:200]}...")
                
                # Formation
                if summary.get("formation"):
                    print(f"\n🎓 FORMATION ({len(summary['formation'])} entrées):")
                    for i, formation in enumerate(summary["formation"][:3], 1):
                        if isinstance(formation, dict):
                            print(f"  {i}. {formation.get('diplome', 'N/A')}")
                        else:
                            print(f"  {i}. {formation}")
                
                # Expériences
                if summary.get("experiences"):
                    print(f"\n💼 EXPÉRIENCES ({len(summary['experiences'])} entrées):")
                    for i, exp in enumerate(summary["experiences"][:3], 1):
                        poste = exp.get('poste', 'N/A')
                        periode = exp.get('periode', '')
                        print(f"  {i}. {poste} {periode}")
                
                # Projets
                if summary.get("projets"):
                    print(f"\n🚀 PROJETS ({len(summary['projets'])} entrées):")
                    for i, projet in enumerate(summary["projets"][:3], 1):
                        if isinstance(projet, dict):
                            print(f"  {i}. {projet.get('titre', 'N/A')}")
                        else:
                            print(f"  {i}. {projet[:60]}...")
                
                # Compétences
                if summary.get("competences"):
                    print(f"\n🛠️ COMPÉTENCES:")
                    total = sum(len(v) for v in summary["competences"].values())
                    print(f"  Total: {total} compétences détectées")
                    for category, skills in summary["competences"].items():
                        if skills:
                            print(f"  - {category.title()}: {len(skills)} ({', '.join(skills[:5])}...)")
            
            # Sections détectées
            if data.get("sections_detected"):
                print(f"\n📋 SECTIONS DÉTECTÉES:")
                print(f"  {', '.join(data['sections_detected'])}")
            
            print("\n" + "=" * 60)
            
            # Sauvegarder le résultat complet
            output_file = "cv_analysis_result.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Résultat complet sauvegardé dans: {output_file}")
            
            return True
        else:
            print(f"❌ Erreur: Status code {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse: {e}")
        return False

def test_statistics(data):
    """Test 3: Statistiques sur les résultats"""
    print("\n🧪 Test 3: Statistiques...")
    
    stats = {
        "contact_fields": len(data.get("contact", {})),
        "formations": len(data.get("summary", {}).get("formation", [])),
        "experiences": len(data.get("summary", {}).get("experiences", [])),
        "projets": len(data.get("summary", {}).get("projets", [])),
        "competences": sum(len(v) for v in data.get("skills", {}).values()),
        "categories": len(data.get("skills", {})),
    }
    
    print("\n📈 Statistiques:")
    for key, value in stats.items():
        print(f"  - {key.replace('_', ' ').title()}: {value}")
    
    return stats

def main():
    """Fonction principale"""
    print("\n" + "=" * 60)
    print("🚀 DÉMARRAGE DES TESTS - CV ANALYZER")
    print("=" * 60 + "\n")
    
    # Test 1: Health check
    if not test_health():
        print("\n❌ Le serveur n'est pas accessible.")
        print("💡 Assurez-vous que le backend est lancé: python app.py")
        sys.exit(1)
    
    # Demander le chemin du PDF si non fourni
    pdf_path = TEST_PDF
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    
    if not Path(pdf_path).exists():
        print(f"\n⚠️  Fichier '{pdf_path}' non trouvé.")
        pdf_path = input("Entrez le chemin vers un fichier PDF: ").strip()
        
        if not Path(pdf_path).exists():
            print("❌ Fichier toujours introuvable. Arrêt des tests.")
            sys.exit(1)
    
    # Test 2: Analyser le CV
    if not test_analyze_cv(pdf_path):
        print("\n❌ L'analyse a échoué.")
        sys.exit(1)
    
    # Charger les résultats pour les stats
    with open("cv_analysis_result.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Test 3: Statistiques
    test_statistics(data)
    
    print("\n" + "=" * 60)
    print("✅ TOUS LES TESTS SONT PASSÉS!")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
