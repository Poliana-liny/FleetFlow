"""
FleetFlow - Análise com Storytelling
======================================
Diferente do OpsFlow (antes x depois), aqui o recorte é comparativo:
transportadoras entre si, e regiões "fáceis" x "difíceis" de operar.

Pergunta de negócio central:
    "Vale a pena escolher a transportadora mais barata por km? E o que
    realmente diferencia o desempenho entre as regiões: a transportadora
    ou a rota?"

Gera gráficos em analysis/figuras/ e um relatório narrativo em
analysis/storytelling.md.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd

DATA_DIR = "data/processed"
FIG_DIR = "analysis/figuras"

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "font.size": 11,
})

COR_PROPRIA = "#1e5f8c"
COR_TERCEIRIZADA = "#c0392b"


def carregar_dados():
    viagens = pd.read_csv(f"{DATA_DIR}/viagens_enriquecidas.csv")
    ocorrencias = pd.read_csv(f"{DATA_DIR}/ocorrencias_enriquecidas.csv")
    kpis_transp = pd.read_csv(f"{DATA_DIR}/kpis_transportadora.csv")
    kpis_regiao = pd.read_csv(f"{DATA_DIR}/kpis_regiao.csv")
    kpis_rota = pd.read_csv(f"{DATA_DIR}/kpis_rota.csv")
    return viagens, ocorrencias, kpis_transp, kpis_regiao, kpis_rota


def calcular_custo_efetivo(viagens: pd.DataFrame, kpis_transp: pd.DataFrame) -> pd.DataFrame:
    """Custo por km somando o custo de ocorrências amortizado — o custo 'de verdade'."""
    km_total = viagens.groupby("nome")["distancia_km"].sum().reset_index(name="km_total")
    kt = kpis_transp.merge(km_total, on="nome")
    kt["custo_efetivo_km"] = (kt["custo_total_geral"] / kt["km_total"]).round(2)
    return kt.sort_values("custo_efetivo_km")


def grafico_custo_x_confiabilidade(kt: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(8, 5.5))
    for _, row in kt.iterrows():
        cor = COR_PROPRIA if row["tipo"] == "Própria" else COR_TERCEIRIZADA
        tamanho = row["viagens"] / 2
        ax.scatter(row["custo_efetivo_km"], row["pct_on_time"] * 100, s=tamanho, color=cor, alpha=0.75, edgecolor="white", linewidth=1.2)
        ax.annotate(row["nome"], (row["custo_efetivo_km"], row["pct_on_time"] * 100),
                    xytext=(8, 6), textcoords="offset points", fontsize=9.5)

    ax.set_xlabel("Custo efetivo por km (R$) — inclui ocorrências")
    ax.set_ylabel("% On Time")
    ax.set_title("Custo x Confiabilidade por transportadora\n(tamanho da bolha = volume de viagens)", fontsize=13, fontweight="bold")
    ax.yaxis.set_major_formatter(mticker.PercentFormatter())
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="both", alpha=0.25)
    fig.tight_layout()
    fig.savefig(f"{FIG_DIR}/01_custo_x_confiabilidade.png", dpi=140)
    plt.close(fig)


def grafico_ocorrencias_por_tipo(ocorrencias: pd.DataFrame):
    tab = ocorrencias.groupby(["transportadora_nome", "tipo"]).size().unstack(fill_value=0)
    tab = tab.loc[tab.sum(axis=1).sort_values(ascending=False).index]

    fig, ax = plt.subplots(figsize=(9, 5.5))
    tab.plot(kind="bar", stacked=True, ax=ax, color=["#e67e22", "#c0392b", "#7f1d1d"])
    ax.set_xlabel("")
    ax.set_ylabel("Nº de ocorrências")
    ax.set_title("Ocorrências por tipo e transportadora", fontsize=13, fontweight="bold")
    ax.legend(title="Tipo", frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    plt.xticks(rotation=20, ha="right")
    fig.tight_layout()
    fig.savefig(f"{FIG_DIR}/02_ocorrencias_por_tipo.png", dpi=140)
    plt.close(fig)


def grafico_regiao_comparativo(kpis_regiao: pd.DataFrame):
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.5))

    indicadores = [
        ("pct_on_time", "% On Time", True),
        ("lead_time_medio_h", "Lead time médio (h)", False),
        ("pct_ocorrencia", "% Ocorrência", True),
    ]
    cores = ["#1e5f8c", "#c0392b"]

    for ax, (col, titulo, pct) in zip(axes, indicadores):
        valores = kpis_regiao[col] * 100 if pct else kpis_regiao[col]
        ax.bar(kpis_regiao["regiao_dificil"], valores, color=cores)
        ax.set_title(titulo, fontsize=11, fontweight="bold")
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(axis="x", labelrotation=15)
        if pct:
            ax.yaxis.set_major_formatter(mticker.PercentFormatter())

    fig.suptitle("Sudeste/Sul/Centro-Oeste x Norte/Nordeste", fontsize=13, fontweight="bold", y=1.03)
    fig.tight_layout()
    fig.savefig(f"{FIG_DIR}/03_comparativo_regiao.png", dpi=140, bbox_inches="tight")
    plt.close(fig)


def grafico_piores_rotas(kpis_rota: pd.DataFrame):
    piores = kpis_rota.sort_values("pct_on_time").head(6)

    fig, ax = plt.subplots(figsize=(9, 5))
    cores = ["#c0392b" if d else "#1e5f8c" for d in piores["regiao_dificil"]]
    ax.barh(piores["rota_nome"], piores["pct_on_time"] * 100, color=cores)
    ax.set_xlabel("% On Time")
    ax.set_title("Rotas com pior desempenho de pontualidade", fontsize=13, fontweight="bold")
    ax.xaxis.set_major_formatter(mticker.PercentFormatter())
    ax.spines[["top", "right"]].set_visible(False)
    ax.invert_yaxis()
    fig.tight_layout()
    fig.savefig(f"{FIG_DIR}/04_piores_rotas.png", dpi=140)
    plt.close(fig)


def grafico_custo_total_geral(kt: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(9, 5))
    ordem = kt.sort_values("custo_efetivo_km")
    cores = [COR_PROPRIA if t == "Própria" else COR_TERCEIRIZADA for t in ordem["tipo"]]
    ax.bar(ordem["nome"], ordem["custo_efetivo_km"], color=cores)
    ax.set_ylabel("Custo efetivo por km (R$)")
    ax.set_title("Custo efetivo por km — frete + ocorrências amortizadas", fontsize=13, fontweight="bold")
    ax.spines[["top", "right"]].set_visible(False)
    plt.xticks(rotation=20, ha="right")
    fig.tight_layout()
    fig.savefig(f"{FIG_DIR}/05_custo_efetivo_km.png", dpi=140)
    plt.close(fig)


def gerar_relatorio(kt: pd.DataFrame, kpis_regiao: pd.DataFrame, kpis_rota: pd.DataFrame, ocorrencias: pd.DataFrame):
    mais_barata = kt.iloc[0]
    mais_confiavel = kt.sort_values("pct_on_time", ascending=False).iloc[0]
    pior_ocorrencia = kt.sort_values("pct_ocorrencia", ascending=False).iloc[0]

    dificil = kpis_regiao[kpis_regiao["regiao_dificil"] == "Norte/Nordeste"].iloc[0]
    facil = kpis_regiao[kpis_regiao["regiao_dificil"] == "Sudeste/Sul/Centro-Oeste"].iloc[0]

    pior_rota = kpis_rota.sort_values("pct_on_time").iloc[0]

    custo_ocorrencias_total = ocorrencias["custo_ocorrencia"].sum()

    conteudo = f"""# FleetFlow — Storytelling: Custo x Confiabilidade no Transporte CD-a-CD

## 1. A pergunta de negócio

> "Vale a pena escolher a transportadora mais barata por km? E o que
> realmente diferencia o desempenho entre regiões: a transportadora ou
> a rota?"

## 2. Custo não é só o valor por km cobrado

A **{mais_barata['nome']}** tem o menor custo por km cobrado
(R$ {mais_barata['custo_medio_km']:.2f}), mas quando se soma o custo das
ocorrências que ela gera (avarias, atrasos por manutenção, sinistros) e
se divide pelo total de km rodados, o **custo efetivo** sobe para
R$ {mais_barata['custo_efetivo_km']:.2f}/km — ainda a opção mais barata
do grupo, mas a diferença para as demais **diminui**.

O que essa transportadora entrega em troca do preço:
- **{mais_barata['pct_on_time']*100:.1f}%** de entregas no prazo (a pior
  taxa entre as 5 transportadoras)
- **{mais_barata['pct_ocorrencia']*100:.1f}%** de viagens com alguma
  ocorrência (a maior taxa do grupo)

Do outro lado, a **{mais_confiavel['nome']}** custa R$ {mais_confiavel['custo_efetivo_km']:.2f}/km
efetivo — quase o dobro — mas entrega **{mais_confiavel['pct_on_time']*100:.1f}%**
de pontualidade e a menor taxa de ocorrência do grupo
({mais_confiavel['pct_ocorrencia']*100:.1f}%).

**A decisão não é "qual é mais barata", é "o que a operação está
disposta a pagar por confiabilidade".** Para cargas urgentes ou de alto
valor, o prêmio de preço da {mais_confiavel['nome']} se paga sozinho
evitando o custo (e o risco reputacional) de atrasos e sinistros.

## 3. Região difícil não significa necessariamente atraso — mas significa mais ocorrência

Comparando rotas que passam por Norte/Nordeste contra as demais:

| Indicador | Sudeste/Sul/Centro-Oeste | Norte/Nordeste |
|---|---|---|
| % On Time | {facil['pct_on_time']*100:.1f}% | {dificil['pct_on_time']*100:.1f}% |
| Lead time médio | {facil['lead_time_medio_h']:.1f} h | {dificil['lead_time_medio_h']:.1f} h |
| % Ocorrência | {facil['pct_ocorrencia']*100:.1f}% | {dificil['pct_ocorrencia']*100:.1f}% |

O percentual de pontualidade é parecido entre as duas regiões — porque o
SLA já é calculado considerando a velocidade média mais baixa das rotas
difíceis. Mas a **taxa de ocorrência é {(dificil['pct_ocorrencia']/facil['pct_ocorrencia']-1)*100:.0f}% maior**
nas rotas de Norte/Nordeste — reflexo de estradas, distância a pontos de
manutenção e maior desgaste da frota nessas condições.

A rota com pior desempenho de pontualidade é **{pior_rota['rota_nome']}**,
com apenas {pior_rota['pct_on_time']*100:.1f}% de entregas no prazo — mais
um indício de que a dificuldade real está concentrada em rotas
específicas, não distribuída igualmente por toda a malha.

## 4. O custo real das ocorrências

No total da base, as ocorrências (avarias, atrasos por manutenção e
sinistros) somaram **R$ {custo_ocorrencias_total:,.2f}** em 6 meses —
um custo que não aparece na cotação de frete, mas que impacta
diretamente a margem da operação. A transportadora com maior taxa de
ocorrência ({pior_ocorrencia['nome']}, {pior_ocorrencia['pct_ocorrencia']*100:.1f}%)
é justamente uma das mais baratas por km — reforçando que negociar só
pelo preço, sem olhar o histórico de ocorrências, é decisão incompleta.

## 5. Gráficos de apoio

- `01_custo_x_confiabilidade.png` — o trade-off central do projeto
- `02_ocorrencias_por_tipo.png` — quais transportadoras concentram quais tipos de problema
- `03_comparativo_regiao.png` — Sudeste/Sul/Centro-Oeste x Norte/Nordeste
- `04_piores_rotas.png` — rotas com pior pontualidade
- `05_custo_efetivo_km.png` — ranking de custo real (frete + ocorrências)

## 6. Conclusão

A pergunta certa não é "qual transportadora é mais barata", mas **"qual
é o custo total esperado por km, dado o histórico de confiabilidade
dessa transportadora?"** — uma decisão de sourcing logístico que só fica
visível cruzando custo de frete, taxa de ocorrência e o tipo de rota
operada.
"""

    with open("analysis/storytelling.md", "w") as f:
        f.write(conteudo)


def main():
    viagens, ocorrencias, kpis_transp, kpis_regiao, kpis_rota = carregar_dados()
    kt = calcular_custo_efetivo(viagens, kpis_transp)

    grafico_custo_x_confiabilidade(kt)
    grafico_ocorrencias_por_tipo(ocorrencias)
    grafico_regiao_comparativo(kpis_regiao)
    grafico_piores_rotas(kpis_rota)
    grafico_custo_total_geral(kt)

    gerar_relatorio(kt, kpis_regiao, kpis_rota, ocorrencias)

    print("Gráficos salvos em analysis/figuras/")
    print("Storytelling salvo em analysis/storytelling.md")


if __name__ == "__main__":
    main()
