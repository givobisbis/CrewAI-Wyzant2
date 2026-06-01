import streamlit as st
from wyzant_tutoring_response_generator.crew import WyzantTutoringResponseGeneratorCrew
import re

st.set_page_config(page_title="Wyzant Tutoring Response Generator", layout="centered")

st.title("🎓 Générateur de réponses Wyzant")
st.markdown("Génère automatiquement des réponses personnalisées pour les annonces de tutorat.")

ad_text = st.text_area(
    "📝 Texte de l'annonce du tuteur",
    placeholder="Collez ici le texte de l'annonce du tuteur...",
    height=200
)

if st.button("🚀 Générer la réponse", type="primary"):
    if not ad_text.strip():
        st.error("Veuillez entrer le texte de l'annonce.")
    else:
        with st.spinner("L'agent CrewAI réfléchit... ⏳"):
            try:
                inputs = {'ad_text': ad_text}
                result = WyzantTutoringResponseGeneratorCrew().crew().kickoff(inputs=inputs)
                
                # Extraire uniquement le message final
                final_message = extract_final_response(result)
                
                st.success("✅ Réponse générée !")
                st.markdown("### 📤 Réponse proposée :")
                st.markdown(final_message)  # Affiche proprement formaté
                
                # Bouton pour copier
                st.code(final_message, language="text")
                
            except Exception as e:
                st.error(f"❌ Une erreur est survenue : {e}")

def extract_final_response(result):
    """
    Extrait uniquement le message final (celui après "VALIDATED FINAL RESPONSE")
    """
    result_str = str(result)
    
    # Cherche le pattern "VALIDATED FINAL RESPONSE — ready to copy-paste"
    match = re.search(r'VALIDATED FINAL RESPONSE.*?\n\n(.*?)(?:\n\n|$)', result_str, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # Si pas trouvé, cherche le dernier message dans tasks_output
    if hasattr(result, 'tasks_output') and result.tasks_output:
        last_task = result.tasks_output[-1]
        if hasattr(last_task, 'raw'):
            raw_content = last_task.raw
            match = re.search(r'VALIDATED FINAL RESPONSE.*?\n\n(.*?)(?:\n\n|$)', raw_content, re.DOTALL)
            if match:
                return match.group(1).strip()
            return raw_content
    
    return result_str
