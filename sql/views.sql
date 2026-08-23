-- ============================================================
-- FleetFlow - Views de enriquecimento
-- views.sql: replica em SQL o enriquecimento feito no Python
-- (automation/transform.py).
-- ============================================================

DROP VIEW IF EXISTS vw_viagens_enriquecidas CASCADE;
DROP VIEW IF EXISTS vw_ocorrencias_enriquecidas CASCADE;

CREATE VIEW vw_viagens_enriquecidas AS
SELECT
    v.viagem_id,
    v.rota_id,
    v.veiculo_id,
    v.transportadora_id,
    t.nome                          AS nome,
    t.tipo,
    r.cd_origem_id,
    r.cd_destino_id,
    co.nome                          AS cd_origem_nome,
    co.regiao                        AS regiao_origem,
    cd.nome                          AS cd_destino_nome,
    cd.regiao                        AS regiao_destino,
    co.nome || ' → ' || cd.nome      AS rota_nome,
    r.regiao_dificil,
    v.data_saida,
    v.data_chegada_prevista,
    v.data_chegada_real,
    TO_CHAR(v.data_saida, 'YYYY-MM') AS ano_mes,
    v.distancia_km,
    v.lead_time_horas,
    v.tempo_estimado_horas,
    ROUND((v.lead_time_horas - v.tempo_estimado_horas)::numeric, 1) AS atraso_horas,
    v.on_time,
    v.custo_frete,
    v.custo_por_km,
    v.carga_kg,
    v.teve_ocorrencia
FROM viagens v
JOIN rotas r ON v.rota_id = r.rota_id
JOIN transportadoras t ON v.transportadora_id = t.transportadora_id
JOIN centros_distribuicao co ON r.cd_origem_id = co.cd_id
JOIN centros_distribuicao cd ON r.cd_destino_id = cd.cd_id;

CREATE VIEW vw_ocorrencias_enriquecidas AS
SELECT
    o.ocorrencia_id,
    o.viagem_id,
    ve.transportadora_id,
    ve.nome                          AS transportadora_nome,
    ve.rota_id,
    ve.rota_nome,
    ve.regiao_origem,
    ve.regiao_destino,
    ve.regiao_dificil,
    ve.ano_mes,
    o.tipo,
    o.gravidade,
    o.custo_ocorrencia,
    o.tempo_parado_horas
FROM ocorrencias o
JOIN vw_viagens_enriquecidas ve ON o.viagem_id = ve.viagem_id;
