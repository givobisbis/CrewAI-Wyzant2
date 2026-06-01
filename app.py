import streamlit as st
from wyzant_tutoring_response_generator.crew import WyzantTutoringResponseGeneratorCrew
import re

st.set_page_config(page_title="Wyzant Tutoring Response Generator", layout="wide")

st.title("🎓 Générateur de réponses Wyzant")
st.markdown("Génère automatiquement des réponses personnalisées pour les annonces de tutorat.")

def extract_step_content(text, step_name):
    """Extrait le contenu d'une étape spécifique"""
    patterns = {
        'analyse': [r'\*\*A\) Requester Profile\*\*.*?(?=\n\n\*\*SKILL PRESCRIPTION|\n\n\*\*STRATEGIC SUMMARY|\Z)', 
                    r'TaskOutput\(description=.*?name=\'analyze_the_wyzant_ad\'.*?raw=\'(.*?)(?=\', pydantic)'],
        'redaction': [r'TaskOutput\(description=.*?name=\'draft_the_response\'.*?raw=\'(.*?)(?=\', pydantic)'],
        'validation': [r'VALIDATED FINAL RESPONSE.*?\n\n(.*?)(?=\n\n\*\*|\n\[|\Z)',
                       r'TaskOutput\(description=.*?name=\'verify_and_validate\'.*?raw=\'(.*?)(?=\', pydantic)'],
        'score': [r'\*\*AVERAGE SCORE: ([\d\.]+)/5\*\*', r'Average score: ([\d\.]+)']
    }
    
    if step_name not in patterns:
        return None
    
    for pattern in patterns[step_name]:
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            content = match.group(1)
            content = content.replace('\\n', '\n').replace('\\"', '"').replace("\\'", "'")
            return content.strip()
    return None

def display_analysis(analysis_text):
    """Affiche l'analyse de façon lisible"""
    if not analysis_text:
        return
    
    st.subheader("📊 Étape 1 : Analyse de la demande")
    
    # Extraire les sections principales
    sections = {
        "Profil du demandeur": r'\*\*A\) Requester Profile\*\*(.*?)(?=\*\*B\)|$)',
        "Niveau & Expérience": r'\*\*B\) Level & Experience\*\*(.*?)(?=\*\*C\)|$)',
        "Objectif & Motivation": r'\*\*C\) Objective & Motivation\*\*(.*?)(?=\*\*D\)|$)',
        "Attentes & Contraintes": r'\*\*D\) Expectations & Constraints\*\*(.*?)(?=\*\*E\)|$)',
        "Tonalité & Psychologie": r'\*\*E\) Tone & Psychology\*\*(.*?)(?=\*\*F\)|$)',
        "Opportunités": r'\*\*F\) Opportunities for the Tutor\*\*(.*?)(?=\*\*STRATEGIC SUMMARY|$)',
    }
    
    for title, pattern in sections.items():
        match = re.search(pattern, analysis_text, re.DOTALL)
        if match:
            with st.expander(title):
                content = match.group(1).strip()
                # Nettoyer et formater
                lines = content.split('\n')
                for line in lines:
                    if line.strip():
                        st.text(line.strip())
    
    # Stratégie résumée
    sum_match = re.search(r'\*\*STRATEGIC SUMMARY:\*\*(.*?)(?=\*\*SKILL PRESCRIPTION|$)', analysis_text, re.DOTALL)
    if sum_match:
        with st.expander("🎯 Stratégie résumée"):
            st.info(sum_match.group(1).strip())
    
    # Prescription des compétences
    skill_match = re.search(r'\*\*SKILL PRESCRIPTION FOR THE COPYWRITER:\*\*(.*?)(?=\n\n\*\*|$)', analysis_text, re.DOTALL)
    if skill_match:
        with st.expander("🔧 Compétences recommandées"):
            st.success(skill_match.group(1).strip())

def display_draft(draft_text):
    """Affiche le brouillon de réponse"""
    if not draft_text:
        return
    st.subheader("✍️ Étape 2 : Rédaction de la réponse")
    st.markdown(draft_text)

def display_validation(validation_text):
    """Affiche la validation et le score"""
    if not validation_text:
        return
    
    st.subheader("✅ Étape 3 : Validation de la qualité")
    
    # Extraire le score
    score_match = re.search(r'\*\*AVERAGE SCORE: ([\d\.]+)/5\*\*', validation_text)
    if score_match:
        score = float(score_match.group(1))
        if score >= 4.5:
            st.success(f"🏆 Score final : {score}/5 - Réponse validée !")
        else:
            st.warning(f"⚠️ Score : {score}/5 - Réponse à améliorer")
    
    # Grille de notation (points clés)
    st.markdown("**Grille d'évaluation :**")
    criteria = [
        "Personalization (personnalisation)",
        "Relevance of skills (pertinence)",
        "Empathy (empathie)",
        "Authenticity (authenticité)",
        "Clear call to action (appel à l'action)"
    ]
    
    cols = st.columns(len(criteria))
    for i, criterion in enumerate(criteria):
        with cols[i]:
            st.metric(criterion, "✓" if "5" in validation_text or "4" in validation_text else "?")

def display_final_response(response_text):
    """Affiche la réponse finale"""
    if not response_text:
        return
    st.subheader("💬 Réponse finale (prête à copier-coller)")
    st.markdown(f'<div style="background-color:#f0f2f6; padding:15px; border-radius:10px; border-left:5px solid #ff4b4b;">{response_text}</div>', unsafe_allow_html=True)
    
    # Bouton copier
    st.code(response_text, language="markdown")

ad_text = st.text_area(
    "📝 Texte de l'annonce du tuteur",
    placeholder="Collez ici le texte de l'annonce du tuteur...",
    height=150
)

if st.button("🚀 Générer la réponse", type="primary"):
    if not ad_text.strip():
        st.error("Veuillez entrer le texte de l'annonce.")
    else:
        with st.spinner("L'agent CrewAI travaille sur votre demande... ⏳ (cela peut prendre 20-30 secondes)"):
            try:
                inputs = {'ad_text': ad_text}
                result = WyzantTutoringResponseGeneratorCrew().crew().kickoff(inputs=inputs)
                
                result_str = str(result)
                
                # Extraire et afficher chaque étape
                analysis = extract_step_content(result_str, 'analyse')
                draft = extract_step_content(result_str, 'redaction')
                validation = extract_step_content(result_str, 'validation')
                final = extract_step_content(result_str, 'validation')
                
                # Si final n'a pas été trouvé, chercher autrement
                if not final:
                    final_match = re.search(r'VALIDATED FINAL RESPONSE.*?\n\n(.+?)(?=\n\n\*\*|\n\[|\Z)', result_str, re.DOTALL)
                    if final_match:
                        final = final_match.group(1).replace('\\n', '\n').strip()
                
                # Afficher les étapes
                if analysis or draft or validation or final:
                    tabs = st.tabs(["📊 Analyse", "✍️ Rédaction", "✅ Validation", "💬 Réponse finale"])
                    
                    with tabs[0]:
                        display_analysis(result_str)
                    
                    with tabs[1]:
                        display_draft(draft if draft else "Brouillon non trouvé")
                    
                    with tabs[2]:
                        display_validation(result_str)
                    
                    with tabs[3]:
                        if final:
                            display_final_response(final)
                        elif draft:
                            display_final_response(draft)
                        else:
                            st.warning("Réponse finale non trouvée. Voici le résultat brut :")
                            st.text(result_str[:2000])
                else:
                    # Fallback : afficher tout le résultat
                    st.subheader("📋 Résultat complet")
                    st.text_area("", result_str, height=400)
                
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ Une erreur est survenue : {e}")
