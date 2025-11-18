## Pontos Principais do LangGraph

**1. Estado (State)**
- Compartilhado entre todos os nós
- Define estrutura de dados do fluxo
- Usa `TypedDict` para validação

**2. Nós (Nodes)**
- Funções que processam o estado
- Recebem estado → retornam atualizações
- Executam lógica isolada

**3. Grafo (Graph)**
- Define fluxo entre nós
- `StateGraph` conecta nós com edges
- Suporta fluxos condicionais e paralelos

**4. Edges (Arestas)**
- `add_edge`: fluxo direto A → B
- `add_conditional_edges`: decisões (if/else)
- Fan-out/fan-in: paralelização

**5. Checkpointing**
- Persistência automática do estado
- Permite pausar/retomar execução
- Human-in-the-loop

**6. Compilação**
- `workflow.compile()` gera executor
- Otimiza o grafo para execução
- Valida fluxo antes de rodar

**Diferencial**: Controle total sobre fluxo de execução, diferente de chains lineares do LangChain.