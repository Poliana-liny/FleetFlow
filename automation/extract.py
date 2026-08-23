"""
FleetFlow - Extract
=====================
Leitura das tabelas brutas em data/raw/, com tipagem correta.
"""

import pandas as pd

RAW_DIR = "data/raw"


def extract_centros() -> pd.DataFrame:
    return pd.read_csv(f"{RAW_DIR}/centros_distribuicao.csv")


def extract_rotas() -> pd.DataFrame:
    return pd.read_csv(f"{RAW_DIR}/rotas.csv")


def extract_transportadoras() -> pd.DataFrame:
    return pd.read_csv(f"{RAW_DIR}/transportadoras.csv")


def extract_veiculos() -> pd.DataFrame:
    return pd.read_csv(f"{RAW_DIR}/veiculos.csv")


def extract_viagens() -> pd.DataFrame:
    df = pd.read_csv(f"{RAW_DIR}/viagens.csv")
    for col in ["data_saida", "data_chegada_prevista", "data_chegada_real"]:
        df[col] = pd.to_datetime(df[col])
    return df


def extract_ocorrencias() -> pd.DataFrame:
    return pd.read_csv(f"{RAW_DIR}/ocorrencias.csv")


def extract_all() -> dict:
    return {
        "centros": extract_centros(),
        "rotas": extract_rotas(),
        "transportadoras": extract_transportadoras(),
        "veiculos": extract_veiculos(),
        "viagens": extract_viagens(),
        "ocorrencias": extract_ocorrencias(),
    }
