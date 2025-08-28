from langchain_core.messages import SystemMessage
from pydantic import BaseModel
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langgraph.graph import START, END, StateGraph
from langgraph.types import Send
from langgraph.checkpoint.memory import MemorySaver
from time import time
import streamlit as st

from schemas import *
from prompts import *
from utils import *

from dotenv import load_dotenv
load_dotenv()

# llm = ChatOpenAI(model="gpt-4o")
# llm = ChatOllama(model="llama3.2:latest")
# llm = ChatOllama(model="llama3.1:8b-instruct-q4_K_S")
llm = ChatOllama(model="llama3.1:8b-instruct-q4_K_S")
reasoning_llm = ChatOllama(model="deepseek-r1:8b")

def build_first_queries(state: ReportState): 
    class QueryList(BaseModel):
        queries: List[str]
        
    user_input = state.user_input

    prompt = build_queries.format(user_input=user_input)
    query_llm = llm.with_structured_output(QueryList)
    result = query_llm.invoke(prompt)

    return {"queries": result.queries}

def spawn_researchers(state: ReportState):
    return [Send("single_search", query) 
            for query in state.queries]

def single_search(query: str):
    tavily_client = TavilyClient()

    results = tavily_client.search(query, 
                         max_results=1, 
                         include_raw_content=False)

    query_results = []
    for result in results["results"]:
        url = result["url"]
        url_extraction = tavily_client.extract(url)

        # print(url_extraction)
        if len(url_extraction["results"]) > 0:
            raw_content = url_extraction["results"][0]["raw_content"]
            prompt = resume_search.format(user_input=user_input,
                                        search_results=raw_content)

            llm_result = llm.invoke(prompt)
            query_results += [QueryResult(query=result["title"],
                                    content=llm_result.content,
                                    sources=[url])]
    return {"queries_results": query_results}
    

def final_writer(state: ReportState):
    search_results = ""
    references = ""
    for i, result in enumerate(state.queries_results):
        search_results += f"[{i+1}]\n\n"
        search_results += f"Title: {result.query}\n"
        search_results += f"URL: {result.sources[0] if result.sources else '#'}\n"
        search_results += f"Content: {result.content}\n"
        search_results += f"================\n\n"

        source_url = result.sources[0] if result.sources else "#"
        references += f"[{i+1}] - [{result.query}]({source_url})\n"
    

    prompt = build_final_response.format(user_input=user_input,
                                    search_results=search_results)

  
    llm_result = reasoning_llm.invoke(prompt)

    print(llm_result)
    final_response = llm_result.content + "\n\n References:\n" + references
    # print(final_response)

    return {"final_response": final_response}


builder = StateGraph(ReportState)
builder.add_node("build_first_queries", build_first_queries)
builder.add_node("single_search", single_search)
builder.add_node("final_writer", final_writer)

builder.add_edge(START, "build_first_queries")
builder.add_conditional_edges("build_first_queries", 
                              spawn_researchers, 
                              ["single_search"])
builder.add_edge("single_search", "final_writer")
builder.add_edge("final_writer", END) 

graph = builder.compile()



if __name__ == "__main__":
    # from IPython.display import Image, display
    # display(Image(graph.get_graph().draw_mermaid_png()))
    # user_input = """How is the process of building a LLM?"""
    st.title("🌎 Local Perplexity")
    user_input = st.text_input("Qual a sua pergunta?", 
                               value="How is the process of building a LLM?")

    if st.button("Pesquisar"):
        # with st.spinner("Gerando resposta", show_time=True):
        with st.status("Gerando resposta"):
            for output in graph.stream({"user_input": user_input},
                                        stream_mode="debug"
                                        # stream_mode="messages"
                                        ):
                if output["type"] == "task_result":
                    st.write(f"Running {output['payload']['name']}")
                    st.write(output)
        # print(output)
        response = output["payload"]["result"][0][1]
        think_str = response.split("</think>")[0]
        final_response = response.split("</think>")[1]

        with st.expander("🧠 Reflexão", expanded=False):
            st.write(think_str)
        st.write(final_response)
    # output = graph.invoke({"user_input": user_input})
    # print(output["final_response"])
