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

def remove_final_message(text):
    """Supprime le bloc 'VALIDATED FINAL RESPONSE' d'un texte"""
    if not text:
        return text
    # Supprime tout ce qui est après "VALIDATED FINAL RESPONSE"
    cleaned = re.sub(r'VALIDATED FINAL RESPONSE.*?$', '', text, flags=re.DOTALL | re.IGNORECASE)
    return cleaned.strip()

def extract_final_message(text):
    """Extrait uniquement le message final"""
    if not text:
        return None
    match = re.search(r'VALIDATED FINAL RESPONSE[^\n]*\n\n(.*?)(?=\n\n\*\*|\n\[|\Z)', text, re.DOTALL | re.IGNORECASE)
    if match:
        msg = match.group(1).replace('\\n', '\n').strip()
        return msg
    return None

def clean_analysis_text(text):
    """Nettoie l'analyse en enlevant les caractères parasites"""
    if not text:
        return None
    # Enlève le message final
    text = remove_final_message(text)
    # Nettoie les retours à la ligne
    text = text.replace('\\n', '\n')
    # Enlève les lignes trop longues ou parasites
    lines = []
    for line in text.split('\n'):
        line = line.strip()
        if line and not line.startswith('```') and not line.startswith('{') and len(line) < 200:
            lines.append(line)
    return '\n'.join(lines[:100])  # Limite à 100 lignes

def clean_draft_text(text):
    """Nettoie le brouillon"""
    if not text:
        return None
    # Enlève le message final si présent
    text = remove_final_message(text)
    text = text.replace('\\n', '\n')
    return text[:1500]

def clean_validation_text(text):
    """Nettoie la validation en gardant le score et la grille, sans le message"""
    if not text:
        return None
    # Enlève le message final
    text = remove_final_message(text)
    text = text.replace('\\n', '\n')
    return text[:1500]

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
                
                # Extraire les contenus bruts
                raw_analysis = extract_task_content(result, 0)
                raw_draft = extract_task_content(result, 1)
                raw_validation = extract_task_content(result, 2)
                
                # Nettoyer chaque contenu
                clean_analysis = clean_analysis_text(raw_analysis)
                clean_draft = clean_draft_text(raw_draft)
                clean_validation = clean_validation_text(raw_validation)
                
                # Extraire le message final (depuis la validation)
                final_message = extract_final_message(raw_validation)
                
                st.success("✅ Réponse générée !")
                
                tab1, tab2, tab3, tab4 = st.tabs(["📊 Analyse", "✍️ Rédaction (brouillon)", "✅ Validation & Score", "💬 Réponse finale"])
                
                with tab1:
                    if clean_analysis:
                        st.markdown("### Analyse de la demande")
                        st.text(clean_analysis)
                    else:
                        st.info("Analyse non disponible")
                
                with tab2:
                    if clean_draft:
                        st.markdown("### Version initiale (brouillon)")
                        st.text(clean_draft)
                    else:
                        st.info("Brouillon non disponible")
                
                with tab3:
                    if clean_validation:
                        # Chercher le score
                        score_match = re.search(r'AVERAGE SCORE:\s*([\d\.]+)/5', clean_validation, re.IGNORECASE)
                        if score_match:
                            score = float(score_match.group(1))
                            if score >= 4.5:
                                st.success(f"🏆 **Score : {score}/5** - Réponse validée !")
                            else:
                                st.warning(f"⚠️ **Score : {score}/5**")
                        
                        with st.expander("📋 Grille d'évaluation"):
                            st.text(clean_validation[:1000])
                    else:
                        st.info("Validation non disponible")
                
                with tab4:
                    if final_message:
                        st.markdown("### 🎯 Message à copier-coller")
                        st.markdown(f'<div style="background-color:#f0f2f6; padding:20px; border-radius:10px; border-left:5px solid #ff4b4b;">{final_message}</div>', unsafe_allow_html=True)
                        with st.expander("📋 Cliquez pour copier"):
                            st.code(final_message, language="text")
                    else:
                        st.error("Message final non trouvé")
                
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ Erreur : {e}")
