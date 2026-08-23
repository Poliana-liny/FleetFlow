"""
FleetFlow - Transform
=======================
Enriquecimento das viagens/ocorrências e cálculo das tabelas de KPI
comparativas — por transportadora e por região — que sustentam o
storytelling do projeto.
"""

import pandas as pd

DIAS_SEMANA_PT = {
    0: "Segunda", 1: "Terça", 2: "Quarta", 3: "Quinta",
    4: "Sexta", 5: "Sábado", 6: "Domingo",
}


def enriquecer_viagens(viagens: pd.DataFrame, rotas: pd.DataFrame, transportadoras: pd.DataFrame, centros: pd.DataFrame) -> pd.DataFrame:
    centros_nome = centros[["cd_id", "nome", "regiao"]]

    df = viagens.merge(rotas, on="rota_id", how="left", suffixes=("", "_rota"))
    df = df.merge(transportadoras, on="transportadora_id", how="left", suffixes=("", "_transp"))
    df = df.merge(
        centros_nome.rename(columns={"cd_id": "cd_origem_id", "nome": "cd_origem_nome", "regiao": "regiao_origem"}),
        on="cd_origem_id", how="left",
    )
    df = df.merge(
        centros_nome.rename(columns={"cd_id": "cd_destino_id", "nome": "cd_destino_nome", "regiao": "regiao_destino"}),
        on="cd_destino_id", how="left",
    )

    df["ano_mes"] = df["data_saida"].dt.to_period("M").astype(str)
    df["dia_semana"] = df["data_saida"].dt.weekday.map(DIAS_SEMANA_PT)
    df["atraso_horas"] = (df["lead_time_horas"] - df["tempo_estimado_horas"]).round(1)
    df["rota_nome"] = df["cd_origem_nome"] + " → " + df["cd_destino_nome"]

    return df


def enriquecer_ocorrencias(ocorrencias: pd.DataFrame, viagens_enriq: pd.DataFrame) -> pd.DataFrame:
    campos = viagens_enriq[[
        "viagem_id", "transportadora_id", "nome", "rota_id", "rota_nome",
        "regiao_origem", "regiao_destino", "regiao_dificil", "ano_mes",
    ]].rename(columns={"nome": "transportadora_nome"})
    return ocorrencias.merge(campos, on="viagem_id", how="left")


def gerar_kpis_transportadora(viagens_enriq: pd.DataFrame, ocorrencias_enriq: pd.DataFrame) -> pd.DataFrame:
    base = viagens_enriq.groupby(["transportadora_id", "nome", "tipo"]).agg(
        viagens=("viagem_id", "count"),
        pct_on_time=("on_time", "mean"),
        lead_time_medio_h=("lead_time_horas", "mean"),
        atraso_medio_h=("atraso_horas", "mean"),
        custo_medio_km=("custo_por_km", "mean"),
        custo_total_frete=("custo_frete", "sum"),
        pct_ocorrencia=("teve_ocorrencia", "mean"),
    ).reset_index()

    custo_ocorrencias = ocorrencias_enriq.groupby("transportadora_id")["custo_ocorrencia"].sum().reset_index(
        name="custo_total_ocorrencias"
    )
    base = base.merge(custo_ocorrencias, on="transportadora_id", how="left")
    base["custo_total_ocorrencias"] = base["custo_total_ocorrencias"].fillna(0)
    base["custo_total_geral"] = base["custo_total_frete"] + base["custo_total_ocorrencias"]

    for col in ["pct_on_time", "pct_ocorrencia"]:
        base[col] = base[col].round(4)
    for col in ["lead_time_medio_h", "atraso_medio_h", "custo_medio_km"]:
        base[col] = base[col].round(2)
    for col in ["custo_total_frete", "custo_total_ocorrencias", "custo_total_geral"]:
        base[col] = base[col].round(2)

    return base.sort_values("custo_medio_km").reset_index(drop=True)


def gerar_kpis_regiao(viagens_enriq: pd.DataFrame) -> pd.DataFrame:
    base = viagens_enriq.groupby("regiao_dificil").agg(
        viagens=("viagem_id", "count"),
        pct_on_time=("on_time", "mean"),
        lead_time_medio_h=("lead_time_horas", "mean"),
        atraso_medio_h=("atraso_horas", "mean"),
        pct_ocorrencia=("teve_ocorrencia", "mean"),
        custo_medio_km=("custo_por_km", "mean"),
    ).reset_index()
    base["regiao_dificil"] = base["regiao_dificil"].map({True: "Norte/Nordeste", False: "Sudeste/Sul/Centro-Oeste"})

    for col in ["pct_on_time", "pct_ocorrencia"]:
        base[col] = base[col].round(4)
    for col in ["lead_time_medio_h", "atraso_medio_h", "custo_medio_km"]:
        base[col] = base[col].round(2)

    return base


def gerar_kpis_rota(viagens_enriq: pd.DataFrame) -> pd.DataFrame:
    base = viagens_enriq.groupby(["rota_id", "rota_nome", "regiao_dificil"]).agg(
        viagens=("viagem_id", "count"),
        distancia_km=("distancia_km", "first"),
        pct_on_time=("on_time", "mean"),
        lead_time_medio_h=("lead_time_horas", "mean"),
        pct_ocorrencia=("teve_ocorrencia", "mean"),
    ).reset_index()

    for col in ["pct_on_time", "pct_ocorrencia"]:
        base[col] = base[col].round(4)
    base["lead_time_medio_h"] = base["lead_time_medio_h"].round(2)

    return base.sort_values("pct_on_time")
