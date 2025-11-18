# 🏗️ Arquitetura MVP - Sistema de Busca Inteligente

## 📦 Estado Compartilhado (SearchState)

Estado único que flui entre todos os nós:

- **pergunta**: Query original do usuário
- **queries**: 3-5 queries de busca otimizadas
- **resultados_brutos**: Dados do Tavily acumulados (usa `operator.add`)
- **resumos**: Sínteses individuais de cada resultado
- **resposta_final**: Resposta formatada com citações numeradas

---

## 🔄 Nós do Grafo

### **1. gerar_queries**
- **Recebe**: `pergunta`
- **Processa**: GPT OSS 20b rápida
- **Retorna**: 3-5 queries otimizadas para busca paralela
- **Propósito**: Decompor pergunta complexa em buscas específicas

### **2. buscar_paralelo**
- **Recebe**: `queries`
- **Processa**: Tavily API em paralelo (fan-out)
- **Retorna**: Resultados brutos acumulados
- **Propósito**: Executar todas as buscas simultaneamente

### **3. resumir**
- **Recebe**: `resultados_brutos`
- **Processa**: GPT OSS 20B rápida para cada resultado
- **Retorna**: Lista de resumos concisos (2-3 frases cada)
- **Propósito**: Condensar informação antes da síntese final

### **4. sintetizar**
- **Recebe**: `pergunta` + `resumos` + `resultados_brutos`
- **Processa**: GPT OSS 120B potente
- **Retorna**: Resposta completa com fontes numeradas [1], [2]...
- **Propósito**: Gerar resposta coerente e bem fundamentada

---

## ⚡ Fluxo de Execução

```
START 
  ↓
gerar_queries (sequencial)
  ↓
buscar_paralelo (fan-out: 3-5 buscas simultâneas)
  ↓
resumir (sequencial: processa todos os resultados)
  ↓
sintetizar (sequencial)
  ↓
END
```

---

## 🎯 Melhorias Baseadas em LangGraph 2025

### **Padrão Fan-out/Fan-in Otimizado**
- Execução paralela real das buscas (Super-step único)
- Reducer `operator.add` evita conflitos de estado
- Aguarda todos os resultados antes de prosseguir

### **Dual LLM Strategy**
- **8B rápida**: Tarefas de decomposição e sumarização
- **70B potente**: Síntese final que exige raciocínio profundo
- Otimiza custo e latência

### **Estado Tipado e Mínimo**
- Apenas dados essenciais no estado
- Type safety com `TypedDict`
- Reducers explícitos para campos acumuláveis
