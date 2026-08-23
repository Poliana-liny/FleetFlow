"""
FleetFlow - Load
==================
Grava as tabelas processadas em data/processed/.
"""

import pandas as pd

PROCESSED_DIR = "data/processed"


def load_tabela(df: pd.DataFrame, nome: str) -> None:
    df.to_csv(f"{PROCESSED_DIR}/{nome}.csv", index=False)


def load_all(tabelas: dict) -> None:
    for nome, df in tabelas.items():
        load_tabela(df, nome)
