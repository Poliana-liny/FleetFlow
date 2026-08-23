"""
FleetFlow - Pipeline
======================
Orquestra o ETL completo: extract -> validate -> transform -> load.

Execução (a partir da raiz do projeto):
    python automation/pipeline.py
"""

import logging
import sys
from datetime import datetime

import extract
import validate
import transform
import load

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("logs/pipeline.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("fleetflow.pipeline")


def run():
    inicio = datetime.now()
    logger.info("=== Iniciando pipeline FleetFlow ===")

    logger.info("Etapa 1/4 — Extract")
    dados = extract.extract_all()
    for nome, df in dados.items():
        logger.info(f"  {nome}: {len(df):,} linhas")

    logger.info("Etapa 2/4 — Validate")
    problemas = validate.validar_tudo(dados)
    if problemas:
        logger.warning(f"  {len(problemas)} problema(s) de qualidade encontrado(s):")
        for p in problemas:
            logger.warning(f"    - {p}")
    else:
        logger.info("  Nenhum problema de qualidade encontrado.")

    logger.info("Etapa 3/4 — Transform")
    viagens_enriq = transform.enriquecer_viagens(
        dados["viagens"], dados["rotas"], dados["transportadoras"], dados["centros"]
    )
    ocorrencias_enriq = transform.enriquecer_ocorrencias(dados["ocorrencias"], viagens_enriq)

    kpis_transportadora = transform.gerar_kpis_transportadora(viagens_enriq, ocorrencias_enriq)
    kpis_regiao = transform.gerar_kpis_regiao(viagens_enriq)
    kpis_rota = transform.gerar_kpis_rota(viagens_enriq)

    logger.info(f"  viagens_enriquecidas: {len(viagens_enriq):,} linhas")
    logger.info(f"  kpis_transportadora: {len(kpis_transportadora):,} linhas")
    logger.info(f"  kpis_regiao: {len(kpis_regiao):,} linhas")
    logger.info(f"  kpis_rota: {len(kpis_rota):,} linhas")

    logger.info("Etapa 4/4 — Load")
    load.load_all({
        "centros": dados["centros"],
        "rotas": dados["rotas"],
        "transportadoras": dados["transportadoras"],
        "veiculos": dados["veiculos"],
        "viagens_enriquecidas": viagens_enriq,
        "ocorrencias_enriquecidas": ocorrencias_enriq,
        "kpis_transportadora": kpis_transportadora,
        "kpis_regiao": kpis_regiao,
        "kpis_rota": kpis_rota,
    })
    logger.info("  Tabelas salvas em data/processed/")

    duracao = (datetime.now() - inicio).total_seconds()
    logger.info(f"=== Pipeline concluído em {duracao:.1f}s ===")


if __name__ == "__main__":
    run()
