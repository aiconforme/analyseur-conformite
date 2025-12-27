import streamlit as st
from dotenv import load_dotenv
import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.colors import HexColor
from io import BytesIO
import base64

load_dotenv()

# Configuration Resend (pour envoi email)
import resend
resend.api_key = os.getenv('RESEND_API_KEY')

# Configuration page
st.set_page_config(
    page_title="AI Conforme - Quiz AI Act",
    page_icon="⚖️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# CSS CUSTOM - THÈME AI CONFORME (Rose/Noir/Blanc)
st.markdown("""
<style>
    /* ===== SIDEBAR ÉLARGIE POUR TEXTE COMPLET ===== */
    [data-testid="stSidebar"] {
        min-width: 450px !important;
        max-width: 450px !important;
    }
    
    /* ===== COULEURS THÈME AI CONFORME ===== */
    :root {
        --primary-color: #FF1654;
        --background-color: #0E1117;
        --secondary-background-color: #1a1d24;
        --text-color: #FFFFFF;
    }
    
    /* ===== AGRANDIR TOUTE LA POLICE ===== */
    .main .block-container {
        font-size: 1.15rem !important;
        line-height: 1.7 !important;
    }
    
    /* Texte général */
    p, div, span {
        font-size: 1.15rem !important;
        line-height: 1.7 !important;
    }
    
    /* ===== RADIO BUTTONS PLUS GROS ===== */
    .stRadio > label {
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        color: #FFFFFF !important;
    }
    
    .stRadio > div {
        font-size: 1.1rem !important;
    }
    
    .stRadio > div > label {
        font-size: 1.1rem !important;
        padding: 8px 0 !important;
    }
    
    /* ===== EXPANDERS PLUS GROS ===== */
    .streamlit-expanderHeader {
        font-size: 1.15rem !important;
        font-weight: 500 !important;
    }
    
    /* ===== INPUTS PLUS GROS ===== */
    input {
        font-size: 1.1rem !important;
    }
    
    /* ===== BOUTONS STYLE AI CONFORME ===== */
    .stButton > button {
        background-color: #FF1654 !important;
        color: white !important;
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        padding: 0.75rem 2rem !important;
        border-radius: 8px !important;
        border: none !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background-color: #E91E63 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(255, 22, 84, 0.3) !important;
    }
    
    /* ===== DOWNLOAD BUTTON ===== */
    .stDownloadButton > button {
        background-color: #FF1654 !important;
        color: white !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
    }
    
    /* ===== SUBHEADERS ===== */
    h2, h3 {
        color: #FF1654 !important;
    }
    
    /* ===== SIDEBAR STYLING ===== */
    [data-testid="stSidebar"] {
        background-color: #1a1d24 !important;
    }
    
    /* ===== CHECKMARKS VERTS ===== */
    .check-item {
        color: #00FF00 !important;
        font-size: 1.15rem !important;
    }
    
    /* ===== LOGO CENTRÉ ===== */
    .logo-container {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* ===== HIDE STREAMLIT BRANDING ===== */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ============================================
# LOGO AI CONFORME
# ============================================

# INSTRUCTIONS POUR AJOUTER VOTRE LOGO :
# 
# Option 1 : Fichier local (simple)
# 1. Mettez votre logo dans le même dossier que app.py
# 2. Décommentez la ligne ci-dessous et remplacez par le nom de votre fichier
st.image("logo_ai_conforme.png", width=400)
#
# Option 2 : Base64 encodé (recommandé pour déploiement)
# 1. Convertissez votre logo en base64 avec : https://base64.guru/converter/encode/image
# 2. Remplacez YOUR_BASE64_HERE ci-dessous par le résultat
# 3. Décommentez les 3 lignes suivantes
#
# logo_base64 = "YOUR_BASE64_HERE"
# st.markdown(f'<div class="logo-container"><img src="data:image/png;base64,{logo_base64}" width="400"></div>', unsafe_allow_html=True)
#
# Pour l'instant, affichage du texte en attendant le logo :

# st.markdown("""
# <div class="logo-container">
#       <h1 style="color: #FF1654; font-size: 2.5rem; margin-bottom: 0;">AI CONFORME</h1>
#       <p style="color: #999; font-size: 1rem; margin-top: 0;">Conformité sans stress</p>
# </div>
# """, unsafe_allow_html=True)

# ============================================
# FONCTIONS DE SCORING
# ============================================

def calculate_score(responses):
    """
    Calcule le score de conformité AI Act basé sur les réponses.
    Version v1.0 améliorée après lecture complète de l'AI Act.
    Retourne un score sur 100.
    """
    score = 0
    
    # Q1: Usage IA (10 points - contexte basique)
    if responses['q1'] == 'Oui, plusieurs systèmes':
        score += 10
    elif responses['q1'] == 'Oui, quelques-uns':
        score += 7
    elif responses['q1'] == 'En projet/développement':
        score += 3
    elif responses['q1'] == 'Non, aucun':
        score += 10  # Pas d'IA = pas de risque de non-conformité
    
    # Q2: Pratiques interdites - CRITIQUE (pondération 2x = 20 points)
    # Article 5 de l'AI Act
    if responses['q2'] == 'Non, aucune de ces pratiques':
        score += 20
    elif responses['q2'] == 'Pas sûr':
        score += 5  # Très risqué de ne pas savoir
    else:  # Si oui à manipulation, émotions, ou scoring social
        score += 0  # Score zéro = violation critique
    
    # Q3: Systèmes haut risque - CRITIQUE (pondération 2x = 20 points)
    # Annexe III de l'AI Act
    if responses['q3'] == 'Non, seulement faible risque':
        score += 20
    elif responses['q3'] == 'Peut-être (décisions automatisées)':
        score += 10
    elif responses['q3'] == 'Oui, au moins un système haut risque':
        score += 5  # Score bas car obligations lourdes
    elif responses['q3'] == 'Pas sûr':
        score += 3  # Très risqué
    
    # Q4: Biométrie - HAUT RISQUE (pondération 1.5x = 15 points)
    if responses['q4'] == 'Non':
        score += 15
    elif responses['q4'] == 'Oui, mais anonymisées ou vérification uniquement':
        score += 8
    elif responses['q4'] == 'Oui, identification en temps réel':
        score += 2  # Très haut risque, possiblement interdit
    elif responses['q4'] == 'Pas sûr':
        score += 4
    
    # Q5: Opérations UE (10 points - contexte)
    if responses['q5'] == 'Non, hors UE uniquement':
        score += 10  # AI Act ne s'applique pas
    elif responses['q5'] == 'Oui, quelques clients UE':
        score += 5
    elif responses['q5'] == 'Oui, principalement UE':
        score += 10  # Compliance nécessaire mais reconnu
    elif responses['q5'] == 'Pas sûr':
        score += 3
    
    # Q6: Documentation (pondération 1.5x = 15 points)
    # Article 11
    if responses['q6'] == 'Oui, documentation complète et à jour':
        score += 15
    elif responses['q6'] == 'Partiellement documenté':
        score += 7
    elif responses['q6'] == 'Non, pas documenté':
        score += 0
    elif responses['q6'] == 'Aucun système IA':
        score += 15
    
    # Q7: Gestion risques + surveillance post-marché (pondération 1.5x = 15 points)
    # Articles 9 et 72
    if responses['q7'] == 'Oui, processus continu avec surveillance post-marché':
        score += 15
    elif responses['q7'] == 'Ponctuellement':
        score += 6
    elif responses['q7'] == 'Non, jamais fait':
        score += 0
    elif responses['q7'] == 'Aucun système IA':
        score += 15
    
    # Q8: Transparence + deepfakes (10 points)
    # Article 50
    if responses['q8'] == 'Oui, utilisateurs informés et contenus IA marqués':
        score += 10
    elif responses['q8'] == 'Partiellement transparent':
        score += 5
    elif responses['q8'] == 'Non, pas mentionné':
        score += 0
    elif responses['q8'] == 'Aucun système IA':
        score += 10
    
    # Q9: Gouvernance et contrôle humain (10 points)
    # Articles 14 et 17
    if responses['q9'] == 'Oui, gouvernance structurée avec contrôle humain':
        score += 10
    elif responses['q9'] == 'Partiellement (contrôle humain existe)':
        score += 6
    elif responses['q9'] == 'Non, rien de formel':
        score += 0
    elif responses['q9'] == 'Aucun système IA':
        score += 10
    
    # Q10: Formation (10 points)
    # Article 14
    if responses['q10'] == 'Oui, formation des opérateurs de systèmes IA':
        score += 10
    elif responses['q10'] == 'Formation ponctuelle passée':
        score += 5
    elif responses['q10'] == 'Non, pas de formation':
        score += 0
    elif responses['q10'] == 'Aucun système IA':
        score += 10
    
    return min(100, score)


def get_category(score):
    """Retourne la catégorie selon le score"""
    if score >= 80:
        return "excellent"
    elif score >= 60:
        return "moyen"
    elif score >= 40:
        return "faible"
    else:
        return "critique"


def get_recommendations(score, responses, category):
    """
    Retourne les recommandations selon le score et les réponses.
    Version v1.0 : textes pré-écrits par catégorie
    """
    
    recommendations = {
        "excellent": {
            "emoji": "🟢",
            "title": "EXCELLENT (80-100%)",
            "description": "Félicitations ! Votre organisation démontre une maturité élevée en conformité AI Act (Règlement UE 2024/1689).",
            "strengths": [
                "Documentation complète de vos systèmes IA",
                "Processus d'évaluation des risques établi",
                "Gouvernance IA structurée avec contrôle humain",
                "Transparence envers les utilisateurs"
            ],
            "next_steps": [
                "Maintenir vos processus de surveillance post-marché continue",
                "Préparer la certification formelle avant août 2026",
                "Former vos équipes sur les mises à jour réglementaires",
                "Documenter les cas limites et exceptions",
                "Vérifier l'absence de pratiques interdites (Article 5)"
            ],
            "cta": "Besoin d'un audit final avant certification ? Contactez-nous pour valider votre conformité complète."
        },
        
        "moyen": {
            "emoji": "🟡",
            "title": "MOYEN (60-79%)",
            "description": "Votre organisation est partiellement conforme mais présente des lacunes importantes.",
            "strengths": [
                "Bases de conformité présentes",
                "Conscience des enjeux IA",
                "Certains processus en place"
            ],
            "gaps": [
                "Documentation technique incomplète ou non à jour",
                "Processus d'évaluation des risques à formaliser",
                "Surveillance post-marché absente ou insuffisante",
                "Gouvernance IA à structurer",
                "Transparence à améliorer"
            ],
            "risks": [
                "Amendes potentielles en cas d'audit (jusqu'à 35M€ ou 7% du CA mondial)",
                "Non-conformité lors du déploiement de nouveaux systèmes",
                "Incapacité à démontrer la conformité aux autorités",
                "Violation possible de l'Article 5 (pratiques interdites)"
            ],
            "next_steps": [
                "Réaliser un audit complet de vos systèmes IA (classification Annexe III)",
                "Vérifier l'absence de pratiques interdites (manipulation, scoring social, émotions)",
                "Établir un plan d'action priorisé",
                "Mettre en place documentation technique conforme (Article 11)",
                "Former vos opérateurs de systèmes haut risque"
            ],
            "cta": "Nous pouvons vous aider avec un plan d'action sur-mesure adapté à votre situation."
        },
        
        "faible": {
            "emoji": "🟠",
            "title": "FAIBLE (40-59%)",
            "description": "⚠️ ATTENTION : Votre organisation présente des lacunes critiques en conformité AI Act.",
            "gaps": [
                "Absence de documentation technique (Article 11)",
                "Aucun processus d'évaluation des risques (Article 9)",
                "Pas de surveillance post-marché (Article 72)",
                "Pas de gouvernance IA ni contrôle humain (Articles 14 et 17)",
                "Manque de transparence vis-à-vis des utilisateurs (Article 50)",
                "Aucune formation des opérateurs",
                "Possibles violations de l'Article 5 (pratiques interdites)"
            ],
            "risks": [
                "🚨 Amendes très élevées en cas d'inspection (jusqu'à 35M€ ou 7% CA mondial)",
                "🚨 Interdiction de mise sur le marché de vos systèmes IA",
                "🚨 Responsabilité juridique en cas d'incident",
                "🚨 Perte de confiance clients et partenaires",
                "🚨 Violation Article 5 = amendes jusqu'à 35M€ ou 7% CA"
            ],
            "urgent_actions": [
                "IMMÉDIAT : Vérifier absence de pratiques interdites (Article 5)",
                "SEMAINE 1 : Identifier tous vos systèmes IA et classifier selon Annexe III",
                "SEMAINE 2 : Évaluer les systèmes à haut risque",
                "MOIS 1 : Mettre en place documentation minimale",
                "MOIS 2-3 : Établir gouvernance et formation",
                "MOIS 3 : Implémenter surveillance post-marché"
            ],
            "cta": "⚠️ ACTION URGENTE REQUISE. Contactez-nous pour un audit d'urgence et un plan de mise en conformité rapide."
        },
        
        "critique": {
            "emoji": "🔴",
            "title": "CRITIQUE (0-39%)",
            "description": "🚨 ALERTE ROUGE : Votre organisation est en situation de non-conformité grave avec l'AI Act (Règlement UE 2024/1689).",
            "severity": "Votre score indique une absence quasi-totale de mesures de conformité. Si vous utilisez des systèmes IA en Europe, vous êtes actuellement en violation potentielle de l'AI Act européen.",
            "immediate_risks": [
                "⛔ Amendes maximales en cas d'inspection : jusqu'à 35M€ ou 7% du CA mondial",
                "⛔ Violation Article 5 (pratiques interdites) : amendes jusqu'à 35M€",
                "⛔ Interdiction immédiate de mise sur le marché",
                "⛔ Responsabilité pénale en cas d'incident grave",
                "⛔ Impossibilité de commercer avec clients européens",
                "⛔ Atteinte majeure à votre réputation",
                "⛔ Systèmes haut risque non conformes (Annexe III) : sanctions immédiates"
            ],
            "emergency_plan": [
                "🚨 AUJOURD'HUI : Vérifier pratiques interdites (manipulation, scoring social, émotions au travail) - Article 5",
                "🚨 AUJOURD'HUI : Recenser tous vos systèmes IA",
                "🚨 CETTE SEMAINE : Classifier systèmes selon Annexe III (haut risque vs limité)",
                "🚨 SEMAINE 2 : Évaluer les systèmes à haut risque",
                "🚨 CE MOIS : Suspendre ou documenter les systèmes critiques",
                "🚨 90 JOURS : Établir conformité minimale viable (documentation, risques, gouvernance)"
            ],
            "legal_note": "Note importante : L'AI Act (Règlement UE 2024/1689) entre en pleine application en août 2026. Les pratiques interdites (Article 5) sont déjà en vigueur depuis février 2025. Toute non-conformité expose à des sanctions immédiates. Vous avez encore du temps pour agir, mais la situation nécessite une intervention urgente.",
            "cta": "🆘 AIDE D'URGENCE NÉCESSAIRE. Contactez-nous IMMÉDIATEMENT pour un diagnostic d'urgence gratuit et un plan de sauvetage."
        }
    }
    
    return recommendations[category]


# ============================================
# INTERFACE UTILISATEUR
# ============================================

# DISCLAIMER EN HAUT
st.info("""
⚠️ **Important :** Cet outil fournit une auto-évaluation indicative basée sur l'AI Act (Règlement UE 2024/1689).  
Il ne constitue pas un avis juridique et ne remplace pas une consultation avec un avocat spécialisé en droit européen.
""")

# TITRE SUR 2 LIGNES
st.markdown("<h1 style='text-align: center; margin-bottom: 0;'>🇪🇺 Quiz AI Act</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; margin-top: 0; color: #FF1654;'>Êtes-vous conforme ?</h2>", unsafe_allow_html=True)

st.markdown("---")

# Introduction
st.markdown("""
<div style='font-size: 1.15rem; line-height: 1.7; text-align: center;'>

L'AI Act européen (Règlement UE 2024/1689) entre en vigueur progressivement jusqu'en août 2026.<br>
<strong style='color: #FF1654;'>Amendes jusqu'à 35M€ ou 7% du CA mondial</strong> pour non-conformité.

<strong>Découvrez votre niveau de conformité en 2 minutes.</strong>

</div>
""", unsafe_allow_html=True)

# Checkmarks
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("<div class='check-item'>✅ Gratuit</div>", unsafe_allow_html=True)
with col2:
    st.markdown("<div class='check-item'>✅ Sans inscription</div>", unsafe_allow_html=True)
with col3:
    st.markdown("<div class='check-item'>✅ Résultat instantané</div>", unsafe_allow_html=True)

st.markdown("---")

# ============================================
# LES 10 QUESTIONS (VERSION AMÉLIORÉE)
# ============================================

st.markdown("## 📋 Évaluez votre conformité")

# Informations entreprise (optionnel)
with st.expander("ℹ️ Informations entreprise (optionnel)", expanded=False):
    company_name = st.text_input("Nom de l'entreprise", placeholder="Acme Corp")
    company_sector = st.selectbox(
        "Secteur d'activité",
        ["", "Technologie/SaaS", "E-commerce", "Finance/Assurance", "Santé", 
         "RH/Recrutement", "Marketing", "Éducation", "Autre"]
    )
    company_size = st.selectbox(
        "Taille entreprise",
        ["", "1-10 employés", "11-50 employés", "51-250 employés", "250+ employés"]
    )

st.markdown("### Questions de conformité")

# Q1 - Usage IA
q1 = st.radio(
    "**1. Utilisez-vous des systèmes d'IA dans vos opérations ?**",
    [
        "Oui, plusieurs systèmes",
        "Oui, quelques-uns",
        "En projet/développement",
        "Non, aucun"
    ],
    help="Exemples : chatbots, recommandations, analyse prédictive, génération de contenu, vision par ordinateur, etc."
)

# Q2 - NOUVELLE - Pratiques interdites (Article 5)
q2 = st.radio(
    "**2. Utilisez-vous l'IA pour des pratiques potentiellement interdites par l'Article 5 de l'AI Act ?**",
    [
        "Oui, pour manipulation des comportements",
        "Oui, pour surveillance émotionnelle au travail/école",
        "Oui, pour notation sociale (scoring social)",
        "Non, aucune de ces pratiques",
        "Pas sûr"
    ],
    help="⚠️ CRITIQUE : Ces pratiques sont INTERDITES par l'Article 5. Amendes jusqu'à 35M€ ou 7% CA mondial."
)

# Q3 - Systèmes haut risque (Annexe III) - AMÉLIORÉE
q3 = st.radio(
    "**3. Vos systèmes IA relèvent-ils d'une catégorie à haut risque selon l'Annexe III de l'AI Act ?**",
    [
        "Oui, au moins un système haut risque (recrutement, crédit, biométrie, éducation, santé)",
        "Peut-être (décisions automatisées affectant des personnes)",
        "Non, seulement faible risque",
        "Pas sûr"
    ],
    help="Annexe III : Biométrie, recrutement/RH, crédit/assurance, éducation, santé, infrastructures critiques, justice. Ces systèmes ont obligations lourdes."
)

# Q4 - Biométrie - AMÉLIORÉE
q4 = st.radio(
    "**4. Collectez-vous ou traitez-vous des données biométriques ?**",
    [
        "Oui, identification en temps réel (visage, voix dans espaces publics)",
        "Oui, mais anonymisées ou vérification uniquement",
        "Non",
        "Pas sûr"
    ],
    help="Identification biométrique en temps réel dans espaces publics = potentiellement INTERDITE (Article 5). Autres usages biométriques = haut risque (Annexe III)."
)

# Q5 - Opérations UE
q5 = st.radio(
    "**5. Opérez-vous dans l'UE ou vendez-vous à des clients européens ?**",
    [
        "Oui, principalement UE",
        "Oui, quelques clients UE",
        "Non, hors UE uniquement",
        "Pas sûr"
    ],
    help="L'AI Act s'applique si vos systèmes IA sont utilisés dans l'UE ou affectent des personnes en UE (Article 2)."
)

# Q6 - Documentation (Article 11) - AMÉLIORÉE
q6 = st.radio(
    "**6. Avez-vous documenté vos systèmes IA (design, données, algorithmes, tests) ?**",
    [
        "Oui, documentation complète et à jour",
        "Partiellement documenté",
        "Non, pas documenté",
        "Aucun système IA"
    ],
    help="Documentation technique OBLIGATOIRE pour systèmes haut risque (Article 11, Annexe IV). Doit être tenue à jour sur tout le cycle de vie."
)

# Q7 - Gestion risques + surveillance post-marché (Articles 9 et 72) - AMÉLIORÉE
q7 = st.radio(
    "**7. Effectuez-vous des évaluations de risques IA avec surveillance post-marché continue ?**",
    [
        "Oui, processus continu avec surveillance post-marché",
        "Ponctuellement",
        "Non, jamais fait",
        "Aucun système IA"
    ],
    help="Gestion des risques = processus ITÉRATIF CONTINU sur tout le cycle de vie (Article 9). Surveillance post-marché obligatoire (Article 72)."
)

# Q8 - Transparence + deepfakes (Article 50) - AMÉLIORÉE
q8 = st.radio(
    "**8. Vos systèmes IA respectent-ils les obligations de transparence ?**",
    [
        "Oui, utilisateurs informés et contenus IA marqués (deepfakes/textes)",
        "Partiellement transparent",
        "Non, pas mentionné",
        "Aucun système IA"
    ],
    help="Obligation d'informer utilisateurs qu'ils interagissent avec IA (Article 50). Contenus générés par IA (deepfakes, textes) doivent être marqués."
)

# Q9 - Gouvernance et contrôle humain (Articles 14 et 17) - REFORMULÉE
q9 = st.radio(
    "**9. Avez-vous un système de gouvernance IA avec contrôle humain effectif ?**",
    [
        "Oui, gouvernance structurée avec contrôle humain",
        "Partiellement (contrôle humain existe)",
        "Non, rien de formel",
        "Aucun système IA"
    ],
    help="Contrôle humain OBLIGATOIRE pour systèmes haut risque (Article 14). Système de gestion qualité requis (Article 17). Pas besoin d'un 'responsable IA' dédié."
)

# Q10 - Formation (Article 14)
q10 = st.radio(
    "**10. Formez-vous vos employés sur l'utilisation des systèmes IA ?**",
    [
        "Oui, formation des opérateurs de systèmes IA",
        "Formation ponctuelle passée",
        "Non, pas de formation",
        "Aucun système IA"
    ],
    help="Formation OBLIGATOIRE pour opérateurs de systèmes haut risque (Article 14) : comprendre capacités/limites, surveiller, prévenir biais automatisation."
)

st.markdown("---")

# Email optionnel
email = None
with st.expander("📧 Recevoir le rapport par email (optionnel)", expanded=False):
    email = st.text_input(
        "Votre email professionnel",
        placeholder="nom@entreprise.com",
        help="Recevez votre rapport détaillé + guide conformité AI Act"
    )
    st.caption("🔒 Vos données restent privées. Pas de spam.")

# ============================================
# CALCUL ET AFFICHAGE DES RÉSULTATS
# ============================================

if st.button("🚀 Calculer mon score de conformité", type="primary"):
    
    # Collecte des réponses
    responses = {
        'q1': q1, 'q2': q2, 'q3': q3, 'q4': q4, 'q5': q5,
        'q6': q6, 'q7': q7, 'q8': q8, 'q9': q9, 'q10': q10
    }
    
    company_info = {
        'name': company_name,
        'sector': company_sector,
        'size': company_size
    }
    
    # Calcul du score
    with st.spinner("Analyse de vos réponses selon l'AI Act (Règlement UE 2024/1689)..."):
        score = calculate_score(responses)
        category = get_category(score)
        recommendations = get_recommendations(score, responses, category)
    
    # ============================================
    # AFFICHAGE RÉSULTATS
    # ============================================
    
    st.markdown("---")
    st.header("📊 Vos résultats")
    
    # Score avec couleur
    col1, col2, col3 = st.columns(3)
    with col2:
        if category == "excellent":
            st.success(f"### Score: {score}/100")
        elif category == "moyen":
            st.warning(f"### Score: {score}/100")
        elif category == "faible":
            st.error(f"### Score: {score}/100")
        else:  # critique
            st.error(f"### ⚠️ Score: {score}/100")
    
    # Affichage catégorie
    st.markdown(f"## {recommendations['emoji']} {recommendations['title']}")
    st.markdown(f"**{recommendations['description']}**")
    
    st.markdown("---")
    
    # Détails selon catégorie
    if category == "excellent":
        st.subheader("✅ Points forts identifiés")
        for strength in recommendations['strengths']:
            st.markdown(f"- {strength}")
        
        st.subheader("📋 Prochaines étapes recommandées")
        for step in recommendations['next_steps']:
            st.markdown(f"- {step}")
    
    elif category == "moyen":
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("✅ Points forts")
            for strength in recommendations['strengths']:
                st.markdown(f"- {strength}")
        
        with col2:
            st.subheader("⚠️ Lacunes identifiées")
            for gap in recommendations['gaps']:
                st.markdown(f"- {gap}")
        
        st.subheader("🚨 Risques associés")
        for risk in recommendations['risks']:
            st.markdown(f"- {risk}")
        
        st.subheader("📋 Actions recommandées")
        for step in recommendations['next_steps']:
            st.markdown(f"- {step}")
    
    elif category == "faible":
        st.subheader("❌ Lacunes critiques")
        for gap in recommendations['gaps']:
            st.error(gap)
        
        st.subheader("🚨 Risques majeurs")
        for risk in recommendations['risks']:
            st.error(risk)
        
        st.subheader("⚡ Plan d'action URGENT")
        for action in recommendations['urgent_actions']:
            st.warning(action)
    
    else:  # critique
        st.error(recommendations['severity'])
        
        st.subheader("⛔ Risques immédiats")
        for risk in recommendations['immediate_risks']:
            st.error(risk)
        
        st.subheader("🚨 Plan d'urgence - 90 jours")
        for action in recommendations['emergency_plan']:
            st.error(action)
        
        st.info(recommendations['legal_note'])
    
    # CTA
    st.markdown("---")
    st.info(f"**💼 {recommendations['cta']}**")
    
    # ============================================
    # GÉNÉRATION PDF
    # ============================================
    
    st.markdown("---")
    st.subheader("📥 Télécharger votre rapport")
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # En-tête
    story.append(Paragraph("Rapport de Conformité AI Act", styles['Title']))
    story.append(Paragraph("Règlement (UE) 2024/1689", styles['Heading3']))
    story.append(Spacer(1, 20))
    
    if company_name:
        story.append(Paragraph(f"<b>Entreprise:</b> {company_name}", styles['Normal']))
    if company_sector:
        story.append(Paragraph(f"<b>Secteur:</b> {company_sector}", styles['Normal']))
    if company_size:
        story.append(Paragraph(f"<b>Taille:</b> {company_size}", styles['Normal']))
    
    story.append(Spacer(1, 20))
    story.append(Paragraph(f"<b>Score global:</b> {score}/100", styles['Heading2']))
    story.append(Paragraph(f"<b>Catégorie:</b> {recommendations['title']}", styles['Heading3']))
    story.append(Spacer(1, 20))
    
    # Description
    story.append(Paragraph("<b>Résumé:</b>", styles['Heading3']))
    story.append(Spacer(1, 8))
    story.append(Paragraph(recommendations['description'], styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Recommandations selon catégorie
    if category == "excellent":
        story.append(Paragraph("<b>Points forts:</b>", styles['Heading3']))
        story.append(Spacer(1, 8))
        for strength in recommendations['strengths']:
            story.append(Paragraph(f"• {strength}", styles['Normal']))
        story.append(Spacer(1, 12))
        
        story.append(Paragraph("<b>Prochaines étapes:</b>", styles['Heading3']))
        story.append(Spacer(1, 8))
        for step in recommendations['next_steps']:
            story.append(Paragraph(f"• {step}", styles['Normal']))
    
    elif category == "moyen":
        story.append(Paragraph("<b>Lacunes identifiées:</b>", styles['Heading3']))
        story.append(Spacer(1, 8))
        for gap in recommendations['gaps']:
            story.append(Paragraph(f"• {gap}", styles['Normal']))
        story.append(Spacer(1, 12))
        
        story.append(Paragraph("<b>Risques:</b>", styles['Heading3']))
        story.append(Spacer(1, 8))
        for risk in recommendations['risks']:
            story.append(Paragraph(f"• {risk}", styles['Normal']))
        story.append(Spacer(1, 12))
        
        story.append(Paragraph("<b>Actions recommandées:</b>", styles['Heading3']))
        story.append(Spacer(1, 8))
        for step in recommendations['next_steps']:
            story.append(Paragraph(f"• {step}", styles['Normal']))
    
    elif category in ["faible", "critique"]:
        if category == "critique":
            story.append(Paragraph(recommendations['severity'], styles['Normal']))
            story.append(Spacer(1, 12))
        
        story.append(Paragraph("<b>Lacunes critiques:</b>", styles['Heading3']))
        story.append(Spacer(1, 8))
        gaps_list = recommendations.get('gaps', []) or []
        for gap in gaps_list:
            story.append(Paragraph(f"• {gap}", styles['Normal']))
        story.append(Spacer(1, 12))
        
        risk_key = 'immediate_risks' if category == "critique" else 'risks'
        story.append(Paragraph("<b>Risques:</b>", styles['Heading3']))
        story.append(Spacer(1, 8))
        for risk in recommendations[risk_key]:
            story.append(Paragraph(f"• {risk}", styles['Normal']))
        story.append(Spacer(1, 12))
        
        action_key = 'emergency_plan' if category == "critique" else 'urgent_actions'
        story.append(Paragraph("<b>Plan d'action:</b>", styles['Heading3']))
        story.append(Spacer(1, 8))
        for action in recommendations[action_key]:
            story.append(Paragraph(f"• {action}", styles['Normal']))
    
    # Disclaimer
    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>Avertissement:</b>", styles['Heading3']))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Ce rapport est une auto-évaluation indicative basée sur l'AI Act (Règlement UE 2024/1689). Il ne constitue pas un avis juridique. Consultez un avocat spécialisé en droit européen pour une analyse complète.", styles['Normal']))
    
    # CTA
    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>Besoin d'aide ?</b>", styles['Heading3']))
    story.append(Spacer(1, 8))
    story.append(Paragraph(recommendations['cta'], styles['Normal']))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Contact: https://aiconforme.com", styles['Normal']))
    
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    
    # Bouton téléchargement
    filename = f"rapport_ai_act_{company_name.replace(' ', '_') if company_name else 'conforme'}.pdf"
    st.download_button(
        label="📥 Télécharger le rapport PDF",
        data=pdf_bytes,
        file_name=filename,
        mime="application/pdf",
        type="primary"
    )
    
    # ============================================
    # ENVOI EMAIL
    # ============================================
    
    if email and "@" in email:
        try:
            from resend import Emails
            
            Emails.send({
                "from": "no-reply@guillaumepicard.ca",
                "to": [email],
                "subject": f"Votre rapport de conformité AI Act - Score: {score}/100",
                "html": f"""
                    <h2>Quiz AI Act - Résultats</h2>
                    <p>Bonjour{' ' + company_name if company_name else ''},</p>
                    <p>Merci d'avoir complété notre quiz de conformité AI Act (Règlement UE 2024/1689).</p>
                    <p><b>Votre score :</b> {score}/100 - {recommendations['title']}</p>
                    <p><b>Catégorie :</b> {recommendations['emoji']} {recommendations['description']}</p>
                    <br>
                    <p>Vous trouverez votre rapport détaillé en pièce jointe.</p>
                    <br>
                    <p>⚖️ <strong>Besoin d'aide pour votre mise en conformité ?</strong></p>
                    <p>Onwa Studio vous accompagne dans votre conformité AI Act et RGPD.</p>
                    <p><a href="https://onwastudio.com">En savoir plus → </a></p>
                    <br>
                    <p>Cordialement,<br>L'équipe Onwa Studio</p>
                    <hr>
                    <p style="font-size: 0.9em; color: #666;">
                    <i>Ce rapport est une auto-évaluation indicative. Il ne constitue pas un avis juridique.</i>
                    </p>
                """,
                "attachments": [{
                    "filename": filename,
                    "content": list(pdf_bytes),
                }],
            })
            
            st.success(f"📧 Rapport également envoyé à {email}")
            
        except Exception as e:
            st.warning("Le rapport n'a pas pu être envoyé par email, mais vous pouvez le télécharger ci-dessus.")
    
    # ============================================
    # CTA SERVICES
    # ============================================
    
    st.markdown("---")
    st.subheader("🚀 Besoin d'aide pour votre mise en conformité ?")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("""
        ### 📋 Audit Complet
        
        Analyse approfondie de vos systèmes IA :
        - Classification Annexe III (haut risque)
        - Évaluation Article 5 (pratiques interdites)
        - Plan d'action étape par étape
        - Documentation technique
        - Support expert
        
        **À partir de 7,000 CAD**
        
        [Demander un audit →](https://onwastudio.com)
        """)
    with col2:
        st.success("""
        ### 💎 Implémentation Complète
        
        Accompagnement sur-mesure :
        - Mise en conformité complète AI Act
        - Formation de vos équipes
        - Documentation et gouvernance (Articles 11, 14, 17)
        - Surveillance post-marché (Article 72)
        - Suivi continu
        
        **À partir de 35,000 CAD**
        
        [Demander une démo →](https://onwastudio.com)
        """)
    
    st.success("✅ Analyse terminée ! Vous pouvez télécharger votre rapport ci-dessus.")

# ============================================
# SIDEBAR
# ============================================

with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #FF1654;'>⚖️ À propos</h2>", unsafe_allow_html=True)
    
    st.markdown("""
    Ce quiz évalue votre niveau de conformité à l'AI Act européen (Règlement UE 2024/1689).
    
    ### L'AI Act en bref
    
    - Réglementation européenne sur l'IA
    - Application progressive jusqu'en **août 2026**
    - Pratiques interdites (Article 5) : **déjà en vigueur**
    - Amendes jusqu'à **35M€ ou 7% CA mondial**
    - Classification par niveau de risque (Annexe III)
    
    ### Qui est concerné ?
    
    - Entreprises opérant dans l'UE
    - Fournisseurs de systèmes IA
    - Déployeurs d'IA à haut risque
    - Toute entreprise avec clients européens
    
    ### Ce quiz vous aide à :
    
    - ✅ Identifier vos pratiques interdites (Article 5)
    - ✅ Classifier vos systèmes (Annexe III)
    - ✅ Découvrir vos lacunes de conformité
    - ✅ Recevoir des recommandations
    - ✅ Planifier votre mise en conformité
    
    ---
    
    **Créé par Onwa Studio**  
    Studio québécois d'innovation IA
    
    [En savoir plus →](https://onwastudio.com)
    """)
    
    st.markdown("---")
    st.caption("v1.0 - Conformité sans stress")
