from pydantic import BaseModel #Biblioteca do langchain usada para identificar certinho o prompt
from typing import List #Para definir tipos de lista
import operator
from typing_extensions import Annotated

class QueryResult(BaseModel): #Resultado da pesquisa naquela url
 title: str = None #Título da página encontrada
 url: str = None #Link da página web
 resume: str = None #Resumo do conteúdo da página

class ReportState(BaseModel): #Vai armazenando todas as queries todos os dados de acordo com todas as pesquisas dos agentes
 user_input: str = None #Pergunta original do usuário
 final_response: str = None #Resposta final compilada pelo sistema
 queries: List[str] = [] #Lista com todas as consultas feitas pelos agentes
 queries_results: Annotated[List[QueryResult], operator.add] #Lista com todos os resultados das consultas