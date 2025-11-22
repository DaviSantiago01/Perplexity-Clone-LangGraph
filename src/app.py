import streamlit as st
from main import graph

# Configuração da página
st.set_page_config(
    page_title="Perplexity Clone",
    page_icon="🔍",
    layout="wide"
)

# Inicializar histórico
if "historico" not in st.session_state:
    st.session_state.historico = []

# Header
st.title("🔍 Perplexity Clone com LangGraph")
st.markdown("Sistema de busca inteligente com IA")
st.divider()

# Input
pergunta = st.text_input(
    "Faça sua pergunta:",
    placeholder="Ex: Quais as principais tendências em IA para 2025?",
    key="input_pergunta"
)

# Botão de busca
if st.button("🚀 Buscar", type="primary", use_container_width=True):
    if pergunta and len(pergunta) >= 5:
        with st.spinner("🔍 Buscando e analisando..."):
            try:
                resultado = graph.invoke({"pergunta": pergunta})
                
                # Salvar histórico
                st.session_state.historico.append({
                    "pergunta": pergunta,
                    "resposta": resultado["resposta_final"],
                    "queries": resultado["queries"]
                })
                
                # Exibir resposta
                st.success("✅ Resposta gerada!")
                st.markdown("### 💡 Resposta:")
                st.markdown(resultado["resposta_final"])
                
                # Queries expansível
                with st.expander("🔎 Ver queries de busca"):
                    for i, query in enumerate(resultado["queries"], 1):
                        st.write(f"{i}. `{query}`")
                
            except Exception as e:
                st.error(f"❌ Erro: {str(e)}")
                
    elif pergunta:
        st.warning("⚠️ Pergunta muito curta (mínimo 5 caracteres)")
    else:
        st.warning("⚠️ Digite uma pergunta!")

# Sidebar com Histórico
with st.sidebar:
    st.header("📚 Histórico")
    
    if st.session_state.historico:
        if st.button("🗑️ Limpar histórico", use_container_width=True):
            st.session_state.historico = []
            st.rerun()
        
        st.divider()
        
        # Mostrar histórico invertido (mais recente primeiro)
        for i, item in enumerate(reversed(st.session_state.historico), 1):
            idx = len(st.session_state.historico) - i + 1
            with st.expander(f"#{idx}: {item['pergunta'][:50]}..."):
                st.markdown(f"**Pergunta:** {item['pergunta']}")
                st.markdown(f"**Resposta:** {item['resposta'][:200]}...")
    else:
        st.info("Nenhuma busca realizada ainda")