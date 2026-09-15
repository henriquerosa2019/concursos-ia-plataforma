-- ==============================================================================
-- SCHEMA DEFINITIVO SUPABASE - PLATAFORMA DE ESTUDOS PARA CONCURSOS
-- ==============================================================================
-- Execute este script no SQL Editor do seu projeto Supabase (https://supabase.com).
-- Ele cria todas as tabelas com suporte aos 4 Pilares de Estudo, Transcrições,
-- Momentos-Chave, Modo Leitura e Caderno de Erros.

-- Habilitar extensão UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. TABELA DE DISCIPLINAS
CREATE TABLE IF NOT EXISTS public.disciplinas (
    id TEXT PRIMARY KEY, -- ex: 'Informatica', 'Direito_Administrativo', 'Raciocinio_Logico'
    nome TEXT NOT NULL,  -- ex: 'Informática', 'Direito Administrativo'
    icone TEXT DEFAULT '📚',
    ordem INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 2. TABELA DE AULAS / TÓPICOS
CREATE TABLE IF NOT EXISTS public.aulas (
    id TEXT PRIMARY KEY, -- ex: 'informatica_excel', 'raciocinio_logico_proposicoes'
    disciplina_id TEXT REFERENCES public.disciplinas(id) ON DELETE CASCADE,
    subarea TEXT NOT NULL,       -- ex: 'Excel', 'Proposições'
    subarea_slug TEXT NOT NULL,  -- ex: 'excel', 'proposicoes' (normalizado, sem acentos nem espaços)
    titulo TEXT NOT NULL,        -- ex: 'Aula 08 - PROCV - Prof. Danilo Vilanova'
    professor TEXT DEFAULT '',   -- ex: 'Danilo Vilanova'
    tipo TEXT DEFAULT 'video',   -- 'video', 'pdf' ou 'texto'
    youtube_url TEXT DEFAULT '', -- URL do vídeo no YouTube
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_aulas_disciplina ON public.aulas(disciplina_id);
CREATE INDEX IF NOT EXISTS idx_aulas_slug ON public.aulas(subarea_slug);

-- 3. TABELA DE CONTEÚDOS E OS 4 PILARES DE RETENÇÃO
CREATE TABLE IF NOT EXISTS public.conteudos_aulas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    aula_id TEXT UNIQUE REFERENCES public.aulas(id) ON DELETE CASCADE,
    
    -- Pilar 1: Resumo Estruturado & Conceitos Centrais (Markdown)
    pilar1_resumo TEXT DEFAULT '',
    
    -- Pilar 2: Raio-X de Banca & Pegadinhas (Markdown / Análise Cebraspe, FGV, etc.)
    pilar2_raiox TEXT DEFAULT '',
    
    -- Pilar 3: Flashcards de Alta Retenção (JSONB com [{front, back}])
    pilar3_flashcards JSONB DEFAULT '[]'::jsonb,
    
    -- Pilar 4: Mini-Simulado de Fixação (JSONB com [{question, options, answer, explanation, banca}])
    pilar4_simulado JSONB DEFAULT '[]'::jsonb,
    
    -- Momentos-Chave com Minutagem Real (JSONB com [{sec, time_str, title, category, quote, importance}])
    momentos_chave JSONB DEFAULT '[]'::jsonb,
    
    -- Transcrição Cronometrada (JSONB ou texto estruturado)
    transcricao_cronometrada JSONB DEFAULT '[]'::jsonb,
    
    -- Transcrição Completa Contínua
    transcricao_completa TEXT DEFAULT '',
    
    -- Páginas para o Modo Leitura (Apostila / Word / Páginas Individuais)
    leitura_paginas JSONB DEFAULT '[]'::jsonb,
    
    updated_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_conteudos_aula_id ON public.conteudos_aulas(aula_id);

-- 4. TABELA DE PROGRESSO DO ALUNO & CADERNO DE ERROS
CREATE TABLE IF NOT EXISTS public.progresso_aluno (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    aula_id TEXT UNIQUE REFERENCES public.aulas(id) ON DELETE CASCADE,
    concluida BOOLEAN DEFAULT false,
    tempo_estudado_segundos INT DEFAULT 0,
    acertos_simulado INT DEFAULT 0,
    total_simulado INT DEFAULT 0,
    caderno_erros JSONB DEFAULT '[]'::jsonb,
    flashcards_revisados INT DEFAULT 0,
    ultima_revisao TIMESTAMPTZ,
    proxima_revisao TIMESTAMPTZ,
    updated_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- ==============================================================================
-- POLÍTICAS DE ACESSO (ROW LEVEL SECURITY - RLS)
-- Permite leitura e gravação para chaves públicas (anon) e autenticadas.
-- ==============================================================================

ALTER TABLE public.disciplinas ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.aulas ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.conteudos_aulas ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.progresso_aluno ENABLE ROW LEVEL SECURITY;

-- Políticas para acesso público/anon (permite que o app funcione sem login obrigatório)
DROP POLICY IF EXISTS "Permitir leitura pública em disciplinas" ON public.disciplinas;
CREATE POLICY "Permitir leitura pública em disciplinas" ON public.disciplinas FOR SELECT USING (true);
DROP POLICY IF EXISTS "Permitir escrita em disciplinas" ON public.disciplinas;
CREATE POLICY "Permitir escrita em disciplinas" ON public.disciplinas FOR ALL USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Permitir leitura pública em aulas" ON public.aulas;
CREATE POLICY "Permitir leitura pública em aulas" ON public.aulas FOR SELECT USING (true);
DROP POLICY IF EXISTS "Permitir escrita em aulas" ON public.aulas;
CREATE POLICY "Permitir escrita em aulas" ON public.aulas FOR ALL USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Permitir leitura pública em conteudos" ON public.conteudos_aulas;
CREATE POLICY "Permitir leitura pública em conteudos" ON public.conteudos_aulas FOR SELECT USING (true);
DROP POLICY IF EXISTS "Permitir escrita em conteudos" ON public.conteudos_aulas;
CREATE POLICY "Permitir escrita em conteudos" ON public.conteudos_aulas FOR ALL USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Permitir leitura pública em progresso" ON public.progresso_aluno;
CREATE POLICY "Permitir leitura pública em progresso" ON public.progresso_aluno FOR SELECT USING (true);
DROP POLICY IF EXISTS "Permitir escrita em progresso" ON public.progresso_aluno;
CREATE POLICY "Permitir escrita em progresso" ON public.progresso_aluno FOR ALL USING (true) WITH CHECK (true);

-- Inserir disciplinas padrão se não existirem
INSERT INTO public.disciplinas (id, nome, icone, ordem) VALUES
('Informatica', 'Informática', '💻', 1),
('Direito_Administrativo', 'Direito Administrativo', '⚖️', 2),
('Direito_Constitucional', 'Direito Constitucional', '📜', 3),
('Raciocinio_Logico', 'Raciocínio Lógico', '🧠', 4),
('Portugues', 'Língua Portuguesa', '✍️', 5)
ON CONFLICT (id) DO NOTHING;
