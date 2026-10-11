import os
import json
from pathlib import Path
import streamlit as st
import google.generativeai as genai

# ==============================================================================
# CONFIGURAÇÃO DA PÁGINA STREAMLIT
# ==============================================================================
st.set_page_config(
    page_title="NutriBot | Assistente Nutricional",
    page_icon="🥗",
    layout="centered"
)

# Caminho para a base de conhecimento local
DATASET_PATH = Path(__file__).parent / "dados_alimentacao.json"


# ==============================================================================
# FUNÇÕES UTILITÁRIAS E DE CARREGAMENTO DE DADOS
# ==============================================================================
@st.cache_data(show_spinner=False)
def carregar_base_conhecimento(caminho: Path) -> tuple[str, bool]:
    """
    Carrega o arquivo JSON local e o formata em string para injeção de contexto.
    Retorna uma tupla: (conteudo_formatado, sucesso)
    """
    if not caminho.exists():
        return (
            f"Erro: O arquivo de conhecimento '{caminho.name}' não foi encontrado.",
            False
        )

    try:
        with open(caminho, "r", encoding="utf-8") as f:
            dados = json.load(f)
            # Converte em JSON formatado com indentação para legibilidade do modelo
            conteudo_formatado = json.dumps(dados, ensure_ascii=False, indent=2)
            return conteudo_formatado, True
    except json.JSONDecodeError as err:
        return f"Erro de sintaxe no arquivo JSON: {str(err)}", False
    except Exception as err:
        return f"Erro inesperado ao ler a base de dados: {str(err)}", False


def obter_api_key() -> str:
    """
    Recupera a chave de API do Gemini a partir das variáveis de ambiente
    ou dos secrets do Streamlit.
    """
    # 1. Tenta pegar de variável de ambiente do sistema
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        return api_key.strip()

    # 2. Tenta pegar dos secrets nativos do Streamlit (.streamlit/secrets.toml)
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return str(st.secrets["GEMINI_API_KEY"]).strip()
    except Exception:
        pass

    return ""


def construir_system_instruction(contexto_json: str) -> str:
    """
    Monta as diretrizes do System Prompt garantindo o papel de especialista
    e ancoragem estrita (RAG fechado) na base de conhecimento.
    """
    return f"""Você é o NutriBot, um Especialista em Alimentação e Nutrição dedicado, acolhedor e altamente qualificado.

SUA MISSÃO E DIRETRIZES FUNDAMENTAIS:
1. Responda às dúvidas do usuário com empatia, clareza e tom profissional e motivador.
2. REQUISITO CRÍTICO DE EXCLUSIVIDADE: Baseie suas respostas ESTRITAMENTE e EXCLUSIVAMENTE nas informações contidas na Base de Conhecimento abaixo.
3. Se a informação solicitada pelo usuário NÃO estiver presente ou não puder ser confirmada diretamente pelos dados fornecidos, você DEVE responder educadamente informando que não possui essa informação em sua base de dados atual. Não invente, não especule e não utilize conhecimentos externos fora do contexto fornecido.
4. Organize as respostas de forma agradável utilizando tópicos, negritos e listas quando apropriado.

=== INÍCIO DA BASE DE CONHECIMENTO (JSON) ===
{contexto_json}
=== FIM DA BASE DE CONHECIMENTO ===
"""


def gerar_resposta_gemini(
    pergunta: str,
    historico: list[dict],
    system_instruction: str,
    api_key: str
) -> str:
    """
    Configura o modelo Gemini e gera a resposta considerando o contexto e histórico.
    """
    try:
        genai.configure(api_key=api_key)

        # Configura o modelo com as instruções do sistema
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=system_instruction,
            generation_config=genai.types.GenerationConfig(
                temperature=0.2  # Baixa temperatura para reduzir alucinações e manter fidelidade aos dados
            )
        )

        # Converte histórico para o formato aceito pelo SDK
        contents = []
        for msg in historico:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [msg["content"]]})

        # Adiciona a pergunta atual
        contents.append({"role": "user", "parts": [pergunta]})

        response = model.generate_content(contents)
        return response.text

    except Exception as e:
        return f"⚠️ Ocorreu um erro ao comunicar com a API do Gemini: {str(e)}"


# ==============================================================================
# INTERFACE DO USUÁRIO (STREAMLIT)
# ==============================================================================
def main():
    # Cabeçalho da Aplicação
    st.title("🥗 NutriBot — Especialista em Nutrição")
    st.markdown(
        """
        Olá! Sou seu assistente de nutrição inteligente. 
        Tire dúvidas sobre alimentos, macronutrientes, mitos alimentares e dicas saudáveis 
        consultando nossa base de conhecimento certificada.
        """
    )

    # 1. Verificação da Base de Conhecimento
    contexto_json, base_carregada_com_sucesso = carregar_base_conhecimento(DATASET_PATH)

    if not base_carregada_com_sucesso:
        st.error(f"❌ Falha crítica: {contexto_json}")
        st.info("Certifique-se de que o arquivo 'dados_alimentacao.json' está presente no mesmo diretório.")
        st.stop()

    # 2. Verificação da API Key
    api_key = obter_api_key()

    with st.sidebar:
        st.header("⚙️ Configurações")
        st.markdown("**Status da Conexão:**")
        if api_key:
            st.success("API Key detectada com sucesso! ✅")
        else:
            st.warning("API Key não encontrada no ambiente. ⚠️")
            api_key_manual = st.text_input(
                "Insira sua GEMINI_API_KEY aqui:",
                type="password",
                help="Obtenha sua chave no Google AI Studio (aistudio.google.com)"
            )
            if api_key_manual:
                api_key = api_key_manual.strip()

        st.divider()
        st.caption(f"📁 Base de dados: `{DATASET_PATH.name}`")
        if st.button("🗑️ Limpar Conversa"):
            st.session_state["messages"] = [
                {
                    "role": "assistant",
                    "content": "Olá! Sou o NutriBot. Em que posso te ajudar hoje sobre nutrição e alimentos?"
                }
            ]
            st.rerun()

    # Alerta visual em destaque caso a chave de API não esteja configurada
    if not api_key:
        st.error("🔑 **Atenção:** A chave de API do Google Gemini (`GEMINI_API_KEY`) não foi configurada.")
        st.info(
            "👉 Por favor, defina a variável de ambiente `GEMINI_API_KEY` no terminal ou "
            "insira sua chave no campo disponível no menu lateral à esquerda para começar."
        )
        st.stop()

    # 3. Gerenciamento do Histórico de Mensagens
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {
                "role": "assistant",
                "content": "Olá! Sou o NutriBot. Em que posso te ajudar hoje sobre nutrição e alimentos?"
            }
        ]

    # Exibição do histórico de mensagens no chat
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 4. Input do Usuário e Processamento
    if prompt := st.chat_input("Digite sua dúvida sobre alimentação e nutrição..."):
        # Exibe mensagem do usuário
        with st.chat_message("user"):
            st.markdown(prompt)

        # Prepara a instrução do sistema com o JSON injetado
        system_instruction = construir_system_instruction(contexto_json)

        # Gera e exibe a resposta do assistente
        with st.chat_message("assistant"):
            with st.spinner("Consultando base de conhecimento nutricional..."):
                resposta = gerar_resposta_gemini(
                    pergunta=prompt,
                    historico=st.session_state["messages"],
                    system_instruction=system_instruction,
                    api_key=api_key
                )
                st.markdown(resposta)

        # Salva as mensagens no histórico da sessão
        st.session_state["messages"].append({"role": "user", "content": prompt})
        st.session_state["messages"].append({"role": "assistant", "content": resposta})


if __name__ == "__main__":
    main()
