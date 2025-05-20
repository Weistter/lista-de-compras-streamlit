import streamlit as st
import json
import os

st.set_page_config(page_title="Editor de Lista Base", layout="centered")
st.title("🔐 Editor da Lista Base Semanal")

ARQUIVO_LISTA_BASE = "lista_base.json"
CATEGORIAS = ["Condimentos", "Açougue", "Frios", "Feira", "Limpeza"]
UNIDADES = ["Un", "Pct", "Kg", "L"]
SENHA_CORRETA = "123"

# Autenticação simples
if "autenticado_base" not in st.session_state:
    st.session_state.autenticado_base = False

if not st.session_state.autenticado_base:
    senha = st.text_input("Digite a senha para acessar o editor:", type="password")
    if st.button("Entrar"):
        if senha == SENHA_CORRETA:
            st.session_state.autenticado_base = True
            st.rerun()
        else:
            st.error("❌ Senha incorreta.")
    st.stop()

# Carrega a lista base
if os.path.exists(ARQUIVO_LISTA_BASE):
    with open(ARQUIVO_LISTA_BASE, "r", encoding="utf-8") as f:
        lista_base = json.load(f)
else:
    lista_base = {}

# Sessão de edição
if "item_em_edicao" not in st.session_state:
    st.session_state.item_em_edicao = None

# Formulário de adicionar/editar
st.subheader("➕ Adicionar ou Editar Item")

# Se for edição, carrega valores atuais
item_atual = st.session_state.item_em_edicao
if item_atual and item_atual in lista_base:
    dados = lista_base[item_atual]
    nome_default = item_atual
    qtd_default = dados["quantidade"]
    un_default = dados["unidade"]
    cat_default = dados["categoria"]
else:
    nome_default = ""
    qtd_default = 0.0
    un_default = UNIDADES[0]
    cat_default = CATEGORIAS[0]

with st.form("form_item"):
    nome = st.text_input("Nome do item", value=nome_default)
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        qtd = st.number_input("Qtd mínima", min_value=0.0, step=0.1, value=float(qtd_default))
    with col2:
        un = st.selectbox("Unidade", UNIDADES, index=UNIDADES.index(un_default) if un_default in UNIDADES else 0)
    with col3:
        cat = st.selectbox("Categoria", CATEGORIAS, index=CATEGORIAS.index(cat_default) if cat_default in CATEGORIAS else 0)
    salvar = st.form_submit_button("💾 Salvar")

# Salvar ou editar
if salvar:
    if not nome.strip():
        st.error("❗ Digite o nome do item.")
    else:
        if item_atual and item_atual != nome and item_atual in lista_base:
            del lista_base[item_atual]  # Renomeou o item
        lista_base[nome] = {"quantidade": qtd, "unidade": un, "categoria": cat}
        with open(ARQUIVO_LISTA_BASE, "w", encoding="utf-8") as f:
            json.dump(lista_base, f, indent=2, ensure_ascii=False)
        st.success(f"✅ Item '{nome}' salvo com sucesso!")
        st.session_state.item_em_edicao = None
        st.rerun()

# Exibe itens existentes com botões de ação
st.subheader("📦 Itens da Lista Base")
if lista_base:
    for nome, dados in lista_base.items():
        col1, col2, col3 = st.columns([5, 1, 1])
        with col1:
            st.write(f"**{nome}** - {dados['quantidade']} {dados['unidade']} ({dados['categoria']})")
        with col2:
            if st.button("✏️", key=f"edit_{nome}"):
                st.session_state.item_em_edicao = nome
                st.rerun()
        with col3:
            if st.button("🗑️", key=f"del_{nome}"):
                del lista_base[nome]
                with open(ARQUIVO_LISTA_BASE, "w", encoding="utf-8") as f:
                    json.dump(lista_base, f, indent=2, ensure_ascii=False)
                st.success(f"❌ Item '{nome}' removido com sucesso!")
                st.rerun()
else:
    st.info("Nenhum item cadastrado ainda.")
