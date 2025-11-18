# Clone Perplexity - Motor de Busca Inteligente

> Sistema de busca que combina IA generativa com pesquisa web em tempo real

---

## 📋 Sobre

Motor de busca que transforma perguntas em pesquisas paralelas, sintetizando informações em respostas completas com citações automáticas.

**Principais recursos:**
- 🔄 Busca paralela em múltiplas fontes
- ⚡ Duas LLMs: GPT-20B (queries + resumos) e GPT-120B (síntese final)
- 💾 Estado persistente (LangGraph v1.0)
- 📚 Citações automáticas

---

## ⚙️ Instalação

```bash
git clone https://github.com/DaviSantiago01/perplexity-clone.git
cd perplexity-clone

python -m venv venv 

# Linux/Mac:
source venv/bin/activate

# Windows (CMD):
venv\Scripts\activate.bat

# Windows (PowerShell):
venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

**Configure suas APIs** (gratuitas): [Groq](https://console.groq.com/keys) • [Tavily](https://tavily.com/#api)

```bash
# Crie .env
GROQ_API_KEY=sua_chave
TAVILY_API_KEY=sua_chave
```

---

## 🚀 Uso

```bash
# CLI
python main.py

# Web UI
streamlit run app.py
```

---

## 📁 Estrutura

```
perplexity-clone/
├── main.py              # CLI
├── app.py               # Streamlit UI
└── src/
    ├── config.py        # Configurações
    ├── models.py        # TypedDict
    ├── prompts.py       # Templates
    ├── graph.py         # LangGraph workflow
    └── services.py      # Groq + Tavily
```

---

## 🏗️ Como Funciona

```mermaid
flowchart TB
    A[📝 Pergunta] --> B[🔍 Gera Queries]
    B --> |GPT-20B: 3-5 queries| C[🌐 Busca Paralela]
    
    C --> C1[Tavily 1]
    C --> C2[Tavily 2]
    C --> C3[Tavily 3]
    
    C1 --> D[📄 Resumo]
    C2 --> D
    C3 --> D
    
    D --> |GPT-20B| E[📊 Consolida]
    E --> |GPT-120B| F[🧠 Síntese]
    F --> G[✅ Resposta + Fontes]
```

**Fluxo:** Pergunta → Queries (20B) → Busca Paralela → Resumos (20B) → Síntese (120B) → Resposta

---

## 💡 Exemplo

**Input:** `"Como fazer café expresso?"`

**Processamento:**

```mermaid
flowchart LR 
    A["☕ Como fazer café expresso?"] --> B["🔍 GPT-20B gera queries"]
    
    B --> C1["temperatura água café"]
    B --> C2["moagem grãos expresso"]
    B --> C3["tempo extração"]
    
    C1 --> D1["🌐 Tavily busca 1"]
    C2 --> D2["🌐 Tavily busca 2"]
    C3 --> D3["🌐 Tavily busca 3"]
    
    D1 --> E1["📄 Resumo: 90-96°C"]
    D2 --> E2["📄 Resumo: moagem fina"]
    D3 --> E3["📄 Resumo: 25-30 seg"]
    
    E1 --> F["🧠 GPT-120B sintetiza tudo"]
    E2 --> F
    E3 --> F
    
    F --> G["✅ Resposta completa + fontes"]
```

1. Sistema gera 3 queries otimizadas
2. Busca paralela em cada uma
3. Resume resultados individuais (GPT-20B)
4. Sintetiza resposta completa (GPT-120B)

**Output:**
```
Para café expresso perfeito:
- Moagem fina e uniforme [1]
- Água a 90-96°C [2]
- Dose: 18-20g de café
- Extração: 25-30 segundos [3]

Resultado: crema dourada e sabor equilibrado.

[1] barista-institute.com/guia-expresso
[2] coffeeresearch.org/temperature
[3] specialtycoffee.com/timing
```

---

---

## Créditos

Projeto inspirado no tutorial da [Asimov Academy](https://www.youtube.com/@AsimovAcademy). Vídeo original: [Crie um Clone do Perplexity AI com LangGraph](https://www.youtube.com/watch?v=q2XPEjQ4Yt0). Esta versão foi atualizada para LangGraph v1.0 e LangChain v1.0.