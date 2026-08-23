"""
FleetFlow - Gerador de Base de Dados Fictícia
================================================
Simula 6 meses de operação de transporte entre Centros de Distribuição
(CD a CD, rotas longas), com frota mista: 1 frota própria + 4
transportadoras terceirizadas.

Diferente do OpsFlow (storytelling "antes x depois"), aqui o recorte é
**comparativo**: entre transportadoras e entre regiões, para responder
perguntas como "quem é mais barato, mas menos confiável?" e "que região
estrutural é mais difícil de operar, independente da transportadora?".

Isso é simulado dando a cada transportadora um "perfil" (custo,
confiabilidade, taxa de ocorrência) e preferência por regiões — algumas
transportadoras atuam nas rotas mais fáceis (Sudeste/Sul), outras nas
rotas estruturalmente mais difíceis (Norte/Nordeste), o que naturalmente
gera diferenças de desempenho que não são só "essa transportadora é
ruim", mas também "essa rota é difícil".

Saídas (CSV, em data/raw/):
    - centros_distribuicao.csv
    - rotas.csv
    - transportadoras.csv
    - veiculos.csv
    - viagens.csv
    - ocorrencias.csv

Execução:
    python generate_data.py
"""

import numpy as np
import pandas as pd
from datetime import date, timedelta

SEED = 7
rng = np.random.default_rng(SEED)

DATA_INICIO = date(2025, 1, 1)
DATA_FIM = date(2025, 6, 30)

OUT_DIR = "/home/claude/fleetflow/data/raw"

# ---------------------------------------------------------------------------
# 1. Centros de Distribuição
# ---------------------------------------------------------------------------

CENTROS = [
    {"cd_id": 1, "nome": "São Paulo", "uf": "SP", "regiao": "Sudeste"},
    {"cd_id": 2, "nome": "Rio de Janeiro", "uf": "RJ", "regiao": "Sudeste"},
    {"cd_id": 3, "nome": "Curitiba", "uf": "PR", "regiao": "Sul"},
    {"cd_id": 4, "nome": "Salvador", "uf": "BA", "regiao": "Nordeste"},
    {"cd_id": 5, "nome": "Goiânia", "uf": "GO", "regiao": "Centro-Oeste"},
    {"cd_id": 6, "nome": "Manaus", "uf": "AM", "regiao": "Norte"},
]


def gerar_centros() -> pd.DataFrame:
    return pd.DataFrame(CENTROS)


# ---------------------------------------------------------------------------
# 2. Rotas (pares de CD, long-haul)
# ---------------------------------------------------------------------------

# distância aproximada (km) — não precisa ser exata, só realista o
# suficiente para dar variação de dificuldade entre rotas
ROTAS_BASE = [
    (1, 2, 430),   # São Paulo - Rio de Janeiro
    (1, 3, 410),   # São Paulo - Curitiba
    (1, 4, 1960),  # São Paulo - Salvador
    (1, 5, 900),   # São Paulo - Goiânia
    (1, 6, 3500),  # São Paulo - Manaus
    (2, 4, 1650),  # Rio de Janeiro - Salvador
    (2, 3, 850),   # Rio de Janeiro - Curitiba
    (3, 5, 1250),  # Curitiba - Goiânia
    (4, 5, 1500),  # Salvador - Goiânia
    (5, 6, 1950),  # Goiânia - Manaus
    (2, 6, 3900),  # Rio de Janeiro - Manaus
    (4, 6, 3300),  # Salvador - Manaus
]


def gerar_rotas() -> pd.DataFrame:
    centros_map = {c["cd_id"]: c for c in CENTROS}
    registros = []
    rota_id = 1
    for origem, destino, dist in ROTAS_BASE:
        # velocidade média varia com a dificuldade estrutural da região
        # (estradas, distância a centros de manutenção, etc.)
        regioes = {centros_map[origem]["regiao"], centros_map[destino]["regiao"]}
        dificil = bool(regioes & {"Norte", "Nordeste"})
        velocidade_media_kmh = 48 if dificil else 58
        tempo_estimado_horas = round(dist / velocidade_media_kmh, 1)

        registros.append({
            "rota_id": rota_id,
            "cd_origem_id": origem,
            "cd_destino_id": destino,
            "distancia_km": dist,
            "tempo_estimado_horas": tempo_estimado_horas,
            "regiao_dificil": dificil,
        })
        rota_id += 1
    return pd.DataFrame(registros)


# ---------------------------------------------------------------------------
# 3. Transportadoras (perfis distintos — base da comparação)
# ---------------------------------------------------------------------------

# custo_km: R$/km cobrado
# confiabilidade: quanto menor, mais variável/atrasado o tempo de viagem
# taxa_ocorrencia: probabilidade-base de ocorrência por viagem
# regioes_preferidas: CDs onde a transportadora atua com mais frequência
TRANSPORTADORAS = [
    {
        "transportadora_id": 1, "nome": "Frota Própria", "tipo": "Própria",
        "custo_km": 4.20, "confiabilidade": 0.90, "taxa_ocorrencia": 0.05,
        "regioes_preferidas": [1, 2, 3],  # Sudeste/Sul
        "n_veiculos": 40,
    },
    {
        "transportadora_id": 2, "nome": "TransRápido Sul", "tipo": "Terceirizada",
        "custo_km": 3.40, "confiabilidade": 0.72, "taxa_ocorrencia": 0.12,
        "regioes_preferidas": [1, 2, 3],  # concorre com a frota própria: mais barata, menos confiável
        "n_veiculos": 30,
    },
    {
        "transportadora_id": 3, "nome": "LogExpress Nacional", "tipo": "Terceirizada",
        "custo_km": 5.10, "confiabilidade": 0.93, "taxa_ocorrencia": 0.04,
        "regioes_preferidas": [1, 2, 4, 5],  # cobertura nacional, foco premium
        "n_veiculos": 25,
    },
    {
        "transportadora_id": 4, "nome": "Rodovias Brasil Cargas", "tipo": "Terceirizada",
        "custo_km": 3.90, "confiabilidade": 0.80, "taxa_ocorrencia": 0.08,
        "regioes_preferidas": [4, 5],  # Nordeste/Centro-Oeste
        "n_veiculos": 30,
    },
    {
        "transportadora_id": 5, "nome": "TransNorte Pesados", "tipo": "Terceirizada",
        "custo_km": 4.60, "confiabilidade": 0.78, "taxa_ocorrencia": 0.10,
        "regioes_preferidas": [5, 6],  # especializada nas rotas mais difíceis (Norte)
        "n_veiculos": 25,
    },
]


def gerar_transportadoras() -> pd.DataFrame:
    cols = ["transportadora_id", "nome", "tipo", "custo_km", "confiabilidade", "taxa_ocorrencia"]
    return pd.DataFrame(TRANSPORTADORAS)[cols]


# ---------------------------------------------------------------------------
# 4. Veículos
# ---------------------------------------------------------------------------

TIPOS_VEICULO = ["Truck", "Carreta", "Bitrem"]


def gerar_veiculos() -> pd.DataFrame:
    registros = []
    veiculo_id = 1
    for transp in TRANSPORTADORAS:
        for _ in range(transp["n_veiculos"]):
            tipo_veiculo = rng.choice(TIPOS_VEICULO, p=[0.35, 0.45, 0.20])
            capacidade_kg = {"Truck": 8000, "Carreta": 27000, "Bitrem": 37000}[tipo_veiculo]
            ano_fabricacao = int(rng.integers(2014, 2025))
            registros.append({
                "veiculo_id": veiculo_id,
                "transportadora_id": transp["transportadora_id"],
                "tipo_veiculo": tipo_veiculo,
                "capacidade_kg": capacidade_kg,
                "ano_fabricacao": ano_fabricacao,
            })
            veiculo_id += 1
    return pd.DataFrame(registros)


# ---------------------------------------------------------------------------
# 5. Viagens (tabela fato principal)
# ---------------------------------------------------------------------------

def _escolher_rota(transp: dict, rotas: pd.DataFrame) -> pd.Series:
    """Rotas que tocam alguma região preferida da transportadora têm mais peso."""
    prefs = set(transp["regioes_preferidas"])
    pesos = rotas.apply(
        lambda r: 3.0 if (r["cd_origem_id"] in prefs or r["cd_destino_id"] in prefs) else 1.0,
        axis=1,
    ).values
    pesos = pesos / pesos.sum()
    idx = rng.choice(rotas.index, p=pesos)
    return rotas.loc[idx]


def gerar_viagens(transportadoras: list, veiculos: pd.DataFrame, rotas: pd.DataFrame):
    registros_viagens = []
    registros_ocorrencias = []
    viagem_id = 1
    ocorrencia_id = 1

    dia = DATA_INICIO
    while dia <= DATA_FIM:
        for transp in transportadoras:
            veiculos_transp = veiculos[veiculos["transportadora_id"] == transp["transportadora_id"]]
            # nem todo veículo roda todo dia — ~35% da frota em viagem por dia
            n_viagens_dia = rng.binomial(len(veiculos_transp), 0.35)

            for _ in range(n_viagens_dia):
                veiculo = veiculos_transp.sample(1).iloc[0]
                rota = _escolher_rota(transp, rotas)

                distancia_km = rota["distancia_km"]
                tempo_estimado_h = rota["tempo_estimado_horas"]

                # confiabilidade menor = mais dispersão e viés de atraso no tempo real
                confiab = transp["confiabilidade"]
                dispersao = (1 - confiab) * 0.6
                vies_atraso = (1 - confiab) * 0.25
                lead_time_horas = max(
                    tempo_estimado_h * 0.7,
                    rng.normal(tempo_estimado_h * (1 + vies_atraso), tempo_estimado_h * dispersao),
                )

                sla_horas = tempo_estimado_h * 1.15  # tolerância de 15% sobre o estimado
                on_time = lead_time_horas <= sla_horas

                custo_por_km = max(1.5, rng.normal(transp["custo_km"], transp["custo_km"] * 0.08))
                custo_frete = round(custo_por_km * distancia_km, 2)

                carga_kg = int(rng.integers(int(veiculo["capacidade_kg"] * 0.5), veiculo["capacidade_kg"] + 1))

                # rotas estruturalmente difíceis aumentam um pouco a chance de ocorrência,
                # além do perfil da própria transportadora
                taxa_ocorrencia = transp["taxa_ocorrencia"] * (1.4 if rota["regiao_dificil"] else 1.0)
                teve_ocorrencia = rng.random() < taxa_ocorrencia

                data_saida = pd.Timestamp(dia) + pd.Timedelta(hours=int(rng.integers(0, 24)))
                data_chegada_prevista = data_saida + pd.Timedelta(hours=tempo_estimado_h)
                data_chegada_real = data_saida + pd.Timedelta(hours=lead_time_horas)

                registros_viagens.append({
                    "viagem_id": viagem_id,
                    "rota_id": int(rota["rota_id"]),
                    "veiculo_id": int(veiculo["veiculo_id"]),
                    "transportadora_id": transp["transportadora_id"],
                    "data_saida": data_saida,
                    "data_chegada_prevista": data_chegada_prevista,
                    "data_chegada_real": data_chegada_real,
                    "distancia_km": distancia_km,
                    "lead_time_horas": round(lead_time_horas, 1),
                    "tempo_estimado_horas": tempo_estimado_h,
                    "on_time": bool(on_time),
                    "custo_frete": custo_frete,
                    "custo_por_km": round(custo_por_km, 2),
                    "carga_kg": carga_kg,
                    "teve_ocorrencia": bool(teve_ocorrencia),
                })

                if teve_ocorrencia:
                    tipo_ocorrencia = rng.choice(
                        ["Avaria", "Atraso por Manutenção", "Sinistro"],
                        p=[0.5, 0.35, 0.15],
                    )
                    gravidade = rng.choice(["Baixa", "Média", "Alta"], p=[0.55, 0.30, 0.15])
                    custo_ocorrencia = {
                        "Baixa": rng.uniform(200, 1500),
                        "Média": rng.uniform(1500, 6000),
                        "Alta": rng.uniform(6000, 25000),
                    }[gravidade]
                    tempo_parado_horas = {
                        "Baixa": rng.uniform(1, 6),
                        "Média": rng.uniform(6, 24),
                        "Alta": rng.uniform(24, 96),
                    }[gravidade]

                    registros_ocorrencias.append({
                        "ocorrencia_id": ocorrencia_id,
                        "viagem_id": viagem_id,
                        "tipo": tipo_ocorrencia,
                        "gravidade": gravidade,
                        "custo_ocorrencia": round(custo_ocorrencia, 2),
                        "tempo_parado_horas": round(tempo_parado_horas, 1),
                    })
                    ocorrencia_id += 1

                viagem_id += 1
        dia += timedelta(days=1)

    return pd.DataFrame(registros_viagens), pd.DataFrame(registros_ocorrencias)


# ---------------------------------------------------------------------------
# Execução
# ---------------------------------------------------------------------------

def main():
    print("Gerando centros de distribuição...")
    centros = gerar_centros()

    print("Gerando rotas...")
    rotas = gerar_rotas()

    print("Gerando transportadoras...")
    transportadoras = gerar_transportadoras()

    print("Gerando veículos...")
    veiculos = gerar_veiculos()

    print("Gerando viagens e ocorrências (pode levar alguns segundos)...")
    viagens, ocorrencias = gerar_viagens(TRANSPORTADORAS, veiculos, rotas)

    centros.to_csv(f"{OUT_DIR}/centros_distribuicao.csv", index=False)
    rotas.to_csv(f"{OUT_DIR}/rotas.csv", index=False)
    transportadoras.to_csv(f"{OUT_DIR}/transportadoras.csv", index=False)
    veiculos.to_csv(f"{OUT_DIR}/veiculos.csv", index=False)
    viagens.to_csv(f"{OUT_DIR}/viagens.csv", index=False)
    ocorrencias.to_csv(f"{OUT_DIR}/ocorrencias.csv", index=False)

    print("\nResumo:")
    print(f"  centros_distribuicao: {len(centros)}")
    print(f"  rotas:                {len(rotas)}")
    print(f"  transportadoras:      {len(transportadoras)}")
    print(f"  veiculos:             {len(veiculos)}")
    print(f"  viagens:              {len(viagens)}")
    print(f"  ocorrencias:          {len(ocorrencias)}")
    print(f"\nArquivos salvos em: {OUT_DIR}")


if __name__ == "__main__":
    main()
