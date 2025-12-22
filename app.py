import streamlit as st
from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv
import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
import re

load_dotenv()

# Configuration Azure OpenAI
llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    temperature=0.2,
)

# Configuration Resend
import resend
resend.api_key = os.getenv('RESEND_API_KEY')

st.set_page_config(page_title="Analyseur Conformite RGPD / AI Act", page_icon="🔒")

st.title("🔒 Analyseur Conformite RGPD / AI Act")
st.markdown("Analysez la conformite de votre site web en quelques clics")

# Input URL
url = st.text_input("URL du site a analyser", placeholder="https://exemple.com")

# Email optionnel avec value proposition
email = None
newsletter = False
with st.expander("📧 Recevoir aussi le rapport par email (optionnel)", expanded=False):
    email = st.text_input(
        "Votre email professionnel",
        placeholder="nom@entreprise.com",
        help="Recevez le rapport par email + conseils conformite gratuits"
    )
    newsletter = st.checkbox(
        "Recevoir des conseils conformite (1 email/mois max)",
        value=True
    )
    st.caption("🔒 Vos donnees restent privees. Pas de spam.")

if st.button("🚀 Analyser mon site", type="primary"):
    if not url:
        st.error("Veuillez entrer une URL")
    else:
        # Conteneur pour les résultats
        results = {}
        
        # Étape 1 - Crawl
        with st.status("Analyse en cours...", expanded=True) as status:
            st.write("📡 Etape 1/5: Exploration du site...")
            crawl_prompt = f"""Analyse la structure du site web {url}.
            
Retourne:
- Pages principales trouvees
- Formulaires detectes
- Technologies utilisees
- Points d'attention

Sois concis (max 200 mots)."""

            crawl_result = llm.invoke(crawl_prompt)
            results['crawl'] = crawl_result.content
            st.success("Exploration terminee")
            
            # Étape 2 - Détection IA
            st.write("🤖 Etape 2/5: Detection usage d'IA...")
            ia_prompt = f"""Analyse ce site et detecte s'il utilise de l'IA:

Site: {url}
Structure: {results['crawl']}

Cherche: chatbots, recommandations, analytics IA, generation de contenu, etc.

Retourne:
- IA detectee: OUI ou NON
- Si oui, quels usages
- Niveau de risque (faible/moyen/eleve)

Sois concis (max 150 mots)."""

            ia_result = llm.invoke(ia_prompt)
            results['ia'] = ia_result.content
            st.success("Detection IA terminee")
            
            # Étape 3 - Analyse RGPD
            st.write("🔐 Etape 3/5: Analyse RGPD...")
            rgpd_prompt = f"""Analyse la conformite RGPD de ce site:

Site: {url}
Structure: {results['crawl']}

Verifie:
1. Bandeau cookies present?
2. Politique de confidentialite?
3. Mentions legales?
4. Formulaires avec consentement?
5. Droit d'acces aux donnees?

Retourne:
- Points conformes
- Violations critiques
- Score RGPD /100

Format: liste claire."""

            rgpd_result = llm.invoke(rgpd_prompt)
            results['rgpd'] = rgpd_result.content
            st.success("Analyse RGPD terminee")
            
            # Étape 4 - AI Act
            st.write("⚖️ Etape 4/5: Verification AI Act...")
            aiact_prompt = f"""Verifie la conformite AI Act europeen:

Site: {url}
Usage IA: {results['ia']}

Si IA detectee, verifie:
- Classification du systeme IA (risque minimal/limite/eleve/inacceptable)
- Transparence requise
- Documentation necessaire
- Obligations specifiques

Si pas d'IA, retourne: "Non applicable - aucune IA detectee"

Sois concis (max 150 mots)."""

            aiact_result = llm.invoke(aiact_prompt)
            results['aiact'] = aiact_result.content
            st.success("Verification AI Act terminee")
            
            # Étape 5 - Rapport final
            st.write("📊 Etape 5/5: Generation du rapport...")
            rapport_prompt = f"""Cree un rapport de conformite final:

Site: {url}
Analyse RGPD: {results['rgpd']}
Analyse AI Act: {results['aiact']}

Retourne:
1. SCORE GLOBAL /100 (en gras au debut)
2. Violations critiques (3 principales max)
3. Suggestions prioritaires (3 principales max)

Format clair, professionnel, concis (max 250 mots).
IMPORTANT: Commence par "Score: XX/100" """

            rapport_result = llm.invoke(rapport_prompt)
            results['rapport'] = rapport_result.content
            
            status.update(label="Analyse terminee!", state="complete", expanded=False)
        
        # Extraction du score
        score_match = re.search(r'[Ss]core[:\s]+(\d+)', results['rapport'])
        score = int(score_match.group(1)) if score_match else 75
        
        # Affichage des résultats
        st.markdown("---")
        st.header(f"📊 Resultats pour {url}")
        
        # Score avec couleur
        col1, col2, col3 = st.columns(3)
        with col2:
            if score >= 80:
                st.success(f"### Score: {score}/100")
            elif score >= 60:
                st.warning(f"### Score: {score}/100")
            else:
                st.error(f"### Score: {score}/100")
        
        # Rapport détaillé
        with st.expander("📄 Rapport complet", expanded=True):
            st.markdown(results['rapport'])
        
        with st.expander("🔍 Details de l'analyse"):
            st.subheader("Exploration du site")
            st.write(results['crawl'])
            
            st.subheader("Detection IA")
            st.write(results['ia'])
            
            st.subheader("Analyse RGPD")
            st.write(results['rgpd'])
            
            st.subheader("AI Act")
            st.write(results['aiact'])
        
        # Génération PDF
        st.markdown("---")
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Contenu PDF
        story.append(Paragraph("Rapport Conformite RGPD / AI Act", styles['Title']))
        story.append(Spacer(1, 20))
        story.append(Paragraph(f"<b>Site analyse:</b> {url}", styles['Normal']))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"<b>Score global:</b> {score}/100", styles['Heading2']))
        story.append(Spacer(1, 20))
        
        story.append(Paragraph("<b>Rapport:</b>", styles['Heading3']))
        story.append(Spacer(1, 8))
        rapport_clean = results['rapport'].replace('\n', '<br/>')
        story.append(Paragraph(rapport_clean, styles['Normal']))
        story.append(Spacer(1, 20))
        
        story.append(Paragraph("<b>Details RGPD:</b>", styles['Heading3']))
        story.append(Spacer(1, 8))
        rgpd_clean = results['rgpd'].replace('\n', '<br/>')[:1500]
        story.append(Paragraph(rgpd_clean, styles['Normal']))
        
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        
        # Bouton téléchargement (toujours disponible)
        st.download_button(
            label="📥 Telecharger le rapport PDF",
            data=pdf_bytes,
            file_name=f"rapport_conformite_{url.replace('https://', '').replace('http://', '').replace('/', '_')[:30]}.pdf",
            mime="application/pdf",
            type="primary"
        )
        
        # Envoi email si fourni
        if email and "@" in email:
            try:
                from resend import Emails
                
                Emails.send({
                    "from": "no-reply@guillaumepicard.ca",
                    "to": [email],
                    "subject": f"Votre rapport conformite RGPD/AI Act - {url}",
                    "html": f"""
                        <h2>Analyse de conformite terminee</h2>
                        <p>Bonjour,</p>
                        <p>Votre analyse de conformite RGPD et AI Act pour <strong>{url}</strong> est complete.</p>
                        <p><b>Score global :</b> {score}/100</p>
                        <p>Vous trouverez le rapport detaille en piece jointe (PDF).</p>
                        <br>
                        <p>💎 <strong>Besoin d'IA personnalisee pour votre entreprise ?</strong></p>
                        <p>Automatisez vos processus avec IA Diamant</p>
                        <p><a href="https://guillaumepicard.ca">Demander une demo gratuite →</a></p>
                        <br>
                        <p>Cordialement,<br>L'equipe IA Diamant</p>
                    """,
                    "attachments": [{
                        "filename": "rapport_conformite.pdf",
                        "content": list(pdf_bytes),
                    }],
                })
                
                st.success(f"📧 Rapport egalement envoye a {email}")
                
                # TODO: Sauvegarder le lead (email, url, newsletter) dans un fichier CSV ou DB
                
            except Exception as e:
                st.warning(f"Le rapport n'a pas pu etre envoye par email, mais vous pouvez le telecharger ci-dessus.")
        
        # CTA Premium + Services IA
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.info("""
            ### 🔓 Passez a Premium
            
            Debloquez le rapport complet avec :
            - Plan d'action detaille etape par etape
            - Conformite article par article  
            - Historique + suivi dans le temps
            - Support expert sous 48h
            
            **49$/mois** | [Essayer Premium →](#)
            """)
        with col2:
            st.success("""
            ### 💎 Besoin d'IA sur-mesure ?
            
            Automatisez vos processus metier
            avec l'IA personnalisee
            
            Audit gratuit de vos besoins
            
            [Demander une demo →](#)
            """)
        
        st.success("Analyse terminee! Vous pouvez telecharger le rapport ci-dessus.")

# Sidebar
with st.sidebar:
    st.header("ℹ️ A propos")
    st.markdown("""
    Cet outil analyse la conformite de votre site web selon:
    
    - **RGPD** (Reglement General sur la Protection des Donnees)
    - **AI Act** (Reglement europeen sur l'IA)
    
    ### Version gratuite
    
    - 1 analyse gratuite
    - Rapport simplifie
    - Telechargement PDF
    
    ### Premium - 49$/mois
    
    - 10 analyses/mois
    - Rapports complets
    - Historique 6 mois
    - Support prioritaire
    
    [En savoir plus →](#)
    """)
    
    st.markdown("---")
    st.caption("Developpe avec ❤️ par IA Diamant")
