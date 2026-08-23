-- ============================================================
-- FleetFlow - Carga dos dados brutos no PostgreSQL
-- Rode a partir da raiz do projeto, depois de tables.sql:
--   psql -d fleetflow -f sql/load.sql
-- ============================================================

\copy centros_distribuicao FROM 'data/raw/centros_distribuicao.csv' WITH (FORMAT csv, HEADER true);
\copy rotas FROM 'data/raw/rotas.csv' WITH (FORMAT csv, HEADER true);
\copy transportadoras FROM 'data/raw/transportadoras.csv' WITH (FORMAT csv, HEADER true);
\copy veiculos FROM 'data/raw/veiculos.csv' WITH (FORMAT csv, HEADER true);
\copy viagens FROM 'data/raw/viagens.csv' WITH (FORMAT csv, HEADER true);
\copy ocorrencias FROM 'data/raw/ocorrencias.csv' WITH (FORMAT csv, HEADER true);
