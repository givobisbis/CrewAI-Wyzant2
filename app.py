import streamlit as st
from wyzant_tutoring_response_generator.crew import WyzantTutoringResponseGeneratorCrew

st.set_page_config(page_title="Wyzant Tutoring Response Generator", layout="centered")

st.title("🎓 Générateur de réponses Wyzant")
st.markdown("Génère automatiquement des réponses personnalisées pour les annonces de tutorat.")

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
                
                # Afficher le résultat du dernier agent (Quality Controller)
                if hasattr(result, 'tasks_output') and result.tasks_output:
                    dernier_agent = result.tasks_output[-1]
                    if hasattr(dernier_agent, 'raw'):
                        contenu = dernier_agent.raw
                        
                        # Nettoyer les caractères d'échappement
                        contenu = contenu.replace('\\n', '\n')
                        
                        # Afficher dans une zone de texte propre
                        st.success("✅ Réponse générée !")
                        st.text_area("📋 Résultat complet (prêt à copier-coller)", contenu, height=500)
                    else:
                        st.write(result)
                else:
                    st.write(result)
                
            except Exception as e:
                st.error(f"❌ Erreur : {e}")
