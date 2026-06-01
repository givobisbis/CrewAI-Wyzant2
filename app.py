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

def extract_final_message(content):
    """Extrait UNIQUEMENT le message final, pas la validation"""
    if not content:
        return None
    
    # Cherche le message après "VALIDATED FINAL RESPONSE"
    match = re.search(r'VALIDATED FINAL RESPONSE.*?\n\n(.*?)(?=\n\n\*\*|\n\[|\n\n[A-Z ]+\:|\Z)', content, re.DOTALL)
    if match:
        text = match.group(1).replace('\\n', '\n').strip()
        return text
    
    return None

def extract_validation_only(content):
    """Extrait la validation (score + grille) SANS le message final"""
    if not content:
        return None
    
    # Enlève la partie "VALIDATED FINAL RESPONSE" si présente
    cleaned = re.sub(r'VALIDATED FINAL RESPONSE.*?$', '', content, flags=re.DOTALL)
    
    return cleaned.strip()

def display_analysis_simple(raw_content):
    """Affiche l'analyse de façon lisible"""
    if not raw_content:
        st.info("Analyse non disponible")
        return
    
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
            content = match.group(1).strip().replace('\\n', '\n')
            with st.expander(f"📌 {title}"):
                lines = content.split('\n')
                for line in lines[:25]:
                    line = line.strip()
                    if line and not line.startswith('```'):
                        st.text(line[:120])
    
    if not found_any:
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
                
                # Extraire les contenus
                task0_analysis = extract_task_content(result, 0)
                task1_draft = extract_task_content(result, 1)
                task2_validation = extract_task_content(result, 2)
                
                # Extraire le message final de la validation
                final_message = extract_final_message(task2_validation) if task2_validation else None
                # Extraire la validation seule (sans le message)
                validation_only = extract_validation_only(task2_validation) if task2_validation else None
                
                st.success("✅ Réponse générée !")
                
                tab1, tab2, tab3, tab4 = st.tabs(["📊 Analyse", "✍️ Rédaction", "✅ Validation", "💬 Réponse finale"])
                
                with tab1:
                    if task0_analysis:
                        display_analysis_simple(task0_analysis)
                    else:
                        st.info("Analyse non trouvée")
                
                with tab2:
                    if task1_draft:
                        st.markdown(task1_draft.replace('\\n', '\n'))
                    else:
                        st.info("Brouillon non trouvé")
                
                with tab3:
                    if validation_only:
                        # Afficher juste le score et la grille
                        score_match = re.search(r'AVERAGE SCORE: ([\d\.]+)/5', validation_only)
                        if score_match:
                            score = float(score_match.group(1))
                            if score >= 4.5:
                                st.success(f"🏆 Score : {score}/5 - Réponse validée !")
                            else:
                                st.warning(f"⚠️ Score : {score}/5")
                        
                        # Afficher le reste de la validation (sans le message)
                        with st.expander("📋 Détails de la validation"):
                            # Enlève le message final si encore présent
                            clean_validation = re.sub(r'VALIDATED FINAL RESPONSE.*', '', validation_only, flags=re.DOTALL)
                            st.text(clean_validation[:1000])
                    else:
                        st.info("Validation non trouvée")
                
                with tab4:
                    if final_message:
                        st.markdown(f'<div style="background-color:#f0f2f6; padding:20px; border-radius:10px; font-size:16px; border-left:5px solid #ff4b4b;">{final_message}</div>', unsafe_allow_html=True)
                        with st.expander("📋 Copier le texte"):
                            st.code(final_message, language="text")
                    elif task1_draft:
                        # Fallback : utiliser le brouillon
                        st.markdown(task1_draft.replace('\\n', '\n'))
                    else:
                        st.warning("Message final non trouvé")
                
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ Erreur : {e}")
