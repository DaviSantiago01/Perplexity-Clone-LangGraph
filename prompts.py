# ============================================================================
# TEMPLATES DE PROMPTS PARA O SISTEMA DE PESQUISA INTELIGENTE
# ============================================================================
# Prompts otimizados para reduzir uso de tokens e melhorar qualidade das respostas
# Cada prompt tem função específica no pipeline de pesquisa e síntese
# ============================================================================

# ============================================================================
# PROMPT DO AGENTE PRINCIPAL
# ============================================================================
# Prompt base para orientar o comportamento geral do assistente
# Mantido simples para reduzir overhead de tokens
# ============================================================================
agent_prompt = """
You are a research assistant. Answer technical questions using current information.

User question: {user_input}
"""

# ============================================================================
# GERAÇÃO DE QUERIES DE PESQUISA
# ============================================================================
# Prompt para criar múltiplas queries otimizadas que cobrem diferentes
# aspectos da pergunta original, maximizando a cobertura de informações
# ============================================================================
build_queries = agent_prompt + """
Create 3-5 search queries to answer this question.
"""

# ============================================================================
# RESUMO DE RESULTADOS DE PESQUISA
# ============================================================================
# Prompt para processar conteúdo bruto da web e criar resumos focados
# Limite de 200 palavras para controle de tokens na síntese final
# ============================================================================
resume_search = """
Summarize this content focusing only on information relevant to: {user_input}

Content: {search_results}

Provide a concise summary (max 200 words):
"""

# ============================================================================
# SÍNTESE FINAL DE RESPOSTA
# ============================================================================
# Prompt para combinar todos os resumos em uma resposta coerente e abrangente
# Limite de 400-600 palavras para resposta completa mas controlada
# ============================================================================
build_final_response = """
Answer this question using the search results: {user_input}

Search results:
{search_results}

Provide a comprehensive answer (400-600 words) with numbered citations [1], [2], etc.
"""