# 🥗 NutriBot — Assistente Especialista em Nutrição & Alimentação

O **NutriBot** é um chatbot inteligente desenvolvido com **Python**, **Streamlit** e a **API do Google Gemini**. O sistema opera utilizando um arquivo JSON como base de conhecimento local em uma arquitetura RAG (*Retrieval-Augmented Generation*) simplificada, garantindo que o assistente responda de forma estrita e personalizada aos dados cadastrados, sem alucinações de informações externas.

---

## 📁 Estrutura do Projeto

```plaintext
chatbot/
│
├── dados_alimentacao.json    # Base de conhecimento local (alimentos, macronutrientes, mitos e dicas)
├── app.py                   # Aplicação principal (UI Streamlit + Integração Gemini RAG)
├── requirements.txt         # Dependências do projeto Python
└── README.md                # Documentação completa de instalação e execução
```

---

## 🚀 Tecnologias Utilizadas

- **Python 3.10+**
- **[Streamlit](https://streamlit.io/)**: Interface web reativa e amigável no formato de chat.
- **[Google Generative AI SDK](https://ai.google.dev/) (`google-generativeai`)**: Integração com a família de modelos Gemini (`gemini-1.5-flash`).
- **JSON**: Manipulação nativa de dados estruturados para injeção de contexto.

---

## ⚙️ Pré-requisitos e Instalação

### 1. Clonar ou Acessar a Pasta do Projeto

Abra o seu terminal na pasta do projeto:
```bash
cd caminho/para/chatbot
```

### 2. Criar e Ativar um Ambiente Virtual (Recomendado)

- **No Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```

- **No Linux / macOS:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Instalar as Dependências

```bash
pip install -r requirements.txt
```

---

## 🔑 Configuração da Chave de API do Google Gemini

Você precisará de uma chave de API gratuita do Gemini gerada no [Google AI Studio](https://aistudio.google.com/).

Você pode configurar a chave de duas maneiras:

### Opção 1: Variável de Ambiente (Recomendado)

- **No Windows (PowerShell):**
  ```powershell
  $env:GEMINI_API_KEY="SUA_CHAVE_AQUI"
  ```

- **No Windows (CMD):**
  ```cmd
  set GEMINI_API_KEY="SUA_CHAVE_AQUI"
  ```

- **No Linux / macOS:**
  ```bash
  export GEMINI_API_KEY="SUA_CHAVE_AQUI"
  ```

### Opção 2: Pela Própria Interface Gráfica
Se preferir, inicie o app e insira a chave no campo de senha da **barra lateral (sidebar)** do Streamlit.

---

## ▶️ Como Executar a Aplicação

Com o ambiente ativado e as dependências instaladas, execute:

```bash
streamlit run app.py
```

O Streamlit iniciará o servidor local e abrirá automaticamente no seu navegador no endereço `http://localhost:8501`.

---

## 🧪 Exemplos de Teste

1. **Perguntas com resposta na base:**
   - *"Quais são os benefícios da banana prata e suas calorias?"*
   - *"Comer carboidrato à noite realmente engorda mais?"*
   - *"Quanto de água devo beber por dia?"*
   - *"Quais alimentos são ricos em vitamina C?"*

2. **Perguntas fora da base (validação de fidelidade RAG):**
   - *"Qual é a tabela nutricional do queijo gorgonzola?"*
   - *O NutriBot responderá educadamente informando que não possui esses dados em sua base de conhecimento atual.*

---

## 🛡️ Tratamento de Erros e Boas Práticas

- **Tratamento de Arquivos Ausentes:** Caso `dados_alimentacao.json` não esteja presente ou corrompido, a UI exibirá um alerta visual explicativo impedindo falhas não tratadas.
- **Validação de Credencial:** Alerta em destaque no caso de ausência da chave `GEMINI_API_KEY`.
- **Temperatura Baixa (`temperature=0.2`):** Assegura respostas consistentes e determinísticas estritamente limitadas ao contexto fornecido.
- **Cache de Leitura:** O carregamento do arquivo JSON é otimizado com `@st.cache_data`.
