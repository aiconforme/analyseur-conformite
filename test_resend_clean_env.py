#!/usr/bin/env python3
"""
Test Resend - Environnement propre sans CrewAI
Teste si l'envoi PDF fonctionne maintenant
"""

import os
from dotenv import load_dotenv
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

load_dotenv()

print("🧪 Test Resend - Environnement propre\n")

# 1. Installation Resend si nécessaire
try:
    import resend
    print("✅ Resend déjà installé")
except ImportError:
    print("📦 Installation de Resend...")
    import subprocess
    subprocess.run(["pip", "install", "resend"], check=True)
    import resend
    print("✅ Resend installé")

# 2. Configuration
resend_key = os.getenv('RESEND_API_KEY')
if not resend_key:
    print("❌ RESEND_API_KEY non trouvée dans .env")
    exit(1)

resend.api_key = resend_key
print(f"✅ Clé Resend chargée: {resend_key[:10]}...")

# 3. Génération PDF test
print("\n📄 Génération PDF test...")
buffer = BytesIO()
doc = SimpleDocTemplate(buffer, pagesize=A4)
styles = getSampleStyleSheet()

story = [
    Paragraph("Test Rapport Conformite RGPD", styles['Title']),
    Spacer(1, 20),
    Paragraph("Site: https://exemple.com", styles['Normal']),
    Spacer(1, 12),
    Paragraph("Score: 75/100", styles['Heading2']),
    Spacer(1, 20),
    Paragraph("Violations:", styles['Heading3']),
    Paragraph("Pas de bandeau cookies", styles['Normal']),
    Spacer(1, 20),
    Paragraph("Suggestions:", styles['Heading3']),
    Paragraph("Implémenter un bandeau cookies conforme", styles['Normal']),
]

doc.build(story)
pdf_bytes = buffer.getvalue()
print(f"✅ PDF généré ({len(pdf_bytes)} octets)")

# 4. Test envoi Resend (METHODE 2 qui fonctionnait)
print("\n📧 Test envoi email...")

try:
    from resend import Emails
    
    result = Emails.send({
        "from": "no-reply@guillaumepicard.ca",
        "to": ["info.guillaume@gmail.com"],  # Ton email
        "subject": "Test Rapport Conformite - Nouvel environnement",
        "html": """
            <h2>Test réussi!</h2>
            <p>Si tu reçois cet email avec le PDF en pièce jointe qui s'ouvre correctement,
            alors Resend fonctionne parfaitement dans le nouvel environnement!</p>
            <p>✅ Pas de CrewAI = Pas de bugs!</p>
        """,
        "attachments": [{
            "filename": "rapport_test.pdf",
            "content": list(pdf_bytes),  # Méthode 2 qui fonctionnait
        }],
    })
    
    print(f"✅ Email envoyé avec succès!")
    print(f"   ID: {result}")
    print(f"\n📬 Vérifie ta boîte email: info.guillaume@gmail.com")
    print(f"   (Regarde aussi les spams)")
    print(f"\n🎯 Si le PDF s'ouvre correctement = TOUT FONCTIONNE!")
    
except Exception as e:
    print(f"\n❌ Erreur Resend: {e}")
    import traceback
    traceback.print_exc()
    print("\n💡 Si erreur = il faudra garder téléchargement direct uniquement")
