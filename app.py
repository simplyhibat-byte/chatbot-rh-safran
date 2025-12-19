import streamlit as st
import pandas as pd
import re

# Configuration de la page
st.set_page_config(
    page_title="Chatbot RH Safran",
    page_icon="💼",
    layout="centered"
)

# Stopwords français
STOPWORDS_FR = {
    'le', 'la', 'les', 'un', 'une', 'des', 'de', 'du', 'au', 'aux',
    'et', 'ou', 'mais', 'donc', 'or', 'ni', 'car',
    'est', 'ce', 'se', 'mon', 'ma', 'mes', 'ton', 'ta', 'tes',
    'je', 'tu', 'il', 'elle', 'nous', 'vous', 'ils', 'elles',
    'ai', 'as', 'a', 'ont', 'été', 'être', 'avoir', 'suis',
    'que', 'qui', 'quoi', 'dont', 'où',
    'pour', 'dans', 'sur', 'avec', 'sans', 'sous', 'par',
    'plus', 'moins', 'très', 'bien', 'comme', 'même'
}

# Mots-clés pour détecter les profils
# Mots-clés pour détecter les profils (ALIGNÉS AVEC LA BDD)
PROFIL_KEYWORDS = {
    'CDI': ['cdi', 'contrat indéterminé', 'permanent', 'titulaire'],
    'CDD': [
        'cdd', 'contrat déterminé', 'temporaire',
        'stagiaire', 'stage', 'apprenti', 'apprentissage',
        'alternance', 'alternant'
    ],
    'Intérim': ['intérim', 'intérimaire', 'interim', 'mission'],
    'Cadre': ['cadre', 'manager', 'responsable'],
    'Non-Cadre': ['non cadre', 'ouvrier', 'employé', 'technicien']
}


# Mots-clés pour détecter les domaines
DOMAINE_KEYWORDS = {
    'Congés': ['congé', 'congés', 'vacances', 'repos', 'absence'],
    'Avantages': ['avantage', 'prime', 'indemnité'],
    'Temps de travail': [
        'horaire', 'pointage', 'badge',
        'heure', 'temps de travail', '35h'
    ]
}
def nettoyer_texte(texte):
    """Nettoie et normalise le texte"""
    if not isinstance(texte, str):
        return []
    texte = texte.lower()
    texte = re.sub(r'[^\w\s]', '', texte)
    mots = [mot for mot in texte.split() if mot not in STOPWORDS_FR and len(mot) > 2]
    return mots

def detecter_profil(question):
    """Détecte le profil mentionné dans la question"""
    question_lower = question.lower()
    
    for profil, keywords in PROFIL_KEYWORDS.items():
        for keyword in keywords:
            if keyword in question_lower:
                return profil
    
    return None

def detecter_domaine(question):
    """Détecte le domaine RH mentionné dans la question"""
    question_lower = question.lower()
    
    scores = {}
    for domaine, keywords in DOMAINE_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in question_lower)
        if score > 0:
            scores[domaine] = score
    
    if scores:
        return max(scores, key=scores.get)
    return None

def calculer_similarite(mots_user, mots_base):
    """Calcule le score de similarité entre deux listes de mots"""
    if not mots_user or not mots_base:
        return 0
    
    communs = set(mots_user) & set(mots_base)
    
    # Score pondéré
    score = len(communs)
    
    # Bonus si beaucoup de mots correspondent
    ratio = len(communs) / max(len(mots_user), len(mots_base))
    score += ratio * 2
    
    return score

def obtenir_reponse(question_user, profil_force, df):
    """
    Trouve la meilleure réponse par matching de mots
    """
    # 1. Détecter le profil
    profil_detecte = detecter_profil(question_user)
    profil_user = profil_detecte if profil_detecte else profil_force
    
    # 2. Détecter le domaine
    domaine_detecte = detecter_domaine(question_user)
    
    # 3. Filtrer par profil
    df_filtre = df[df['profil'] == profil_user].copy()

    if df_filtre.empty:
        return {
            'reponse': None,
            'message': f"Aucune information disponible pour le profil '{profil_user}'.",
            'domaine': domaine_detecte,
            'question_similaire': None,
            'score': 0.0,
            'profil_detecte': profil_detecte,
            'profil_utilise': profil_user
        }

    # 4. Filtrer aussi par domaine si détecté
    if domaine_detecte:
        df_domaine = df_filtre[df_filtre['domaine'] == domaine_detecte]
        if not df_domaine.empty:
            df_filtre = df_domaine

    # 5. Nettoyer la question utilisateur
    mots_user = nettoyer_texte(question_user)
    
    if not mots_user:
        return {
            'reponse': None,
            'message': "Veuillez poser une question plus détaillée.",
            'domaine': domaine_detecte,
            'question_similaire': None,
            'score': 0.0,
            'profil_detecte': profil_detecte,
            'profil_utilise': profil_user
        }

    # 6. Calculer similarité avec chaque question
    meilleur_score = 0
    meilleure_reponse = None
    meilleur_domaine = None
    meilleure_question = None
    
    for idx, row in df_filtre.iterrows():
        mots_base = nettoyer_texte(row['question'])
        score = calculer_similarite(mots_user, mots_base)
        
        if score > meilleur_score:
            meilleur_score = score
            meilleure_reponse = row['reponse']
            meilleur_domaine = row['domaine']
            meilleure_question = row['question']
    
    # 7. Seuil de confiance
    if meilleur_score < 2:
        return {
            'reponse': None,
            'message': "Je ne trouve pas de réponse adaptée. Veuillez contacter le service RH pour une assistance personnalisée.",
            'domaine': domaine_detecte or meilleur_domaine,
            'question_similaire': None,
            'score': meilleur_score / 10,  # Normaliser
            'profil_detecte': profil_detecte,
            'profil_utilise': profil_user,
            'escalade': True
        }
    
    return {
        'reponse': meilleure_reponse,
        'message': None,
        'domaine': meilleur_domaine,
        'question_similaire': meilleure_question,
        'score': min(meilleur_score / 10, 1.0),  # Normaliser entre 0 et 1
        'profil_detecte': profil_detecte,
        'profil_utilise': profil_user,
        'escalade': False
    }

@st.cache_data
def charger_donnees():
    try:
        df = pd.read_csv('RH_infos.csv')
        return df
    except FileNotFoundError:
        st.error("❌ Fichier RH_infos.csv introuvable.")
        return None

def afficher_resultat(resultat, question):
    """Affiche le résultat de manière structurée"""
    st.markdown("---")
    st.markdown("### 💬 Réponse du Chatbot")
    
    # Profil et domaine
    col1, col2 = st.columns(2)
    with col1:
        if resultat['profil_detecte']:
            st.success(f"✅ **Profil détecté :** {resultat['profil_detecte']}")
        else:
            st.info(f"ℹ️ **Profil utilisé :** {resultat['profil_utilise']}")
    
    with col2:
        if resultat['domaine']:
            st.info(f"📁 **Domaine :** {resultat['domaine']}")
    
    # Réponse
    if resultat['reponse']:
        st.success(f"**Confiance :** {resultat['score']:.0%}")
        
        if resultat['question_similaire']:
            st.caption(f"Question similaire : *{resultat['question_similaire']}*")
        
        st.markdown("### 📝 Réponse")
        st.write(resultat['reponse'])
        
        # Feedback
        st.markdown("---")
        st.markdown("##### Cette réponse vous a-t-elle été utile ?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("👍 Oui", key=f"up_{hash(question)}"):
                st.success("Merci !")
        with col2:
            if st.button("👎 Non", key=f"down_{hash(question)}"):
                st.warning("Merci. Contactez le service RH.")
    else:
        st.warning(resultat['message'])
        
        if resultat.get('escalade'):
            st.error("### ⚠️ Escalade vers le service RH")
            st.markdown("""
            **Cette question nécessite une réponse personnalisée.**
            
            - 📧 Email : rh@safran.com
            - 📞 Tel : +33 1 XX XX XX XX
            - 🌐 Intranet Safran
            """)

def main():
    st.title("💼 Chatbot RH Safran")
    st.markdown("### Assistant virtuel pour vos questions RH")
    st.markdown("---")
    
    df = charger_donnees()
    if df is None:
        st.stop()

    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []
    
    # Statistiques
    with st.expander("📊 Statistiques de la base de connaissances"):
        col1, col2, col3 = st.columns(3)
        col1.metric("Questions disponibles", len(df))
        col2.metric("Profils couverts", df['profil'].nunique())
        col3.metric("Domaines RH", df['domaine'].nunique())
    
    # Modes
    st.markdown("### 💬 Posez votre question")
    
    tab1, tab2 = st.tabs(["🤖 Mode Automatique", "👤 Mode Manuel"])
    
    with tab1:
        st.info("💡 Mentionnez votre profil dans la question (ex: 'En tant que stagiaire...', 'Je suis CDI...')")
        
        question_auto = st.text_area(
            "Votre question RH",
            placeholder="Ex: En tant que stagiaire, ai-je droit à des tickets restaurant ?",
            height=100,
            key="q_auto"
        )
        
        profils = sorted(df['profil'].unique().tolist())
        profil_defaut = st.selectbox("Profil par défaut si non détecté :", profils, key="p_auto")
        
        if st.button("🔍 Rechercher", key="btn_auto"):
            if question_auto:
                with st.spinner("Analyse..."):
                    resultat = obtenir_reponse(question_auto, profil_defaut, df)
                    st.session_state['chat_history'].append((question_auto, resultat))
                afficher_resultat(resultat, question_auto)
            else:
                st.warning("⚠️ Veuillez saisir une question.")
    
    with tab2:
        profils = sorted(df['profil'].unique().tolist())
        profil_manuel = st.selectbox("Sélectionnez votre profil", profils, key="p_manuel")
        
        question_manuel = st.text_area(
            "Votre question RH",
            placeholder="Ex: Combien de jours de congés ?",
            height=100,
            key="q_manuel"
        )
        
        if st.button("🔍 Rechercher", key="btn_manuel"):
            if question_manuel:
                with st.spinner("Recherche..."):
                    resultat = obtenir_reponse(question_manuel, profil_manuel, df)
                    st.session_state['chat_history'].append((question_manuel, resultat))
                afficher_resultat(resultat, question_manuel)
            else:
                st.warning("⚠️ Veuillez saisir une question.")
    
    # Historique
    if st.session_state['chat_history']:
        st.markdown("---")
        st.markdown("### 🕘 Historique")
        for i, (q, r) in enumerate(reversed(st.session_state['chat_history'][-5:]), 1):
            with st.expander(f"Question {i}: {q[:50]}..."):
                st.markdown(f"**Vous :** {q}")
                if r['profil_detecte']:
                    st.success(f"✅ Profil : {r['profil_detecte']}")
                if r['domaine']:
                    st.info(f"📁 Domaine : {r['domaine']}")
                if r['reponse']:
                    st.markdown(f"**Réponse :** {r['reponse']}")
                else:
                    st.warning(r['message'])
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/150x50/003366/FFFFFF?text=SAFRAN", use_container_width=True, width= 'stretch')
        st.markdown("---")
        
        st.markdown("### 🎯 Fonctionnalités")
        st.markdown("""
        ✅ Détection auto du profil  
        ✅ Identification du domaine  
        ✅ Réponses personnalisées  
        ✅ Escalade vers RH  
        """)
        
        st.markdown("---")
        st.markdown("### 📚 Domaines")
        for d in sorted(df['domaine'].unique()):
            st.markdown(f"• {d}")
        
        st.markdown("---")
        st.markdown("### 👥 Profils")
        for p in sorted(df['profil'].unique()):
            st.markdown(f"• {p}")
        
        st.markdown("---")
        if st.button("🔄 Reset"):
            st.session_state['chat_history'] = []
            st.rerun()

if __name__ == "__main__":
    main()