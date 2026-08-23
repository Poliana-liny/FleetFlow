-- ============================================================
-- FleetFlow - Modelagem SQL (PostgreSQL)
-- tables.sql: schema físico, chaves e índices de apoio.
-- ============================================================

DROP TABLE IF EXISTS ocorrencias CASCADE;
DROP TABLE IF EXISTS viagens CASCADE;
DROP TABLE IF EXISTS veiculos CASCADE;
DROP TABLE IF EXISTS transportadoras CASCADE;
DROP TABLE IF EXISTS rotas CASCADE;
DROP TABLE IF EXISTS centros_distribuicao CASCADE;

-- ------------------------------------------------------------
-- Centros de Distribuição
-- ------------------------------------------------------------
CREATE TABLE centros_distribuicao (
    cd_id       INTEGER PRIMARY KEY,
    nome        VARCHAR(50) NOT NULL,
    uf          CHAR(2) NOT NULL,
    regiao      VARCHAR(20) NOT NULL
);

-- ------------------------------------------------------------
-- Rotas (pares de CD, long-haul)
-- ------------------------------------------------------------
CREATE TABLE rotas (
    rota_id                INTEGER PRIMARY KEY,
    cd_origem_id           INTEGER NOT NULL REFERENCES centros_distribuicao(cd_id),
    cd_destino_id          INTEGER NOT NULL REFERENCES centros_distribuicao(cd_id),
    distancia_km           NUMERIC(8,1) NOT NULL,
    tempo_estimado_horas   NUMERIC(6,1) NOT NULL,
    regiao_dificil         BOOLEAN NOT NULL
);

-- ------------------------------------------------------------
-- Transportadoras
-- ------------------------------------------------------------
CREATE TABLE transportadoras (
    transportadora_id  INTEGER PRIMARY KEY,
    nome               VARCHAR(50) NOT NULL,
    tipo               VARCHAR(20) NOT NULL CHECK (tipo IN ('Própria', 'Terceirizada')),
    custo_km           NUMERIC(6,2) NOT NULL,
    confiabilidade     NUMERIC(4,3) NOT NULL,
    taxa_ocorrencia    NUMERIC(4,3) NOT NULL
);

-- ------------------------------------------------------------
-- Veículos
-- ------------------------------------------------------------
CREATE TABLE veiculos (
    veiculo_id          INTEGER PRIMARY KEY,
    transportadora_id   INTEGER NOT NULL REFERENCES transportadoras(transportadora_id),
    tipo_veiculo        VARCHAR(20) NOT NULL CHECK (tipo_veiculo IN ('Truck', 'Carreta', 'Bitrem')),
    capacidade_kg       INTEGER NOT NULL,
    ano_fabricacao      SMALLINT NOT NULL
);

CREATE INDEX idx_veiculos_transportadora ON veiculos(transportadora_id);

-- ------------------------------------------------------------
-- Viagens (tabela fato principal)
-- ------------------------------------------------------------
CREATE TABLE viagens (
    viagem_id                BIGINT PRIMARY KEY,
    rota_id                  INTEGER NOT NULL REFERENCES rotas(rota_id),
    veiculo_id               INTEGER NOT NULL REFERENCES veiculos(veiculo_id),
    transportadora_id        INTEGER NOT NULL REFERENCES transportadoras(transportadora_id),
    data_saida                TIMESTAMP NOT NULL,
    data_chegada_prevista     TIMESTAMP NOT NULL,
    data_chegada_real         TIMESTAMP NOT NULL,
    distancia_km              NUMERIC(8,1) NOT NULL,
    lead_time_horas           NUMERIC(8,1) NOT NULL,
    tempo_estimado_horas      NUMERIC(6,1) NOT NULL,
    on_time                   BOOLEAN NOT NULL,
    custo_frete               NUMERIC(10,2) NOT NULL,
    custo_por_km              NUMERIC(6,2) NOT NULL,
    carga_kg                  INTEGER NOT NULL,
    teve_ocorrencia           BOOLEAN NOT NULL
);

CREATE INDEX idx_viagens_data ON viagens(data_saida);
CREATE INDEX idx_viagens_rota ON viagens(rota_id);
CREATE INDEX idx_viagens_transportadora ON viagens(transportadora_id);
CREATE INDEX idx_viagens_veiculo ON viagens(veiculo_id);

-- ------------------------------------------------------------
-- Ocorrências
-- ------------------------------------------------------------
CREATE TABLE ocorrencias (
    ocorrencia_id       BIGINT PRIMARY KEY,
    viagem_id           BIGINT NOT NULL REFERENCES viagens(viagem_id),
    tipo                VARCHAR(30) NOT NULL CHECK (tipo IN ('Avaria', 'Atraso por Manutenção', 'Sinistro')),
    gravidade           VARCHAR(10) NOT NULL CHECK (gravidade IN ('Baixa', 'Média', 'Alta')),
    custo_ocorrencia    NUMERIC(10,2) NOT NULL,
    tempo_parado_horas  NUMERIC(6,1) NOT NULL
);

CREATE INDEX idx_ocorrencias_viagem ON ocorrencias(viagem_id);
