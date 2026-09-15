# MEMÓRIA & DIRETRIZES DE EXTRAÇÃO PARA CONCURSOS PÚBLICOS
**Área:** `C:\PROJETOS IA\Concursos`  
**Subárea:** `Excel` (e futuras subáreas como `Direito_Constitucional`, `Direito_Administrativo`, `Portugues`, etc.)

---

## 📌 Objetivo do Sistema
Processar aulas em vídeo (YouTube, cursos online, plataformas de concurso), extrair o máximo de conteúdo e gerar materiais de estudo de alto rendimento focados em **acertar questões de concursos públicos**.

---

## 🏛️ Padrão Obrigatório de Estruturação (Os 4 Pilares)
Toda nova extração solicitada deve gerar um documento estruturado contendo:

1. **Resumo Estruturado e Conceitos-Chave:**
   - Definições formais, sintaxes, artigos de lei, teorias e conceitos essenciais;
   - Parâmetros, argumentos e funcionamento interno.
2. **Pontos Críticos de Banca & Pegadinhas:**
   - As armadilhas típicas das bancas (Cebraspe, FGV, Vunesp, FCC, etc.);
   - O que confunde os candidatos e como neutralizar a pegadinha.
3. **Esquematização para Revisão Ativa:**
   - Tabelas comparativas (de/para, diferenças fundamentais);
   - Mnemônicos práticos de fácil memorização;
   - Flashcards prontos no formato compatível com **Anki** (Frente / Verso separados por tabulação).
4. **Mini-Simulado de Fixação com Gabarito Comentado:**
   - Questões inéditas ou adaptadas nos estilos das principais bancas;
   - Resolução detalhada passo a passo de cada alternativa.

---

## 📂 Padrão de Arquivos por Aula Extraída
Cada aula processada dentro de sua respectiva subárea deve conter:
- `Aula_XX_[Tema]_[Professor].md` $\rightarrow$ Material de estudo completo e formatado.
- `Flashcards_[Tema]_Anki.txt` $\rightarrow$ Cartões prontos para importação no Anki.
- `Transcricao_Completa_[Tema].txt` $\rightarrow$ Transcrição textual completa para busca de termos.
- `Transcricao_Cronometrada_[Tema].txt` $\rightarrow$ Transcrição com timestamps para localização rápida no vídeo.

---

## 🛠️ Procedimento Técnico de Extração
1. **Vídeos do YouTube:** Utilizar a biblioteca `youtube_transcript_api` em Python para baixar as legendas oficiais ou geradas automaticamente em português (`pt`, `pt-BR`).
2. **Tratamento de Texto:** Decodificar entidades HTML, ordenar os trechos cronometrados e gerar a versão de texto contínuo.
3. **Análise Pedagógica:** Processar a transcrição identificando os pontos de ênfase do professor, as questões resolvidas em aula e as armadilhas destacadas.
4. **Armazenamento:** Salvar os artefatos diretamente na pasta da disciplina (`C:\PROJETOS IA\Concursos\[Materia]`).
