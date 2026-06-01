import streamlit as st
from wyzant_tutoring_response_generator.crew import WyzantTutoringResponseGeneratorCrew
import re

st.set_page_config(page_title="Wyzant Tutoring Response Generator", layout="wide")

st.title("🎓 Générateur de réponses Wyzant")
st.markdown("Génère automatiquement des réponses personnalisées pour les annonces de tutorat.")

def extract_task_content(result, task_index):
    """Extrait le contenu brut d'une tâche spécifique"""
    if hasattr(result, 'tasks_output') and len(result.tasks_output) > task_index:
        task = result.tasks_output[task_index]
        if hasattr(task, 'raw'):
            return task.raw
    return None

def extract_final_message_from_validation(content):
    """Extrait le message final depuis la validation"""
    if not content:
        return None
    
    # Cherche le message après "VALIDATED FINAL RESPONSE"
    match = re.search(r'VALIDATED FINAL RESPONSE[^\n]*\n\n(.*?)(?=\n\n\*\*|\n\[|\n\n[A-Z ]+\:|\Z)', content, re.DOTALL)
    if match:
        text = match.group(1).replace('\\n', '\n').strip()
        # Nettoie les caractères parasites
        text = re.sub(r'\\n', '\n', text)
        text = re.sub(r'\\"', '"', text)
        return text
    
    return None

def extract_validation_only(content):
    """Extrait la validation SANS le message final"""
    if not content:
        return None
    
    # Garde seulement ce qui est avant "VALIDATED FINAL RESPONSE"
    parts = re.split(r'VALIDATED FINAL RESPONSE', content, flags=re.IGNORECASE)
    if len(parts) > 1:
        return parts[0].strip()
    return content.strip()

def display_analysis(raw_content):
    """Affiche l'analyse"""
    if not raw_content:
        st.info("Analyse non disponible")
        return
    
    sections = {
        "📌 Profil": r'(?:A\)|1\.)\s*Requester Profile(.*?)(?=(?:B\)|2\.)\s*Level|$)',
        "📌 Niveau": r'(?:B\)|2\.)\s*Level & Experience(.*?)(?=(?:C\)|3\.)\s*Objective|$)',
        "📌 Objectif": r'(?:C\)|3\.)\s*Objective & Motivation(.*?)(?=(?:D\)|4\.)\s*Expectations|$)',
        "📌 Attentes": r'(?:D\)|4\.)\s*Expectations & Constraints(.*?)(?=(?:E\)|5\.)\s*Tone|$)',
        "📌 Psychologie": r'(?:E\)|5\.)\s*Tone & Psychology(.*?)(?=(?:F\)|6\.)\s*Opportunities|$)',
    }
    
    found = False
    for title, pattern in sections.items():
        match = re.search(pattern, raw_content, re.DOTALL | re.IGNORECASE)
        if match:
            found = True
            content = match.group(1).strip().replace('\\n', '\n')
            with st.expander(title):
                # Montre les premières lignes
                lines = [l.strip() for l in content.split('\n') if l.strip() and not l.startswith('```')]
                for line in lines[:20]:
                    st.text(line[:100])
    
    if not found:
        with st.expander("📄 Analyse complète"):
            st.text(raw_content[:1500])

ad_text = st.text_area(
    "📝 Texte de l'annonce",
    placeholder="Collez ici le texte de l'annonce du tuteur...",
    height=150
)

if st.button("🚀 Générer la réponse", type="primary"):
    if not ad_text.strip():
        st.error("Veuillez entrer le texte de l'annonce.")
    else:
        with st.spinner("L'agent CrewAI travaille... ⏳ (environ 30 secondes)"):
            try:
                inputs = {'ad_text': ad_text}
                result = WyzantTutoringResponseGeneratorCrew().crew().kickoff(inputs=inputs)
                
                # Extraire les contenus des 4 tâches
                task_analysis = extract_task_content(result, 0)   # Analyse (Task 0)
                task_draft = extract_task_content(result, 1)      # Rédaction (Task 1)
                task_validation = extract_task_content(result, 2) # Validation (Task 2)
                
                # Le message final est dans la validation (Task 2)
                final_message = extract_final_message_from_validation(task_validation) if task_validation else None
                
                # La validation sans le message
                validation_only = extract_validation_only(task_validation) if task_validation else None
                
                st.success("✅ Réponse générée !")
                
                tab1, tab2, tab3, tab4 = st.tabs(["📊 Analyse", "✍️ Rédaction (brouillon)", "✅ Validation & Score", "💬 Réponse finale"])
                
                with tab1:
                    if task_analysis:
                        display_analysis(task_analysis)
                    else:
                        st.info("Analyse non trouvée")
                
                with tab2:
                    if task_draft:
                        st.markdown("### Version initiale (brouillon)")
                        st.text(task_draft.replace('\\n', '\n')[:800])
                    else:
                        st.info("Brouillon non trouvé")
                
                with tab3:
                    if validation_only:
                        # Afficher le score
                        score_match = re.search(r'AVERAGE SCORE: ([\d\.]+)/5', validation_only)
                        if score_match:
                            score = float(score_match.group(1))
                            if score >= 4.5:
                                st.success(f"🏆 **Score : {score}/5** - Réponse validée !")
                            else:
                                st.warning(f"⚠️ **Score : {score}/5**")
                        
                        # Afficher la grille de notation
                        with st.expander("📋 Grille d'évaluation détaillée"):
                            # Nettoie le texte
                            clean_text = validation_only.replace('\\n', '\n')
                            st.text(clean_text[:1200])
                    else:
                        st.info("Validation non trouvée")
                
                with tab4:
                    if final_message:
                        st.markdown("### 🎯 Message prêt à copier-coller")
                        st.markdown(f'<div style="background-color:#f0f2f6; padding:20px; border-radius:10px; border-left:5px solid #ff4b4b;">{final_message}</div>', unsafe_allow_html=True)
                        
                        # Bouton de copie
                        with st.expander("📋 Cliquez pour copier"):
                            st.code(final_message, language="markdown")
                    elif task_validation:
                        # Fallback: montrer la validation entière
                        st.warning("Message final non extrait automatiquement. Voici le contenu brut :")
                        st.text(task_validation[:1000])
                    else:
                        st.error("Aucun message trouvé")
                
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ Erreur : {e}")
