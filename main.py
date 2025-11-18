"""
Clone Perplexity
Fluxo: Pergunta -> Gera queries de pesquisa -> Busca paralela na web -> Resposta Final
"""

import os
from typing import TypedDict, List
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
import config

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    
FAST_MODEL = "openai/gpt-oss-20b"     
REASONING_MODEL = "openai/gpt-oss-120b"
    
MAX_QUERIES = 3  
MAX_RESULTS_PER_QUERY = 2
    
TEMP_FAST = 0.3
TEMP_REASONING = 0.7

class EstadoPesquisa(TypedDict):
    """Estado compartilhado entre os nós do grafo"""
    pergunta_original: str
    queries_geradas: List[str]
    resultados_busca: List[dict]
    resposta_final: str
    erro: str