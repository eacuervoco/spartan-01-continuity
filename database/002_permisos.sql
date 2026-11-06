-- ContinuitY RF01 - permisos de aplicacion (ejecucion separada, rol administrador)
-- Ejecutar DESPUES de 001_schema.sql y verificar propietarios/roles reales.
-- Las sentencias no revocan permisos existentes ni crean usuarios.
GRANT USAGE ON SCHEMA public TO continuity_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.usuarios, public.credenciales, public.sesiones TO continuity_app;
-- En un endurecimiento posterior revisar REVOKE CREATE ON SCHEMA public FROM continuity_app.
