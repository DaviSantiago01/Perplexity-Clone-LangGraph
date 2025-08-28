# 📋 schemas.py - Documentação Técnica

## Visão Geral

O arquivo `schemas.py` define as **estruturas de dados** fundamentais do sistema usando **Pydantic**. Estes modelos garantem validação de tipos, serialização consistente e documentação automática dos dados que fluem através do workflow LangGraph.

**🚀 Atualização**: Schemas otimizados para integração com Groq LLMs e código completamente documentado com comentários detalhados.

## 🎯 Propósito dos Schemas

### Por que usar Pydantic?

1. **Validação Automática**: Garante que dados estejam no formato correto
2. **Type Safety**: Previne erros de tipo em tempo de execução
3. **Serialização**: Conversão automática para JSON/dict
4. **Documentação**: Auto-documentação dos modelos
5. **IDE Support**: Melhor autocomplete e detecção de erros

## 📊 Modelos Definidos

### 1. `QueryResult`

```python
class QueryResult(BaseModel):
    title: str
    url: str
    summary: str
```

#### Propósito
Representa o **resultado de uma pesquisa individual** após processamento pelo nó `single_search`.

#### Campos Detalhados

| Campo | Tipo | Descrição | Exemplo |
|-------|------|-----------|----------|
| `title` | `str` | Título da página/artigo encontrado | "Inteligência Artificial - Wikipedia" |
| `url` | `str` | URL completa da fonte | "https://pt.wikipedia.org/wiki/Inteligência_artificial" |
| `summary` | `str` | Resumo gerado pelo LLM do conteúdo | "IA é a capacidade de máquinas simularem..." |

#### Fluxo de Criação

```python
# No nó single_search
results = tavily_client.search(query, max_results=1)

for result in results:
    # Extração de dados brutos
    title = result.get('title', 'Sem título')
    url = result.get('url', 'Sem URL')
    content = result.get('content', 'Sem conteúdo')
    
    # Processamento via LLM Groq (ultrarrápido)
    summary_response = llm.invoke(resume_prompt + content)
    summary = summary_response.content
    
    # Criação do objeto validado
    query_result = QueryResult(
        title=title,
        url=url,
        summary=summary
    )
```

#### Validações Automáticas

- **title**: Deve ser string não-vazia
- **url**: Deve ser string (validação de URL pode ser adicionada)
- **summary**: Deve ser string não-vazia

#### Uso no Sistema

1. **Criação**: No nó `single_search` após processar resultado Tavily
2. **Armazenamento**: Adicionado à lista `query_results` no estado
3. **Consumo**: Usado no nó `final_write` para gerar resposta final

### 2. `ReportState`

```python
class ReportState(TypedDict):
    user_input: str
    final_response: str
    queries: List[str]
    query_results: List[QueryResult]
```

#### Propósito
Define o **estado compartilhado** que flui através de todos os nós do LangGraph. É o "cérebro" que mantém todas as informações durante o processamento.

#### Campos Detalhados

| Campo | Tipo | Descrição | Momento de Criação |
|-------|------|-----------|--------------------|
| `user_input` | `str` | Pergunta original do usuário | Início do workflow |
| `final_response` | `str` | Resposta final compilada | Nó `final_write` |
| `queries` | `List[str]` | Lista de queries de pesquisa | Nó `build_first_queries` |
| `query_results` | `List[QueryResult]` | Resultados processados | Nós `single_search` |

#### Evolução do Estado

```python
# Estado inicial
state = {
    "user_input": "Como funciona a inteligência artificial?",
    "final_response": "",
    "queries": [],
    "query_results": []
}

# Após build_first_queries
state = {
    "user_input": "Como funciona a inteligência artificial?",
    "final_response": "",
    "queries": [
        "definição inteligência artificial",
        "algoritmos machine learning",
        "aplicações práticas IA"
    ],
    "query_results": []
}

# Após single_search (executado 3x em paralelo)
state = {
    "user_input": "Como funciona a inteligência artificial?",
    "final_response": "",
    "queries": [...],
    "query_results": [
        QueryResult(title="IA - Wikipedia", url="...", summary="..."),
        QueryResult(title="ML Algorithms", url="...", summary="..."),
        QueryResult(title="AI Applications", url="...", summary="...")
    ]
}

# Após final_write
state = {
    "user_input": "Como funciona a inteligência artificial?",
    "final_response": "A inteligência artificial é...",
    "queries": [...],
    "query_results": [...]
}
```

## 🔄 Integração com LangGraph

### TypedDict vs BaseModel

**Por que `ReportState` usa `TypedDict`?**

- **LangGraph Requirement**: LangGraph espera `TypedDict` para estados
- **Performance**: Mais leve que classes Pydantic
- **Flexibilidade**: Permite modificações dinâmicas

**Por que `QueryResult` usa `BaseModel`?**

- **Validação**: Dados externos (Tavily) precisam de validação
- **Métodos**: Acesso a métodos Pydantic (`.dict()`, `.json()`)
- **Serialização**: Fácil conversão para diferentes formatos

### Fluxo de Dados

```mermaid
graph TD
    A[user_input: str] --> B[build_first_queries]
    B --> C[queries: List[str]]
    C --> D[single_search]
    D --> E[QueryResult objects]
    E --> F[query_results: List[QueryResult]]
    F --> G[final_write]
    G --> H[final_response: str]
```

## 🛡️ Validação e Tratamento de Erros

### Validação Automática

```python
# Exemplo de validação automática
try:
    result = QueryResult(
        title="",  # String vazia - pode causar problemas
        url="invalid-url",  # URL inválida
        summary=None  # Tipo incorreto
    )
except ValidationError as e:
    print(f"Erro de validação: {e}")
```

### Tratamento de Dados Ausentes

```python
# No single_search - tratamento defensivo
title = result.get('title', 'Sem título')
url = result.get('url', 'Sem URL')
content = result.get('content', 'Sem conteúdo')

# Validação adicional
if not content or content == 'Sem conteúdo':
    summary = "Conteúdo não disponível para resumo"
else:
    summary_response = llm.invoke(resume_prompt + content)
    summary = summary_response.content or "Resumo não gerado"
```

## 🔧 Extensões e Melhorias

### Validações Customizadas

```python
from pydantic import validator, HttpUrl
from typing import Optional

class QueryResult(BaseModel):
    title: str
    url: HttpUrl  # Validação automática de URL
    summary: str
    confidence: Optional[float] = None  # Score de confiança
    
    @validator('title')
    def title_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Título não pode estar vazio')
        return v.strip()
    
    @validator('summary')
    def summary_min_length(cls, v):
        if len(v) < 10:
            raise ValueError('Resumo deve ter pelo menos 10 caracteres')
        return v
    
    @validator('confidence')
    def confidence_range(cls, v):
        if v is not None and (v < 0 or v > 1):
            raise ValueError('Confiança deve estar entre 0 e 1')
        return v
```

### Campos Adicionais

```python
from datetime import datetime
from enum import Enum

class SourceType(str, Enum):
    ACADEMIC = "academic"
    NEWS = "news"
    BLOG = "blog"
    WIKI = "wiki"
    OTHER = "other"

class EnhancedQueryResult(BaseModel):
    title: str
    url: HttpUrl
    summary: str
    source_type: SourceType
    relevance_score: float
    extracted_at: datetime = datetime.now()
    word_count: int
    language: str = "pt"
    
    class Config:
        use_enum_values = True  # Serializa enums como valores
```

### Estado Estendido

```python
from typing import Optional, Dict, Any

class ExtendedReportState(TypedDict):
    # Campos originais
    user_input: str
    final_response: str
    queries: List[str]
    query_results: List[QueryResult]
    
    # Campos adicionais
    session_id: Optional[str]
    processing_time: Optional[float]
    error_messages: List[str]
    metadata: Dict[str, Any]
    language: str
    search_depth: int
```

## 📊 Serialização e Persistência

### Conversão para JSON

```python
# QueryResult para JSON
result = QueryResult(
    title="Exemplo",
    url="https://example.com",
    summary="Resumo do exemplo"
)

# Serialização
json_data = result.json()
dict_data = result.dict()

# Deserialização
result_from_json = QueryResult.parse_raw(json_data)
result_from_dict = QueryResult(**dict_data)
```

### Salvamento de Estado

```python
import json
from typing import List

def save_state(state: ReportState, filename: str):
    """Salva estado em arquivo JSON"""
    # Converter QueryResult objects para dicts
    serializable_state = {
        "user_input": state["user_input"],
        "final_response": state["final_response"],
        "queries": state["queries"],
        "query_results": [result.dict() for result in state["query_results"]]
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(serializable_state, f, ensure_ascii=False, indent=2)

def load_state(filename: str) -> ReportState:
    """Carrega estado de arquivo JSON"""
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Reconstruir QueryResult objects
    query_results = [QueryResult(**result) for result in data["query_results"]]
    
    return ReportState(
        user_input=data["user_input"],
        final_response=data["final_response"],
        queries=data["queries"],
        query_results=query_results
    )
```

## 🧪 Testes e Validação

### Testes Unitários

```python
import pytest
from pydantic import ValidationError

def test_query_result_creation():
    """Testa criação válida de QueryResult"""
    result = QueryResult(
        title="Teste",
        url="https://example.com",
        summary="Resumo de teste"
    )
    assert result.title == "Teste"
    assert str(result.url) == "https://example.com"
    assert result.summary == "Resumo de teste"

def test_query_result_validation():
    """Testa validação de dados inválidos"""
    with pytest.raises(ValidationError):
        QueryResult(
            title="",  # Título vazio
            url="invalid-url",  # URL inválida
            summary=""  # Resumo vazio
        )

def test_state_evolution():
    """Testa evolução do estado"""
    state = ReportState(
        user_input="Teste",
        final_response="",
        queries=[],
        query_results=[]
    )
    
    # Adicionar queries
    state["queries"] = ["query1", "query2"]
    assert len(state["queries"]) == 2
    
    # Adicionar resultados
    result = QueryResult(title="T", url="https://ex.com", summary="S")
    state["query_results"].append(result)
    assert len(state["query_results"]) == 1
```

## 📈 Performance e Otimização

### Uso de Memória (com Groq)

- **QueryResult**: ~200-500 bytes por objeto
- **ReportState**: ~1-5KB dependendo do número de resultados
- **Serialização**: JSON compacto para persistência
- **Vantagem Groq**: Sem overhead de modelos locais, menor uso de RAM

### Otimizações

```python
# Usar __slots__ para reduzir uso de memória
class OptimizedQueryResult(BaseModel):
    title: str
    url: str
    summary: str
    
    class Config:
        # Otimizações Pydantic
        allow_reuse=True
        validate_assignment=False  # Desabilita validação em atribuições
        copy_on_model_validation=False  # Evita cópias desnecessárias
```

Os schemas definidos neste arquivo são fundamentais para manter a integridade e consistência dos dados em todo o sistema, proporcionando uma base sólida para o workflow complexo do LangGraph.