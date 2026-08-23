-- ============================================================
-- FleetFlow - KPIs agregados
-- kpis.sql: replica em SQL os KPIs comparativos calculados no
-- Python (automation/transform.py) — por transportadora, por
-- dificuldade de região e por rota.
-- ============================================================

DROP VIEW IF EXISTS vw_kpis_transportadora CASCADE;
DROP VIEW IF EXISTS vw_kpis_regiao CASCADE;
DROP VIEW IF EXISTS vw_kpis_rota CASCADE;

CREATE VIEW vw_kpis_transportadora AS
SELECT
    ve.transportadora_id,
    ve.nome,
    ve.tipo,
    COUNT(*)                                    AS viagens,
    ROUND(AVG(ve.on_time::int)::numeric, 4)      AS pct_on_time,
    ROUND(AVG(ve.lead_time_horas)::numeric, 2)   AS lead_time_medio_h,
    ROUND(AVG(ve.atraso_horas)::numeric, 2)      AS atraso_medio_h,
    ROUND(AVG(ve.custo_por_km)::numeric, 2)      AS custo_medio_km,
    ROUND(SUM(ve.custo_frete)::numeric, 2)       AS custo_total_frete,
    ROUND(AVG(ve.teve_ocorrencia::int)::numeric, 4) AS pct_ocorrencia,
    COALESCE(oc.custo_total_ocorrencias, 0)      AS custo_total_ocorrencias,
    ROUND(SUM(ve.custo_frete)::numeric, 2) + COALESCE(oc.custo_total_ocorrencias, 0) AS custo_total_geral
FROM vw_viagens_enriquecidas ve
LEFT JOIN (
    SELECT transportadora_id, ROUND(SUM(custo_ocorrencia)::numeric, 2) AS custo_total_ocorrencias
    FROM vw_ocorrencias_enriquecidas
    GROUP BY transportadora_id
) oc ON ve.transportadora_id = oc.transportadora_id
GROUP BY ve.transportadora_id, ve.nome, ve.tipo, oc.custo_total_ocorrencias
ORDER BY custo_medio_km;

CREATE VIEW vw_kpis_regiao AS
SELECT
    CASE WHEN regiao_dificil THEN 'Norte/Nordeste' ELSE 'Sudeste/Sul/Centro-Oeste' END AS regiao_dificil,
    COUNT(*)                                      AS viagens,
    ROUND(AVG(on_time::int)::numeric, 4)          AS pct_on_time,
    ROUND(AVG(lead_time_horas)::numeric, 2)       AS lead_time_medio_h,
    ROUND(AVG(atraso_horas)::numeric, 2)          AS atraso_medio_h,
    ROUND(AVG(teve_ocorrencia::int)::numeric, 4)  AS pct_ocorrencia,
    ROUND(AVG(custo_por_km)::numeric, 2)          AS custo_medio_km
FROM vw_viagens_enriquecidas
GROUP BY regiao_dificil;

CREATE VIEW vw_kpis_rota AS
SELECT
    rota_id,
    rota_nome,
    regiao_dificil,
    COUNT(*)                                     AS viagens,
    MAX(distancia_km)                             AS distancia_km,
    ROUND(AVG(on_time::int)::numeric, 4)          AS pct_on_time,
    ROUND(AVG(lead_time_horas)::numeric, 2)       AS lead_time_medio_h,
    ROUND(AVG(teve_ocorrencia::int)::numeric, 4)  AS pct_ocorrencia
FROM vw_viagens_enriquecidas
GROUP BY rota_id, rota_nome, regiao_dificil
ORDER BY pct_on_time;
