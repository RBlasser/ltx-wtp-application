-- =========================================================================================
-- ESQUEMA DE BASE DE DATOS DEDICADA: LATINEX DATA HUB WTP STANDALONE APP
-- =========================================================================================
-- IMPORTANTE:
-- Esta aplicación es completamente INDEPENDIENTE del portal oficial y NO interactúa ni
-- escribe en 'cm-db'. Posee su propio motor persistente (PostgreSQL o SQLite) para almacenar
-- de forma segura y estructurada todas las respuestas de la evaluación de precios (WTP).
-- =========================================================================================

-- 1. Tabla de Sesiones y Control de Acceso por Token Único (Standalone Auth / Tokens)
CREATE TABLE IF NOT EXISTS wtp_survey_sessions (
    session_id VARCHAR(64) PRIMARY KEY,
    institution_alias VARCHAR(100) NOT NULL, -- Identificador neutral (ej. 'Entidad #1', 'Puesto de Bolsa A')
    market_segment VARCHAR(50) NOT NULL,    -- 'Puesto de Bolsa', 'Banco Comercial', 'Wealth Management', etc.
    invitation_token VARCHAR(128) UNIQUE NOT NULL,
    respondent_role_category VARCHAR(50),   -- 'Decisor de Negocio / Mesa', 'Decisor Técnico / TI'
    is_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- 2. Tabla Principal de Respuestas de Sensibilidad de Precios (Van Westendorp + NMS)
CREATE TABLE IF NOT EXISTS wtp_survey_responses (
    response_id VARCHAR(64) PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL REFERENCES wtp_survey_sessions(session_id) ON DELETE CASCADE,
    
    -- Metadatos de la Evaluación
    institution_alias VARCHAR(100) NOT NULL,
    market_segment VARCHAR(50) NOT NULL,
    respondent_role_category VARCHAR(50) NOT NULL,
    package_code_evaluated VARCHAR(50) NOT NULL,
    
    -- Parámetros de Esfuerzo Operativo y Valor Intrínseco
    manual_hours_per_month NUMERIC(6, 2) NOT NULL DEFAULT 46.0,
    evaluated_intrinsic_value_usd NUMERIC(10, 2) NOT NULL DEFAULT 1415.0,
    
    -- Los 4 Umbrales de Precio de Van Westendorp (USD / mes)
    price_too_cheap NUMERIC(10, 2) NOT NULL,
    price_cheap NUMERIC(10, 2) NOT NULL,
    price_expensive NUMERIC(10, 2) NOT NULL,
    price_too_expensive NUMERIC(10, 2) NOT NULL,
    
    -- Calibración de Probabilidad de Compra (Extensión Newton-Miller-Smith 1..5)
    nms_score_cheap SMALLINT NOT NULL CHECK (nms_score_cheap BETWEEN 1 AND 5),
    nms_score_expensive SMALLINT NOT NULL CHECK (nms_score_expensive BETWEEN 1 AND 5),
    
    -- Interés en Servicios Complementarios (Almacenado como JSON para extensibilidad)
    -- Ej: [{"service_id": "srv_aws_s3_hechos_relevantes", "setup_usd": 500, "monthly_usd": 100}]
    selected_complementary_services JSONB,
    
    -- Notas cualitativas y observaciones
    qualitative_notes TEXT,
    
    -- Timestamps de Auditoría
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- REGLA DE INTEGRIDAD MATEMÁTICA ESTRICTA (VAN WESTENDORP)
    -- Garantiza en el motor de base de datos que jamás existan datos con inconsistencias lógicas
    CONSTRAINT chk_strict_van_westendorp_inequality CHECK (
        price_too_cheap > 0 AND
        price_too_cheap < price_cheap AND
        price_cheap < price_expensive AND
        price_expensive < price_too_expensive
    )
);

-- 3. Catálogo de Servicios Complementarios Configurados
CREATE TABLE IF NOT EXISTS wtp_complementary_services_catalog (
    service_id VARCHAR(50) PRIMARY KEY,
    service_code VARCHAR(30) UNIQUE NOT NULL,
    service_name VARCHAR(150) NOT NULL,
    setup_fee_usd NUMERIC(10, 2) NOT NULL DEFAULT 0.0,
    monthly_fee_usd NUMERIC(10, 2) NOT NULL DEFAULT 0.0,
    is_active BOOLEAN DEFAULT TRUE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Inserción inicial del catálogo de servicios complementarios (Sub-entregable D1.2)
INSERT INTO wtp_complementary_services_catalog (service_id, service_code, service_name, setup_fee_usd, monthly_fee_usd, is_active, description)
VALUES 
    ('srv_whitelabel_terminal', 'SRV-WL-01', 'Dashboard Institucional Interactivo White-Label con Marca Propia', 1800.00, 250.00, TRUE, 'Aplicación interactiva personalizada con buscador de renta fija y marca propia.'),
    ('srv_pipeline_mark_to_market', 'SRV-E2E-02', 'Pipeline E2E de Precios Oficiales', 1200.00, 175.00, TRUE, 'Integración automatizada de precios oficiales vía API para Core/PMS.'),
    ('srv_quickstart_integration', 'SRV-SOW-01', 'Paquete Quick-Start de Consultoría de Integración (SOW)', 1200.00, 0.00, TRUE, 'Hasta 12 horas de ingeniería especializada para conexión M2M.')
ON CONFLICT (service_id) DO NOTHING;

-- 4. Tabla de Snapshots Analíticos del Modelo (Para Historial del Super Admin)
CREATE TABLE IF NOT EXISTS wtp_pricing_analysis_snapshots (
    snapshot_id VARCHAR(64) PRIMARY KEY,
    sample_size INT NOT NULL,
    calculated_pmc NUMERIC(10, 2) NOT NULL, -- Point of Marginal Cheapness (Límite Inferior RAP)
    calculated_opp NUMERIC(10, 2) NOT NULL, -- Optimal Price Point
    calculated_ipp NUMERIC(10, 2) NOT NULL, -- Indifference Price Point
    calculated_pme NUMERIC(10, 2) NOT NULL, -- Point of Marginal Expensiveness (Límite Superior RAP)
    optimal_revenue_price NUMERIC(10, 2) NOT NULL, -- Precio que maximiza el MRR bajo NMS
    expected_mrr_sample NUMERIC(12, 2) NOT NULL,
    snapshot_data JSONB NOT NULL, -- Curvas completas y grilla de precios en formato JSON
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices de Consulta Rápida
CREATE INDEX IF NOT EXISTS idx_wtp_responses_segment ON wtp_survey_responses(market_segment);
CREATE INDEX IF NOT EXISTS idx_wtp_responses_submitted ON wtp_survey_responses(submitted_at);
