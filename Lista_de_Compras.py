import streamlit as st
import pandas as pd
import json
import os
from collections import defaultdict

st.set_page_config(page_title="Lista de Compras Automatizada", layout="centered")
st.title("🛒 Lista de Compras Automatizada")

ARQUIVO_RECEITAS = "receitas.json"
ARQUIVO_LISTA_BASE = "lista_base.json"

# === Funções com cache (releem arquivos a cada segundo) ===
@st.cache_data(ttl=1)
def carregar_receitas():
    if os.path.exists(ARQUIVO_RECEITAS):
        with open(ARQUIVO_RECEITAS, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

@st.cache_data(ttl=1)
def carregar_lista_base():
    if os.path.exists(ARQUIVO_LISTA_BASE):
        with open(ARQUIVO_LISTA_BASE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

receitas = carregar_receitas()
lista_base = carregar_lista_base()

# === Inicialização de estado ===
if "estoque_usuario" not in st.session_state:
    st.session_state.estoque_usuario = {item: 0.0 for item in lista_base}

if "receitas_selecionadas" not in st.session_state:
    st.session_state.receitas_selecionadas = []

if "extras" not in st.session_state:
    st.session_state.extras = []

# === Botão de reset ===
if st.button("🔄 Resetar tudo"):
    st.session_state.estoque_usuario = {item: 0.0 for item in lista_base}
    st.session_state.receitas_selecionadas = []
    st.session_state.extras = []
    st.rerun()

# === Seleção de receitas ===
st.subheader("👨‍🍳 Escolha até 5 receitas:")
selecionadas = st.multiselect(
    "Receitas:",
    list(receitas.keys()),
    default=st.session_state.get("receitas_selecionadas", []),
    max_selections=5,
    key="multiselect_receitas"
)

# Atualiza somente se o usuário interagir
if "multiselect_receitas" in st.session_state:
    st.session_state.receitas_selecionadas = st.session_state.multiselect_receitas

# === Estoque do usuário ===
st.subheader("📦 Quantos itens você tem em casa?")
itens_unicos = set(lista_base.keys())
for nome in st.session_state.receitas_selecionadas:
    itens_unicos.update(receitas.get(nome, {}).keys())

for item in sorted(itens_unicos):
    unidade = (
        lista_base.get(item, {}).get("unidade")
        or next((receitas[n].get(item, [None, None])[1] for n in st.session_state.receitas_selecionadas if item in receitas[n]), "")
    )
    st.session_state.estoque_usuario[item] = st.number_input(
        f"{item} ({unidade})",
        min_value=0.0,
        step=0.1,
        key=f"estoque_{item}",
        value=st.session_state.estoque_usuario.get(item, 0.0)
    )

# === Adição de item extra manual ===
st.subheader("➕ Adicionar item extra (manual)")
with st.form("form_item_extra"):
    col1, col2, col3, col4 = st.columns([3, 1, 1, 2])
    with col1:
        nome_extra = st.text_input("Item")
    with col2:
        qtd_extra = st.number_input("Qtd", min_value=0.0, step=0.1, value=0.0)
    with col3:
        un_extra = st.selectbox("Unidade", ["Un", "Pct", "Kg", "L"])
    with col4:
        cat_extra = st.selectbox("Categoria", ["Condimentos", "Açougue", "Frios", "Feira", "Limpeza", "Outros"])
    adicionar = st.form_submit_button("Adicionar")

if adicionar and nome_extra.strip():
    st.session_state.extras.append({
        "item": nome_extra.strip(),
        "quantidade": round(qtd_extra, 2),
        "unidade": un_extra,
        "categoria": cat_extra
    })
    st.success(f"Item '{nome_extra}' adicionado à lista!")

# === Gerar lista de compras ===
if st.button("Gerar lista de compras"):
    ingredientes_necessarios = defaultdict(lambda: [0, ""])
    ingredientes_extras = {}

    for nome in st.session_state.receitas_selecionadas:
        for item, (qtd, un, cat) in receitas[nome].items():
            ingredientes_necessarios[item][0] += qtd
            ingredientes_necessarios[item][1] = un
            if item not in lista_base:
                ingredientes_extras[item] = {"quantidade": 0, "unidade": un, "categoria": cat}

    # Garante que todos os ingredientes estejam no estoque_usuario
    for item in ingredientes_necessarios:
        if item not in st.session_state.estoque_usuario:
            st.session_state.estoque_usuario[item] = 0.0

    itens_ativos = {**lista_base, **ingredientes_extras}
    faltantes = defaultdict(lambda: [0, "", ""])

    for item, dados in itens_ativos.items():
        qtd_min = dados["quantidade"]
        un = dados["unidade"]
        cat = dados.get("categoria", "Outros")
        qtd_atual = st.session_state.estoque_usuario.get(item, 0)
        if qtd_atual < qtd_min:
            faltantes[item][0] += round(qtd_min - qtd_atual, 2)
            faltantes[item][1] = un
            faltantes[item][2] = cat

    for item, (qtd_rec, un) in ingredientes_necessarios.items():
        qtd_atual = st.session_state.estoque_usuario.get(item, 0)
        if qtd_atual < qtd_rec:
            faltantes[item][0] += round(qtd_rec - qtd_atual, 2)
            faltantes[item][1] = un
            faltantes[item][2] = ingredientes_extras.get(item, {}).get("categoria", lista_base.get(item, {}).get("categoria", "Outros"))

    # Monta DataFrame final
    linhas = [
        {"Item": item, "Qtd. Faltante": round(qtd, 2), "Unidade": un, "Categoria": cat}
        for item, (qtd, un, cat) in faltantes.items() if qtd > 0
    ]

    for e in st.session_state.extras:
        linhas.append({
            "Item": e["item"],
            "Qtd. Faltante": e["quantidade"],
            "Unidade": e["unidade"],
            "Categoria": e["categoria"]
        })

    resultado_df = pd.DataFrame(linhas)

    st.success("✅ Lista de compras gerada com sucesso!")

    for categoria in sorted(resultado_df["Categoria"].unique()):
        st.markdown(f"### 🗂️ {categoria}")
        df_cat = resultado_df[resultado_df["Categoria"] == categoria][["Item", "Qtd. Faltante", "Unidade"]]
        st.dataframe(df_cat, use_container_width=True)

    csv = resultado_df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Baixar lista como CSV", data=csv, file_name="lista_de_compras.csv", mime="text/csv")