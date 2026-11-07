-- RF02 Bloque 2: ejecutar explícitamente con rol administrador/migrador.
-- Revisar y aprobar el destino antes de aplicar. No ejecutar desde FastAPI.
BEGIN;

CREATE TABLE public.empresas (
    id UUID PRIMARY KEY,
    usuario_id UUID NOT NULL
        REFERENCES public.usuarios(id) ON DELETE RESTRICT,
    nombre VARCHAR(150) NOT NULL
        CHECK (length(btrim(nombre)) > 0),
    nit VARCHAR(20),
    ciudad VARCHAR(100) NOT NULL
        CHECK (length(btrim(ciudad)) > 0),
    sector VARCHAR(100),
    creado_en TIMESTAMPTZ NOT NULL,
    CONSTRAINT empresas_usuario_id_key UNIQUE (usuario_id)
);

GRANT USAGE ON SCHEMA public TO continuity_app;
GRANT SELECT, INSERT ON TABLE public.empresas TO continuity_app;

COMMIT;
