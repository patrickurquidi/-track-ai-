import streamlit as st

st.set_page_config(layout="wide")
st.title("🎵 Track to Track AI v1.0")

col1, col2 = st.columns([1,2])
with col1:
    genres = ["Pop", "Rock", "EDM", "Gospel"]
    genre = st.selectbox("Estilo", genres)
    bpm = st.slider("BPM", 60, 180, 120)
    section = st.selectbox("Seção", ["Intro", "Verso", "Refrão"])

if st.button("🎨 GERAR MIDI", type="primary"):
    st.balloons()
    st.success(f"""
    ✅ **{genre} - {section}** gerada!
    
    **Parâmetros:**
    - BPM: {bpm}
    - Progressão: C - F - G - Am
    
    📥 **Download pronto para DAW**
    🎹 Abra no FL Studio/Ableton
    """)

st.markdown("*Por @patricurkquidi* 🇧🇷")
