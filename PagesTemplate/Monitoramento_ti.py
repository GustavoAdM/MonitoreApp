import streamlit as st
import subprocess
import platform
import re
from streamlit_autorefresh import st_autorefresh

def ping_uma_vez(ip: str):
    sistema = platform.system()

    if sistema == "Windows":
        comando = ["ping", "-n", "1", "-l", "1", ip]
        regex = re.compile(r'tempo[=<](\d+)\s*ms|time[=<](\d+)\s*ms')
    else:
        comando = ["ping", "-c", "1", "-s", "1", ip]
        regex = re.compile(r'time[=<]?(\d+(?:\.\d+)?)\s*ms')

    processo = None  # Variável para armazenar o objeto Popen

    try:
        processo = subprocess.Popen(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = processo.communicate(timeout=2)
        for linha in stdout.splitlines():
            match = regex.search(linha)
            if match:
                return float(match.group(1) or match.group(2))
    except subprocess.TimeoutExpired:
        if processo:
            processo.terminate()  # Envia um sinal de término (SIGTERM)
            processo.wait()   
        return None
    except FileNotFoundError:
        print(f"Erro: O comando 'ping' não foi encontrado no sistema.")
        return None
    except Exception as e:
        print(f"Ocorreu um erro ao executar o ping: {e}")
        return None
    finally:
        if processo and processo.returncode is None:
            processo.terminate()
            processo.wait()

    return None

def monitoramento_ti():
    if "tempo_atualizar" not in st.session_state:
        st.session_state.tempo_atualizar = 36000

    st_autorefresh(interval=2100, key="ATUALIZAR_PING", limit=st.session_state.tempo_atualizar)
    st.html(
        """
        <style>
        .stElementContainer.element-container.st-key-ATUALIZAR_PING {
            display: None;
        }
        .stVerticalBlock > div:nth-child(3) {
            display: none;
        }
        </style>
        """
    )

    # --- Streamlit App ---
    st.title("Monitoramento de Rede")
    st.info("Eixo Y: Tempo de resposta (ms) — servidor 10.0.10.25 || Eixo X: Tempo decorrido (s) — intervalo de 30 segundos")

    with st.sidebar:
        col1, col2 = st.columns(2)

        with col1:
            if st.button("Parar Ping"):
                st.session_state.tempo_atualizar = 1
        with col2:
            if st.button("Reiniciar Ping"):
                st.session_state.ping_lista.clear()
                st.session_state.tempo_atualizar = 36000

        st.warning("""
        Buscar IP No Windwos: \n
        - for /f "tokens=2 delims=:" %i in ('ipconfig ^| findstr "IPv4"') do @echo %i
        
        Buscar IP Linux: \n
        - hostname -I | awk '{print $1}' """)

    ip = st.text_input("Endereço IP ou hostname:", None)
         
    # Inicializa a lista na sessão
    if "ping_lista" not in st.session_state:
        st.session_state.ping_lista = []

    if ip:

        tempo = ping_uma_vez(ip)
        if tempo is not None:
            st.session_state.ping_lista.append(tempo)
            if len(st.session_state.ping_lista) >= 31:
                st.session_state.ping_lista.pop(0)
        else:
            st.warning("Sem resposta ou erro no ping") 

        if st.session_state.ping_lista:
            st.line_chart(st.session_state.ping_lista)