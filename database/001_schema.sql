-- ContinuitY RF01 - BD-02 - esquema inicial v1.0
-- Aplicar explícitamente en continuity_db con rol administrador/migrador.
-- No ejecutar desde el arranque de FastAPI.
BEGIN;

CREATE TABLE public.usuarios (
    id UUID PRIMARY KEY,
    nombre VARCHAR(120) NOT NULL CHECK (length(btrim(nombre)) > 0),
    email_normalizado TEXT NOT NULL UNIQUE
        CHECK (length(btrim(email_normalizado)) > 0 AND email_normalizado = lower(btrim(email_normalizado))),
    creado_en TIMESTAMPTZ NOT NULL,
    estado TEXT NOT NULL DEFAULT 'ACTIVA' CHECK (estado = 'ACTIVA'),
    rol TEXT NOT NULL DEFAULT 'CLIENTE' CHECK (rol = 'CLIENTE')
);

CREATE TABLE public.credenciales (
    usuario_id UUID PRIMARY KEY REFERENCES public.usuarios(id) ON DELETE CASCADE,
    password_hash TEXT NOT NULL CHECK (length(password_hash) > 0)
);

CREATE TABLE public.sesiones (
    token_digest CHAR(64) PRIMARY KEY CHECK (token_digest ~ '^[0-9a-f]{64}$'),
    usuario_id UUID NOT NULL REFERENCES public.usuarios(id) ON DELETE CASCADE,
    creado_en TIMESTAMPTZ NOT NULL,
    expira_en TIMESTAMPTZ NOT NULL,
    ultima_actividad_en TIMESTAMPTZ NOT NULL,
    CONSTRAINT sesiones_fechas_validas CHECK (
        expira_en > creado_en
        AND ultima_actividad_en >= creado_en
        AND ultima_actividad_en <= expira_en
    )
);

CREATE INDEX idx_sesiones_usuario ON public.sesiones(usuario_id);

COMMIT;
