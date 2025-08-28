import operator
from typing_extensions import  Annotated
from typing import List

from pydantic import BaseModel


class QueryResult(BaseModel):
    title: str = None
    url: str = None
    resume: str = None

class ReportState(BaseModel):
    user_input: str = None
    final_response: str = None
    queries: List[str] = []
    queries_results: Annotated[List[QueryResult], operator.add]




