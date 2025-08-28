# 💬 prompts.py - Documentação Técnica

## Visão Geral

O arquivo `prompts.py` contém os **templates de prompts** que guiam o comportamento dos modelos de linguagem (LLMs) em cada etapa do workflow. Estes prompts são cuidadosamente elaborados para extrair o máximo desempenho dos modelos Ollama, definindo personalidades, contextos e formatos de saída específicos.

## 🎯 Importância dos Prompts

### Por que Prompts Bem Elaborados São Cruciais?

1. **Controle de Comportamento**: Definem como o LLM deve agir em cada situação
2. **Consistência**: Garantem respostas padronizadas e previsíveis
3. **Qualidade**: Melhoram a relevância e precisão das respostas
4. **Especialização**: Cada prompt é otimizado para uma tarefa específica
5. **Eficiência**: Reduzem a necessidade de múltiplas iterações

## 📝 Prompts Definidos

### 1. `agent_prompt`

```python
agent_prompt = """
Você é um planejador de pesquisa especializado. Sua tarefa é analisar perguntas dos usuários e criar estratégias de pesquisa eficazes.

Sua responsabilidade:
- Entender a intenção por trás da pergunta
- Identificar os aspectos-chave que precisam ser pesquisados
- Sugerir abordagens de pesquisa que cubram diferentes ângulos do tópico

Seja preciso, objetivo e estratégico em suas análises.
"""
```

#### Propósito
Define a **personalidade base** para o sistema - um especialista em planejamento de pesquisa.

#### Características do Prompt

- **Papel Definido**: "planejador de pesquisa especializado"
- **Responsabilidades Claras**: Lista específica de tarefas
- **Tom Profissional**: Linguagem formal e técnica
- **Diretrizes Comportamentais**: "preciso, objetivo e estratégico"

#### Uso no Sistema

Este prompt serve como **contexto base** que pode ser combinado com outros prompts mais específicos, estabelecendo a "personalidade" do assistente.

### 2. `build_queries`

```python
build_queries = """
Com base na pergunta do usuário, gere uma lista de 3-5 consultas de pesquisa específicas e diversificadas.

Cada consulta deve:
- Abordar um aspecto diferente da pergunta original
- Ser específica o suficiente para encontrar informações relevantes
- Usar palavras-chave estratégicas
- Cobrir diferentes perspectivas do tópico

Formato de saída: Uma lista simples, uma consulta por linha, sem numeração ou marcadores.

Exemplo:
Pergunta: "Como funciona a inteligência artificial?"
Saída:
definição inteligência artificial conceitos básicos
algoritmos machine learning redes neurais
aplicações práticas IA vida cotidiana
história desenvolvimento inteligência artificial
ética inteligência artificial impactos sociedade
"""
```

#### Propósito
Guia o LLM na **geração de múltiplas queries** de pesquisa a partir de uma pergunta única.

#### Análise Detalhada

**Estrutura do Prompt:**

1. **Instrução Principal**: "gere uma lista de 3-5 consultas"
2. **Critérios Específicos**: Lista de 4 requisitos para cada query
3. **Formato de Saída**: Especificação clara do formato esperado
4. **Exemplo Prático**: Demonstração concreta do resultado esperado

**Estratégia de Diversificação:**

- **Aspecto Conceitual**: "definição inteligência artificial conceitos básicos"
- **Aspecto Técnico**: "algoritmos machine learning redes neurais"
- **Aspecto Prático**: "aplicações práticas IA vida cotidiana"
- **Aspecto Histórico**: "história desenvolvimento inteligência artificial"
- **Aspecto Social**: "ética inteligência artificial impactos sociedade"

#### Uso no Workflow

```python
# No nó build_first_queries
full_prompt = agent_prompt + "\n\n" + build_queries + "\n\nPergunta: " + user_input
response = llm.invoke(full_prompt)
queries = response.content.strip().split('\n')
```

### 3. `resume_search`

```python
resume_search = """
Você é um especialista em análise e síntese de conteúdo web. Sua tarefa é criar um resumo conciso e informativo do conteúdo fornecido.

Diretrizes para o resumo:
- Extraia apenas as informações mais relevantes e importantes
- Mantenha o foco no tópico principal
- Use linguagem clara e objetiva
- Preserve dados específicos, números e fatos importantes
- Ignore informações irrelevantes como navegação, publicidade, etc.
- Limite o resumo a 2-3 parágrafos

Conteúdo para resumir:
"""
```

#### Propósito
Organiza o LLM para **resumir conteúdo web** extraído pela API Tavily.

#### Análise Detalhada

**Papel Especializado**: "especialista em análise e síntese de conteúdo web"

**Diretrizes Específicas:**

1. **Seletividade**: "apenas as informações mais relevantes"
2. **Foco**: "mantenha o foco no tópico principal"
3. **Clareza**: "linguagem clara e objetiva"
4. **Preservação**: "preserve dados específicos, números e fatos"
5. **Filtragem**: "ignore informações irrelevantes"
6. **Limitação**: "limite o resumo a 2-3 parágrafos"

#### Desafios Abordados

- **Ruído Web**: Filtra elementos de navegação e publicidade
- **Relevância**: Mantém foco no tópico da pesquisa
- **Concisão**: Evita resumos excessivamente longos
- **Qualidade**: Preserva informações factuais importantes

#### Uso no Workflow

```python
# No nó single_search
for result in results:
    content = result.get('content', 'Sem conteúdo')
    full_prompt = resume_search + content
    summary_response = llm.invoke(full_prompt)
    summary = summary_response.content
```

### 4. `build_final_response`

```python
build_final_response = """
Você é um especialista em síntese de informações e redação técnica. Sua tarefa é criar uma resposta abrangente e bem estruturada com base nos relatórios de pesquisa fornecidos.

Diretrizes para a resposta final:
- Sintetize todas as informações dos relatórios em uma resposta coerente
- Organize o conteúdo de forma lógica e fácil de entender
- Inclua informações específicas, dados e fatos relevantes
- Mantenha um tom informativo e profissional
- Cite as fontes usando o formato: [Título da Fonte](URL)
- Estruture a resposta com introdução, desenvolvimento e conclusão quando apropriado
- Responda diretamente à pergunta original do usuário

Relatórios de pesquisa:
"""
```

#### Propósito
Guia o LLM na **compilação final** de todos os resultados de pesquisa em uma resposta abrangente.

#### Análise Detalhada

**Papel Especializado**: "especialista em síntese de informações e redação técnica"

**Diretrizes Estruturais:**

1. **Síntese**: "sintetize todas as informações dos relatórios"
2. **Organização**: "organize o conteúdo de forma lógica"
3. **Especificidade**: "inclua informações específicas, dados e fatos"
4. **Tom**: "mantenha um tom informativo e profissional"
5. **Citações**: "cite as fontes usando o formato: [Título](URL)"
6. **Estrutura**: "introdução, desenvolvimento e conclusão"
7. **Relevância**: "responda diretamente à pergunta original"

#### Formato de Citação

```markdown
[Título da Fonte](URL)
```

Este formato permite:
- **Rastreabilidade**: Usuário pode verificar fontes
- **Credibilidade**: Transparência nas referências
- **Navegação**: Links clicáveis na interface

#### Uso no Workflow

```python
# No nó final_write
reports = "\n\n".join([
    f"Título: {result.title}\nURL: {result.url}\nResumo: {result.summary}"
    for result in state["query_results"]
])

full_prompt = (
    agent_prompt + "\n\n" + 
    build_final_response + "\n\n" + 
    reports + "\n\n" +
    f"Pergunta original: {state['user_input']}"
)

response = llm_reasoning.invoke(full_prompt)
```

## 🔧 Técnicas de Prompt Engineering

### 1. Estrutura Hierárquica

```
Contexto Geral (agent_prompt)
    ↓
Tarefa Específica (build_queries/resume_search/build_final_response)
    ↓
Dados de Entrada (pergunta/conteúdo/relatórios)
    ↓
Formato de Saída (especificações claras)
```

### 2. Técnicas Utilizadas

#### **Role Playing**
- "Você é um planejador de pesquisa especializado"
- "Você é um especialista em análise e síntese"

#### **Task Specification**
- Listas claras de responsabilidades
- Critérios específicos para cada tarefa

#### **Output Formatting**
- Especificação de formatos de saída
- Exemplos concretos

#### **Constraint Setting**
- Limitações de tamanho ("2-3 parágrafos")
- Diretrizes de qualidade

#### **Few-Shot Learning**
- Exemplos práticos no prompt `build_queries`

### 3. Otimizações para Ollama

#### **Clareza e Simplicidade**
```python
# ✅ Bom - Instrução clara
"Gere uma lista de 3-5 consultas de pesquisa"

# ❌ Ruim - Instrução ambígua
"Crie algumas queries relacionadas"
```

#### **Contexto Suficiente**
```python
# ✅ Bom - Contexto completo
agent_prompt + build_queries + user_input

# ❌ Ruim - Contexto insuficiente
build_queries + user_input
```

#### **Formato Estruturado**
```python
# ✅ Bom - Formato específico
"Formato: Uma lista simples, uma consulta por linha"

# ❌ Ruim - Formato vago
"Liste as consultas"
```

## 🚀 Extensões e Melhorias

### 1. Prompts Dinâmicos

```python
def build_dynamic_query_prompt(domain: str, complexity: str) -> str:
    """Gera prompt personalizado baseado no domínio"""
    base = build_queries
    
    if domain == "scientific":
        base += "\nFoque em termos técnicos e fontes acadêmicas."
    elif domain == "news":
        base += "\nPrioritize fontes jornalísticas recentes."
    
    if complexity == "beginner":
        base += "\nUse linguagem simples e conceitos básicos."
    elif complexity == "expert":
        base += "\nIncluir terminologia técnica avançada."
    
    return base
```

### 2. Prompts Multilíngues

```python
PROMPTS = {
    "pt": {
        "agent": "Você é um planejador de pesquisa especializado...",
        "queries": "Gere uma lista de 3-5 consultas..."
    },
    "en": {
        "agent": "You are a specialized research planner...",
        "queries": "Generate a list of 3-5 search queries..."
    }
}

def get_prompt(key: str, language: str = "pt") -> str:
    return PROMPTS[language][key]
```

### 3. Prompts com Validação

```python
validation_prompt = """
Antes de finalizar sua resposta, verifique se:
1. Todas as informações são factualmente corretas
2. As fontes estão devidamente citadas
3. A resposta está completa e bem estruturada
4. O tom é apropriado para o público-alvo

Se algum critério não for atendido, revise sua resposta.
"""
```

### 4. Prompts com Feedback Loop

```python
self_critique_prompt = """
Avalie sua resposta anterior considerando:
- Relevância para a pergunta original
- Completude das informações
- Qualidade das fontes citadas
- Clareza da explicação

Se necessário, sugira melhorias ou informações adicionais.
"""
```

## 📊 Métricas e Avaliação

### 1. Qualidade dos Prompts

```python
def evaluate_prompt_effectiveness(prompt: str, test_cases: List[str]) -> float:
    """Avalia eficácia do prompt com casos de teste"""
    scores = []
    for test_case in test_cases:
        response = llm.invoke(prompt + test_case)
        score = calculate_quality_score(response)
        scores.append(score)
    return sum(scores) / len(scores)
```

### 2. Métricas de Performance

- **Consistência**: Respostas similares para inputs similares
- **Relevância**: Aderência ao tópico solicitado
- **Completude**: Cobertura abrangente do assunto
- **Precisão**: Informações factualmente corretas
- **Clareza**: Facilidade de compreensão

## 🧪 Testes e Validação

### 1. Testes A/B de Prompts

```python
def ab_test_prompts(prompt_a: str, prompt_b: str, test_queries: List[str]):
    """Compara eficácia de dois prompts"""
    results_a = [llm.invoke(prompt_a + query) for query in test_queries]
    results_b = [llm.invoke(prompt_b + query) for query in test_queries]
    
    score_a = evaluate_responses(results_a)
    score_b = evaluate_responses(results_b)
    
    return {"prompt_a": score_a, "prompt_b": score_b}
```

### 2. Validação de Formato

```python
def validate_query_format(response: str) -> bool:
    """Valida se resposta segue formato esperado"""
    lines = response.strip().split('\n')
    
    # Verifica número de queries
    if not (3 <= len(lines) <= 5):
        return False
    
    # Verifica se não há numeração
    for line in lines:
        if line.strip().startswith(('1.', '2.', '-', '*')):
            return False
    
    return True
```

## 🎯 Melhores Práticas

### 1. Design de Prompts

- **Seja Específico**: Instruções claras e detalhadas
- **Use Exemplos**: Demonstre o formato esperado
- **Defina Papéis**: Estabeleça personalidade e expertise
- **Limite Escopo**: Evite ambiguidade
- **Teste Iterativamente**: Refine baseado em resultados

### 2. Manutenção

- **Versionamento**: Mantenha histórico de mudanças
- **Documentação**: Explique o propósito de cada prompt
- **Monitoramento**: Acompanhe performance em produção
- **Feedback**: Colete dados de usuários

### 3. Otimização

- **Tamanho**: Balance detalhamento com eficiência
- **Contexto**: Forneça informações suficientes
- **Consistência**: Mantenha estilo uniforme
- **Flexibilidade**: Permita adaptação para casos específicos

Os prompts definidos neste arquivo são fundamentais para o sucesso do sistema, atuando como a "interface de comunicação" entre as intenções humanas e as capacidades dos modelos de IA.