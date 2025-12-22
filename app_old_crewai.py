import streamlit as st
from dotenv import load_dotenv
import os
from langchain_openai import AzureChatOpenAI
from crewai import Agent, Task, Crew, Process
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from contextlib import redirect_stdout
from io import StringIO

# Charge les secrets .env
load_dotenv()

# LLM LangChain direct (stable Azure)
llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    temperature=0.2,
)

# ================== LES 5 AGENTS ==================
agent_crawl = Agent(
    role="Expert en crawling web",
    goal="Explorer le site et récupérer la structure, pages principales, formulaires, liens",
    backstory="Tu es un crawler intelligent capable de naviguer un site et d'en extraire l'arborescence et les éléments clés.",
    llm="azure/gpt-4o-mini",  # ton format qui fonctionnait
    allow_delegation=False,
    verbose=True,
)

agent_detect_ia = Agent(
    role="Détecteur d'usage d'IA",
    goal="Identifier si le site utilise de l'IA (chatbot, recommandations, analytics, génération contenu, etc.)",
    backstory="Tu es spécialiste en reconnaissance des technologies IA intégrées dans les sites web.",
    llm="azure/gpt-4o-mini",
    allow_delegation=False,
    verbose=True,
)

agent_rgpd = Agent(
    role="Expert RGPD",
    goal="Analyser la conformité RGPD : cookies, bandeau consentement, privacy policy, mentions légales, etc.",
    backstory="Tu connais le RGPD par cœur et tu sais repérer les manquements courants.",
    llm="azure/gpt-4o-mini",
    allow_delegation=False,
    verbose=True,
)

agent_ai_act = Agent(
    role="Expert AI Act européen",
    goal="Vérifier les obligations AI Act uniquement si usage IA détecté (transparence, classification risque, etc.)",
    backstory="Tu es à jour sur le règlement européen AI Act et ses exigences pour les fournisseurs et déployeurs.",
    llm="azure/gpt-4o-mini",
    allow_delegation=False,
    verbose=True,
)

agent_rapport = Agent(
    role="Rédacteur de rapport conformité",
    goal="Synthétiser les résultats, calculer un score /100, lister violations critiques et suggestions priorisées",
    backstory="Tu produis des rapports clairs, professionnels et visuels pour les entreprises.",
    llm="azure/gpt-4o-mini",
    allow_delegation=False,
    verbose=True,
)

# ================== INTERFACE STREAMLIT ==================
st.title("Analyseur Conformité RGPD / AI Act - MVP")

col1, col2 = st.columns([3, 1])
with col1:
    url = st.text_input("Entrez l'URL de votre site web à analyser", placeholder="https://www.example.com")
with col2:
    email = st.text_input("Votre email (pour recevoir le PDF)", placeholder="client@exemple.com")

if st.button("Lancer l'analyse"):
    if not url:
        st.error("Veuillez entrer une URL valide.")
    elif not email or "@" not in email:
        st.error("Veuillez entrer un email valide pour recevoir le rapport.")
    else:
        try:
            from azure.storage.queue import QueueClient

            queue_client = QueueClient.from_connection_string(
                os.getenv("AZURE_STORAGE_CONNECTION_STRING"), "scan-queue"
            )
            # Message = URL + séparateur + email
            message_content = f"{url}|{email}"
            queue_client.send_message(message_content)

            st.success("Analyse lancée ! Vous recevrez le rapport PDF à " + email + " dans quelques minutes.")
            st.info("Vous pouvez fermer cette page – le traitement continue en arrière-plan.")
            st.caption("Besoin d’aide ? Parlons de comment IA Diamant peut automatiser votre conformité.")
        except Exception as e:
            st.error(f"Erreur envoi queue : {e}")