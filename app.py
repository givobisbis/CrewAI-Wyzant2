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

def display_analysis_simple(raw_content):
    """Affiche l'analyse de façon lisible même si c'est brut"""
    if not raw_content:
        st.info("Analyse non disponible")
        return
    
    st.subheader("📊 Analyse de la demande")
    
    # Cherche les sections principales
    sections = {
        "Profil": r'(?:A\)|1\.)\s*Requester Profile(.*?)(?=(?:B\)|2\.)\s*Level|$)',
        "Niveau": r'(?:B\)|2\.)\s*Level & Experience(.*?)(?=(?:C\)|3\.)\s*Objective|$)',
        "Objectif": r'(?:C\)|3\.)\s*Objective & Motivation(.*?)(?=(?:D\)|4\.)\s*Expectations|$)',
        "Attentes": r'(?:D\)|4\.)\s*Expectations & Constraints(.*?)(?=(?:E\)|5\.)\s*Tone|$)',
        "Psychologie": r'(?:E\)|5\.)\s*Tone & Psychology(.*?)(?=(?:F\)|6\.)\s*Opportunities|$)',
        "Opportunités": r'(?:F\)|6\.)\s*Opportunities for the Tutor(.*?)(?=STRATEGIC SUMMARY|$)',
    }
    
    found_any = False
    for title, pattern in sections.items():
        match = re.search(pattern, raw_content, re.DOTALL | re.IGNORECASE)
        if match:
            found_any = True
            content = match.group(1).strip()
            # Nettoie le contenu
            content = content.replace('\\n', '\n')
            with st.expander(f"📌 {title}"):
                lines = content.split('\n')
                for line in lines[:30]:  # Limite à 30 lignes par section
                    line = line.strip()
                    if line and not line.startswith('```'):
                        st.text(line[:150])
    
    if not found_any:
        # Affiche le début du contenu brut
        with st.expander("📄 Analyse complète (version brute)"):
            st.text(raw_content[:2000])

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
                
                # Extraire les contenus des tâches
                task0_analysis = extract_task_content(result, 0)  # Analyse
                task1_draft = extract_task_content(result, 1)    # Rédaction
                task2_validation = extract_task_content(result, 2) # Validation
                
                st.success("✅ Réponse générée !")
                
                # Créer les onglets
                tab1, tab2, tab3, tab4 = st.tabs(["📊 Analyse", "✍️ Rédaction", "✅ Validation", "💬 Réponse finale"])
                
                with tab1:
                    if task0_analysis:
                        display_analysis_simple(task0_analysis)
                    else:
                        st.info("Contenu de l'analyse non trouvé")
                
                with tab2:
                    if task1_draft:
                        st.markdown(task1_draft.replace('\\n', '\n'))
                    else:
                        st.info("Contenu de la rédaction non trouvé")
                
                with tab3:
                    if task2_validation:
                        # Cherche le score
                        score_match = re.search(r'AVERAGE SCORE: (\d+\.?\d*)/5', task2_validation)
                        if score_match:
                            score = float(score_match.group(1))
                            if score >= 4.5:
                                st.success(f"🏆 Score : {score}/5 - Réponse validée !")
                            else:
                                st.warning(f"⚠️ Score : {score}/5")
                        
                        # Affiche la grille
                        with st.expander("📋 Grille d'évaluation détaillée"):
                            st.text(task2_validation[:1500])
                    else:
                        st.info("Contenu de la validation non trouvé")
                
                with tab4:
                    # Cherche le message final
                    final_message = None
                    if task2_validation:
                        match = re.search(r'VALIDATED FINAL RESPONSE.*?\n\n(.*?)(?=\n\n\*\*|\n\[|\Z)', task2_validation, re.DOTALL)
                        if match:
                            final_message = match.group(1).replace('\\n', '\n').strip()
                    
                    if not final_message and task1_draft:
                        final_message = task1_draft.replace('\\n', '\n').strip()
                    
                    if final_message:
                        st.markdown(f'<div style="background-color:#f0f2f6; padding:20px; border-radius:10px; font-size:16px; border-left:5px solid #ff4b4b;">{final_message}</div>', unsafe_allow_html=True)
                        with st.expander("📋 Copier le texte"):
                            st.code(final_message, language="text")
                    else:
                        st.warning("Message final non trouvé")
                
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ Erreur : {e}")
