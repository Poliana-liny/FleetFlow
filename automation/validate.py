"""
FleetFlow - Validate
======================
Checagens de qualidade de dados. Cada função retorna uma lista de
problemas encontrados (vazia se estiver tudo certo).
"""

import pandas as pd


def _checar_nulos(df: pd.DataFrame, colunas: list, tabela: str) -> list:
    problemas = []
    for col in colunas:
        n_nulos = df[col].isna().sum()
        if n_nulos > 0:
            problemas.append(f"[{tabela}] {n_nulos} valores nulos em '{col}'")
    return problemas


def _checar_duplicados(df: pd.DataFrame, chave: str, tabela: str) -> list:
    n_dup = df[chave].duplicated().sum()
    if n_dup > 0:
        return [f"[{tabela}] {n_dup} valores duplicados na chave '{chave}'"]
    return []


def _checar_fk(df: pd.DataFrame, coluna: str, valores_validos: set, tabela: str) -> list:
    invalidos = ~df[coluna].isin(valores_validos)
    if invalidos.any():
        return [f"[{tabela}] {invalidos.sum()} registros com '{coluna}' fora do domínio esperado"]
    return []


def _checar_intervalo(df: pd.DataFrame, coluna: str, minimo, maximo, tabela: str) -> list:
    fora = ~df[coluna].between(minimo, maximo)
    if fora.any():
        return [f"[{tabela}] {fora.sum()} registros com '{coluna}' fora do intervalo [{minimo}, {maximo}]"]
    return []


def validar_tudo(dados: dict) -> list:
    problemas = []

    centros_validos = set(dados["centros"]["cd_id"])
    transportadoras_validas = set(dados["transportadoras"]["transportadora_id"])
    veiculos_validos = set(dados["veiculos"]["veiculo_id"])
    rotas_validas = set(dados["rotas"]["rota_id"])

    problemas += _checar_nulos(dados["centros"], ["cd_id", "nome", "regiao"], "centros")
    problemas += _checar_duplicados(dados["centros"], "cd_id", "centros")

    problemas += _checar_duplicados(dados["rotas"], "rota_id", "rotas")
    problemas += _checar_fk(dados["rotas"], "cd_origem_id", centros_validos, "rotas")
    problemas += _checar_fk(dados["rotas"], "cd_destino_id", centros_validos, "rotas")
    problemas += _checar_intervalo(dados["rotas"], "distancia_km", 1, 10000, "rotas")

    problemas += _checar_duplicados(dados["transportadoras"], "transportadora_id", "transportadoras")

    problemas += _checar_duplicados(dados["veiculos"], "veiculo_id", "veiculos")
    problemas += _checar_fk(dados["veiculos"], "transportadora_id", transportadoras_validas, "veiculos")

    problemas += _checar_nulos(
        dados["viagens"],
        ["viagem_id", "rota_id", "veiculo_id", "transportadora_id", "lead_time_horas"],
        "viagens",
    )
    problemas += _checar_duplicados(dados["viagens"], "viagem_id", "viagens")
    problemas += _checar_fk(dados["viagens"], "rota_id", rotas_validas, "viagens")
    problemas += _checar_fk(dados["viagens"], "veiculo_id", veiculos_validos, "viagens")
    problemas += _checar_fk(dados["viagens"], "transportadora_id", transportadoras_validas, "viagens")
    problemas += _checar_intervalo(dados["viagens"], "lead_time_horas", 0, 500, "viagens")
    problemas += _checar_intervalo(dados["viagens"], "custo_por_km", 0, 20, "viagens")

    viagens_validas = set(dados["viagens"]["viagem_id"])
    problemas += _checar_duplicados(dados["ocorrencias"], "ocorrencia_id", "ocorrencias")
    problemas += _checar_fk(dados["ocorrencias"], "viagem_id", viagens_validas, "ocorrencias")
    problemas += _checar_intervalo(dados["ocorrencias"], "custo_ocorrencia", 0, 100000, "ocorrencias")

    return problemas
