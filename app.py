import streamlit as st
import music21
from music21 import stream, note, chord, meter, key, tempo
import io
import base64
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os

st.set_page_config(page_title="Track to Track AI", layout="wide")

st.title("🎵 Track to Track AI")
st.markdown("---")

# Sidebar API Key
with st.sidebar:
    st.header("🔑 Configuração")
    api_key = st.text_input("OpenAI API Key", type="password", 
                           help="Insira sua chave da OpenAI (GPT-4o-mini)")
    st.info("💡 Gere em: https://platform.openai.com/api-keys")

# Estilos musicais
genres = [
    "Pop", "Rock", "EDM", "Hip-Hop", "Bossa Nova", "Gospel", 
    "Jazz", "Funk", "Samba", "Reggae", "Trap", "Lo-Fi", 
    "Country", "R&B", "Disco", "Techno", "House", "Drum n Bass",
    "Worship", "Forró", "Sertanejo", "Axé"
]

# Main interface
col1, col2 = st.columns([1, 1])

with col1:
    st.header("🎛️ Parâmetros")
    selected_genre = st.multiselect("Estilos", genres, default=["Pop", "Gospel"])[0]
    bpm = st.slider("BPM", 60, 180, 120)
    scale = st.selectbox("Escala", ["C Major", "G Major", "D Major", "A Major", "E Major"])
    bars = st.slider("Compassos", 4, 16, 8)
    
    section = st.selectbox("Seção", ["Intro", "Verso", "Refrão"])

with col2:
    st.header("🎼 Preview")
    if 'preview_score' in st.session_state:
        st.write(f"**{st.session_state.preview_score.metadata.get('title', 'Preview')}**")
        st.write(f"BPM: {st.session_state.preview_score.metadata.get('bpm', bpm)}")
        st.write(f"Escala: {st.session_state.preview_score.metadata.get('scale', scale)}")
        st.write(f"Barras: {len(st.session_state.preview_score.parts[0].getElementsByClass('Measure'))}")

# Generate button
if st.button("🎨 **GERAR TRILHA MIDI**", type="primary"):
    if not api_key:
        st.error("❌ Insira sua OpenAI API Key!")
    else:
        with st.spinner("🤖 Gerando com IA..."):
            try:
                # Configurar LLM
                llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key, temperature=0.7)
                
                # Prompt para estrutura musical
                prompt = PromptTemplate(
                    input_variables=["genre", "section", "bpm", "scale"],
                    template="Crie uma estrutura musical simples em {section} no estilo {genre}. "
                           "Use BPM {bpm}, escala {scale}. Sugira progressão de acordes "
                           "e melodia principal (notas C4 a C6). Formato: Acordes | Melodia"
                )
                
                chain = LLMChain(llm=llm, prompt=prompt)
                musical_idea = chain.run(genre=selected_genre, section=section, 
                                       bpm=bpm, scale=scale)
                
                st.session_state.musical_idea = musical_idea
                
                # Gerar MIDI com music21
                score = create_midi_track(selected_genre, section, bpm, scale, bars)
                score.metadata['title'] = f"{selected_genre} - {section}"
                score.metadata['bpm'] = bpm
                score.metadata['scale'] = scale
                
                st.session_state.preview_score = score
                
                # Download
                midi_buffer = io.BytesIO()
                score.write('midi', fp=midi_buffer)
                midi_buffer.seek(0)
                
                b64 = base64.b64encode(midi_buffer.read()).decode()
                href = f'<a href="data:audio/midi;base64,{b64}" download="{selected_genre}_{section.lower()}.mid">📥 Download MIDI</a>'
                st.markdown(href, unsafe_allow_html=True)
                
                st.success("✅ Trilha gerada com sucesso!")
                st.text_area("💡 Ideia da IA:", musical_idea, height=100)
                
            except Exception as e:
                st.error(f"❌ Erro: {str(e)}")
                st.info("💡 Verifique sua API Key e conexão.")

def create_midi_track(genre, section, bpm, scale_name, bars):
    """Gera trilha MIDI com music21"""
    s = stream.Score()
    s.append(meter.TimeSignature('4/4'))
    
    # Escala
    scale_map = {
        "C Major": "C major",
        "G Major": "G major",
        "D Major": "D major"
    }
    k = key.Key(scale_map.get(scale_name, "C major"))
    s.append(k)
    
    s.append(tempo.MetronomeMark(number=bpm))
    
    # Pista principal
    p1 = stream.Part()
    
    # Progressão de acordes por gênero
    chord_progressions = {
        "Pop": [["C", "E", "G"], ["F", "A", "C"], ["G", "B", "D"], ["C", "E", "G"]],
        "Gospel": [["C", "E", "G"], ["F", "A", "C"], ["G", "B", "D"], ["Am", "C", "F", "G"]],
        "Rock": [["G", "B", "D"], ["D", "F#", "A"], ["Em", "G", "B"], ["C", "E", "G"]],
        "Bossa Nova": [["Am7", "Dm7", "G7", "Cmaj7"]],
        "EDM": [["C", "E", "G"], ["Am", "C", "Em", "G"]]
    }
    
    progression = chord_progressions.get(genre, [["C", "F", "G", "C"]])
    
    for bar in range(bars):
        m = stream.Measure(number=bar+1)
        
        # Acorde
        chord_notes = progression[bar % len(progression)][0] if bar < len(progression) else "C"
        ch = chord.Chord(chord_notes)
        ch.duration.quarterLength = 4
        m.append(ch)
        
        # Melodia simples
        melody_notes = ["C4", "E4", "G4", "C5"] if "Major" in scale_name else ["C4", "Eb4", "G4", "Bb4"]
        n = note.Note(melody_notes[bar % len(melody_notes)])
        n.duration.quarterLength = 1
        m.append(n)
        
        p1.append(m)
    
    s.append(p1)
    return s

# Footer
st.markdown("---")
st.markdown("**Track to Track AI v1.0** | Feito com ❤️ para produtores brasileiros")
