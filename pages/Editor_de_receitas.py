import streamlit as st
import json
import os
import streamlit.components.v1 as components

st.set_page_config(page_title="Editor de Receitas", layout="centered")

ARQUIVO_RECEITAS = "receitas.json"
SENHA_CORRETA = "123"
CATEGORIAS = ["Feira", "Frios", "Açougue", "Condimentos", "Limpeza", "Outros"]
UNIDADES = ["Un", "Pct", "Kg", "L"]

# ==== AUTENTICAÇÃO ====
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🔐 Área Restrita")
    senha = st.text_input("Digite a senha para acessar o editor:", type="password")
    if st.button("Entrar"):
        if senha == SENHA_CORRETA:
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("❌ Senha incorreta.")
    st.stop()

# ==== CARREGAR RECEITAS ====
if os.path.exists(ARQUIVO_RECEITAS):
    with open(ARQUIVO_RECEITAS, "r", encoding="utf-8") as f:
        receitas = json.load(f)
else:
    receitas = {}

# ==== CONTROLE DE ESTADO ====
if "editar_receita" not in st.session_state:
    st.session_state.editar_receita = None
if "ingredientes_count" not in st.session_state:
    st.session_state.ingredientes_count = 1

# ==== FUNÇÃO PARA ADICIONAR INGREDIENTE ==== #
def adicionar_ingrediente():
    st.session_state.ingredientes_count += 1

# ==== FORMULÁRIO DE NOVA RECEITA / EDIÇÃO ==== #
st.subheader("➕ Nova Receita ou Edição")

nome_receita_default = ""
ingredientes_editar = {}

if st.session_state.editar_receita:
    nome_receita_default = st.session_state.editar_receita
    ingredientes_editar = receitas.get(nome_receita_default, {})
    if st.session_state.ingredientes_count < len(ingredientes_editar):
        st.session_state.ingredientes_count = len(ingredientes_editar)

nome_receita = st.text_input("Nome da receita", value=nome_receita_default, key="nome_input")

with st.form("form_ingredientes"):
    st.write("Ingredientes:")
    ingredientes = []
    for i in range(st.session_state.ingredientes_count):
        nome_padrao = list(ingredientes_editar.keys())[i] if i < len(ingredientes_editar) else ""
        dados_padrao = ingredientes_editar.get(nome_padrao, [0, "Un", "Outros"]) if nome_padrao else [0, "Un", "Outros"]
        qtd_padrao, un_padrao, cat_padrao = dados_padrao

        col1, col2, col3, col4 = st.columns([3, 1, 1, 2])
        with col1:
            nome = st.text_input(f"Ingrediente {i+1}", value=nome_padrao, key=f"nome_{i}")
        with col2:
            qtd = st.number_input("Qtd", min_value=0.0, step=0.1, value=float(qtd_padrao), key=f"qtd_{i}")
        with col3:
            un = st.selectbox("Un", UNIDADES, index=UNIDADES.index(un_padrao) if un_padrao in UNIDADES else 0, key=f"un_{i}")
        with col4:
            cat = st.selectbox("Categoria", CATEGORIAS, index=CATEGORIAS.index(cat_padrao) if cat_padrao in CATEGORIAS else 0, key=f"cat_{i}")

        if nome:
            ingredientes.append((nome, qtd, un, cat))

    col_a, col_b = st.columns([1, 3])
    with col_a:
        st.form_submit_button("➕", on_click=adicionar_ingrediente)
    with col_b:
        salvar = st.form_submit_button("💾 Salvar Receita")

# ==== SALVAR RECEITA ==== #
if salvar:
    if not nome_receita.strip():
        st.error("❗ Digite o nome da receita.")
    elif not ingredientes:
        st.error("❗ Adicione ao menos um ingrediente.")
    else:
        if st.session_state.editar_receita and nome_receita != st.session_state.editar_receita:
            receitas.pop(st.session_state.editar_receita, None)

        receitas[nome_receita] = {nome: [qtd, un, cat] for nome, qtd, un, cat in ingredientes}
        with open(ARQUIVO_RECEITAS, "w", encoding="utf-8") as f:
            json.dump(receitas, f, indent=2, ensure_ascii=False)

        st.success(f"✅ Receita '{nome_receita}' salva com sucesso!")
        st.session_state.editar_receita = None
        st.session_state.ingredientes_count = 1
        st.rerun()

# ==== LISTAGEM DE RECEITAS ==== #
st.subheader("📚 Receitas Existentes")
if receitas:
    for nome, itens in receitas.items():
        col1, col2 = st.columns([5, 1])
        with col1:
            with st.expander(nome):
                for ingrediente, (qtd, un, cat) in itens.items():
                    st.write(f"- {ingrediente}: {qtd} {un} ({cat})")
        with col2:
            if st.button("✏️ Editar", key=f"edit_{nome}"):
                st.session_state.editar_receita = nome
                st.rerun()
                st.jump("form_ingredientes")
            if st.button("🗑️ Excluir", key=f"delete_{nome}"):
                del receitas[nome]
                with open(ARQUIVO_RECEITAS, "w", encoding="utf-8") as f:
                    json.dump(receitas, f, indent=2, ensure_ascii=False)
                st.success(f"❌ Receita '{nome}' excluída com sucesso!")
                st.rerun()
else:
    st.info("Nenhuma receita cadastrada ainda.")
