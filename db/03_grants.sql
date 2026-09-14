-- Rôle utilisé par les tools SQL des élèves (palier 2) : LECTURE SEULE.
--
-- Objectif pédagogique : quand on branche un LLM sur une base, on ne lui donne
-- jamais les droits d'écriture « au cas où ». Le moindre privilège n'est pas une
-- précaution théorique, c'est la configuration par défaut.

CREATE ROLE student WITH LOGIN PASSWORD 'student';

GRANT CONNECT ON DATABASE shop TO student;
GRANT USAGE ON SCHEMA public TO student;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO student;

-- Et pour les tables créées plus tard (si le TP est étendu) :
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO student;

-- Explicitement PAS de INSERT / UPDATE / DELETE, et pas d'accès aux séquences.
