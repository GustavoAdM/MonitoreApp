import streamlit as st
from gtts import gTTS
import tempfile

def gerar_audio():
    # Configuração da página
    st.title("📖 Texto para Fala")
    st.write("Carregue um arquivo de texto e escute a narração!")

    # Upload do arquivo de texto
    uploaded_file = st.file_uploader("Escolha um arquivo de texto (.txt)", type=["txt"])

    if uploaded_file is not None:
        # Lê o conteúdo do arquivo
        text = uploaded_file.read().decode("utf-8")

        # Exibe o texto carregado
        st.text_area("Conteúdo do Arquivo", text, height=200)

        if st.button("Gerar Áudio"):
            # Converte o texto para fala
            tts = gTTS(text, lang="pt") 

            # Salva temporariamente o áudio
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
                tts.save(temp_audio.name)
                audio_path = temp_audio.name

            # Exibe o player de áudio
            st.audio(audio_path, format="audio/mp3")

            # Permite download do áudio
            with open(audio_path, "rb") as audio_file:
                st.download_button(
                    label="📥 Baixar Áudio",
                    data=audio_file,
                    file_name="audio_gerado.mp3",
                    mime="audio/mp3",
                )
