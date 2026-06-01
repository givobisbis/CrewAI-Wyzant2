import streamlit as st
from wyzant_tutoring_response_generator.crew import WyzantTutoringResponseGeneratorCrew
import re

st.set_page_config(page_title="Wyzant Tutoring Response Generator", layout="wide")

st.title("🎓 Générateur de réponses Wyzant")
st.markdown("Génère automatiquement des réponses personnalisées pour les annonces de tutorat.")

def extract_final_message(result):
    """Extrait le message final du résultat"""
    result_str = str(result)
    
    # Cherche le message après "VALIDATED FINAL RESPONSE"
    patterns = [
        r'VALIDATED FINAL RESPONSE[^\n]*\n\n(.+?)(?=\n\n\*\*|\n\[|\n\n[ A-Z]+:)',
        r'\*\*VALIDATED FINAL RESPONSE.*?\*\*\n\n(.+?)(?=\n\n\*\*|\n\[)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, result_str, re.DOTALL)
        if match:
            text = match.group(1)
            text = text.replace('\\n', '\n').replace('\\"', '"')
            # Nettoie les caractères parasites
            lines = text.split('\n')
            cleaned = []
            for line in lines:
                if not line.startswith('```') and not line.startswith('{'):
                    cleaned.append(line.strip())
            return '\n'.join(cleaned).strip()
    
    # Si pas trouvé, prend le dernier task_output
    if hasattr(result, 'tasks_output') and result.tasks_output:
        last = result.tasks_output[-1]
        if hasattr(last, 'raw'):
            raw = last.raw
            # Cherche le bloc de réponse
            if 'VALIDATED FINAL RESPONSE' in raw:
                parts = raw.split('VALIDATED FINAL RESPONSE')
                if len(parts) > 1:
                    msg = parts[1].split('```')[0].split('\n\n**')[0]
                    msg = msg.replace('\\n', '\n').strip()
                    return msg
            return raw
    
    return "Message non trouvé"

ad_text = st.text_area(
    "📝 Texte de l'annonce",
    placeholder="Collez ici le texte de l'annonce du tuteur...",
    height=150
)

if st.button("🚀 Générer la réponse", type="primary"):
    if not ad_text.strip():
        st.error("Veuillez entrer le texte de l'annonce.")
    else:
        with st.spinner("L'agent CrewAI travaille... ⏳ (30 secondes environ)"):
            try:
                inputs = {'ad_text': ad_text}
                result = WyzantTutoringResponseGeneratorCrew().crew().kickoff(inputs=inputs)
                
                final_message = extract_final_message(result)
                
                st.success("✅ Réponse générée !")
                
                # Afficher le message final
                st.markdown("### 💬 Réponse proposée")
                st.markdown(f'<div style="background-color:#f0f2f6; padding:20px; border-radius:10px; font-size:16px;">{final_message}</div>', unsafe_allow_html=True)
                
                # Option copier
                with st.expander("📋 Cliquez pour copier le texte"):
                    st.code(final_message, language="text")
                
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ Erreur : {e}")
