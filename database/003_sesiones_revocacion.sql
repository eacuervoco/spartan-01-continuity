-- BD-04: revocación irreversible de sesiones; compatible con tablas existentes.
-- Ejecutar solo tras revisión, con spartan_admin, en BD de pruebas primero.
BEGIN;
ALTER TABLE public.sesiones
    ADD COLUMN IF NOT EXISTS revocada_en TIMESTAMPTZ;
COMMIT;
