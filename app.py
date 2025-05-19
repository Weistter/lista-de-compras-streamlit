
import streamlit as st
import pandas as pd
from collections import defaultdict

st.set_page_config(page_title="Lista de Compras Automatizada", layout="centered")
st.title("🛒 Lista de Compras Automatizada")

# Lista base semanal
lista_base = {
    "Arroz": (5, "Kg"), "Feijão": (2, "Kg"), "Açucar": (2, "Kg"), "Sal": (0.5, "Kg"),
    "Tempero pronto Sem Gluten": (0.5, "Kg"), "Amido de milho Sem Gluten": (0.5, "Kg"),
    "Oleo": (2, "L"), "Pó de café": (1, "Kg"), "Ovo": (6, "Un"), "Folha de louro": (0.1, "Kg"),
    "Paprica": (0.1, "Kg"), "Alho": (0.2, "Kg"), "Cebola": (0.3, "Kg"), "Limão": (0.3, "Kg"),
    "Batata": (0, "Kg"), "Cheiro verde": (0, "Kg"), "Sabão em pó": (2, "Kg"),
    "Amaciante": (1, "L"), "Sabão barra": (2, "Un"), "Sabonete líquido": (0.5, "L"),
    "Aguá sanitária com cloro": (2, "L"), "Desinfetante": (2, "L"),
    "Limpador multiuso (veja/azulim)": (1, "L"), "Álcool": (0.5, "L"),
    "Saco de lixo": (15, "Un"), "Esponja": (2, "Un"), "Palha de aço (bombril / açolã)": (1, "Un")
}

# Receitas com ingredientes
receitas = {
    "Fricassê": {
        "Peito de frango com osso": (3, "Kg"), "Creme de leite - caixinha com 200g": (2, "Cx"),
        "Batata palha - pacote com 500g": (1, "Pct"), "Queijo mussarela": (0.3, "Kg"),
    },
    "Pernil assado": {
        "Pernil sem osso - peça inteira com 2 Kg": (2, "Pç"), "Cebola cabeça grande": (2, "Un"),
    },
    "Costelinha BBQ": {
        "Ponta de costela": (4, "Kg"), "Barbecue": (0.3, "Kg"), "Cebola cabeça grande": (1, "Un"),
    },
    "Frango Grelhado": {
        "Peito de frango sem osso": (3, "Kg"), "Cebola cabeça grande": (1, "Un"),
    },
    "Kibe": {
        "Farinha de kibe - pacote com 500g": (2, "Pct"), "Carne moida": (2.5, "Kg"),
        "Cheiro verde": (0.1, "Kg"), "Queijo mussarela": (0.2, "Kg"),
    },
    "Torta de frango": {
        "Farinha de trigo": (0.5, "Kg"), "Frango": (2.5, "Kg"), "Ovo": (5, "Un"),
        "Leite": (0.2, "L"), "Requeijão ou mussarela (opcional)": (0.2, "Kg"),
    },
    "Escondidinho de batata": {
        "Peito de frango com osso": (2, "Kg"), "Batata": (1, "Kg"),
        "Molho de tomate - pacote com 300g": (3, "Pct"),
    },
    "Carne de panela com Mandioca": {
        "Carne bovina p/ panela": (2, "Kg"), "Mandioca": (1, "Kg"), "Cebola cabeça grande": (1, "Un"),
    },
    "Carne de panela com Batata": {
        "Carne bovina p/ panela": (2, "Kg"), "Batata": (1, "Kg"), "Cebola cabeça grande": (1, "Un"),
    },
}

# Adiciona ingredientes à lista base
for receita in receitas.values():
    for item, (_, un) in receita.items():
        if item not in lista_base:
            lista_base[item] = (0, un)

st.subheader("🧾 Quantos itens você tem em casa?")
estoque_usuario = {}
for item, (_, un) in lista_base.items():
    estoque_usuario[item] = st.number_input(f"{item} ({un})", min_value=0.0, step=0.1)

st.subheader("👨‍🍳 Escolha até 5 receitas:")
selecionadas = st.multiselect("Receitas:", list(receitas.keys()), max_selections=5)

if st.button("Gerar lista de compras"):
    from collections import defaultdict
    ingredientes_necessarios = defaultdict(lambda: [0, ""])
    for nome in selecionadas:
        for item, (qtd, un) in receitas[nome].items():
            ingredientes_necessarios[item][0] += qtd
            ingredientes_necessarios[item][1] = un

    faltantes = defaultdict(lambda: [0, ""])
    for item, (min_qtd, un) in lista_base.items():
        qtd_atual = estoque_usuario.get(item, 0)
        if qtd_atual < min_qtd:
            faltantes[item][0] += round(min_qtd - qtd_atual, 2)
            faltantes[item][1] = un

    for item, (qtd_rec, un) in ingredientes_necessarios.items():
        qtd_atual = estoque_usuario.get(item, 0)
        if qtd_atual < qtd_rec:
            faltantes[item][0] += round(qtd_rec - qtd_atual, 2)
            faltantes[item][1] = un

    resultado = pd.DataFrame([
        {"Item": item, "Qtd. Faltante": round(qtd, 2), "Unidade": un}
        for item, (qtd, un) in faltantes.items() if qtd > 0
    ])

    st.success("✅ Lista de compras gerada com sucesso!")
    st.dataframe(resultado, use_container_width=True)

    csv = resultado.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Baixar lista como CSV", data=csv, file_name="lista_de_compras.csv", mime="text/csv")
