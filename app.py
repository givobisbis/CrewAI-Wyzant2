import streamlit as st
from wyzant_tutoring_response_generator.crew import WyzantTutoringResponseGeneratorCrew

st.set_page_config(page_title="Wyzant Tutoring Response Generator", layout="centered")

st.title("🎓 Générateur de réponses Wyzant")
st.markdown("Génère automatiquement des réponses personnalisées pour les annonces de tutorat.")

# Zone de saisie pour l'annonce
ad_text = st.text_area(
    "📝 Texte de l'annonce du tuteur",
    placeholder="Collez ici le texte de l'annonce du tuteur...",
    height=200
)

# Bouton pour lancer la génération
if st.button("🚀 Générer la réponse", type="primary"):
    if not ad_text.strip():
        st.error("Veuillez entrer le texte de l'annonce.")
    else:
        with st.spinner("L'agent CrewAI réfléchit... ⏳"):
            try:
                inputs = {'ad_text': ad_text}
                result = WyzantTutoringResponseGeneratorCrew().crew().kickoff(inputs=inputs)
                st.success("✅ Réponse générée !")
                st.markdown("### 📤 Réponse proposée :")
                st.write(result)
            except Exception as e:
                st.error(f"❌ Une erreur est survenue : {e}")
