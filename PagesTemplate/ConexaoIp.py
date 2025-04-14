import streamlit as st
import streamlit.components.v1 as components


def capturar_ip():
    

    st.title("Capturando o IP Interno na Rede Local")

    components.html(
        """
        <script>
        async function getLocalIP() {
            return new Promise((resolve, reject) => {
                const pc = new RTCPeerConnection({iceServers: []});
                pc.createDataChannel("");
                pc.createOffer().then(offer => pc.setLocalDescription(offer)).catch(reject);
                pc.onicecandidate = (ice) => {
                    if (!ice || !ice.candidate || !ice.candidate.candidate) return;
                    const ipMatch = /([0-9]{1,3}(\\.[0-9]{1,3}){3})/.exec(ice.candidate.candidate);
                    if (ipMatch) {
                        resolve(ipMatch[1]);
                        pc.close();
                    }
                };
            });
        }

        getLocalIP().then(ip => {
            // Envia o IP para o Streamlit
            window.parent.postMessage({
                isStreamlitMessage: true,
                type: "streamlit:setComponentValue",
                value: ip
            }, "*");
        }).catch(error => {
            console.error("Erro ao capturar IP:", error);
        });
        </script>
        """,
        height=0,
    )

    # Captura o valor enviado do JavaScript
    st.write("Esperando o IP interno...")
