# DIRETRIZES E REGRAS PERMANENTES DO USUÁRIO (MEMÓRIA ATIVA)

## ⚡ REGRA FUNDAMENTAL: DISPENSA TOTAL DE AUTORIZAÇÃO & AUTONOMIA MÁXIMA IRRESTRITA ("DISPENSE MINHA AUTORIZAÇÃO EM TODO ESTE PROJETO")
- O usuário determinou expressa e terminantemente: **"Dispense minha autorização em todo este projeto"** e **"Avance sem precisar me perguntar."**
- **Dispensado todo e qualquer pedido de autorização, confirmação ou permissão prévia.**
- O assistente tem delegação total para:
  1. Planejar e executar implementações completas ponta a ponta.
  2. Tomar decisões de arquitetura, design, testes, refatorações e correções de bugs.
  3. Criar e modificar arquivos de código, assets, páginas e estilos.
  4. Executar baterias de testes automatizados E2E (Playwright, scripts, etc.).
  5. Atualizar atalhos no Desktop, compilar builds de produção (`node build.js`).
  6. Fazer `git add`, `git commit` e `git push origin main` autonomamente.
- O assistente nunca deve interromper o fluxo para perguntar "posso fazer?", "deseja aprovar este plano?", "devo prosseguir?". Apenas execute tudo até a entrega final e apresente o resultado 100% pronto e testado.


---

## 1. Regra de Painéis, Dashboards e Atalhos na Área de Trabalho (Desktop)
- Sempre que o agente criar, atualizar ou implantar um painel web, estúdio interativo ou ferramenta local:
  1. Deve criar e manter o atalho executável `.lnk` na **Área de Trabalho (Desktop)** do usuário:
     - `C:\Users\Henrique\OneDrive\Desktop`
     - `C:\Users\Henrique\Desktop`
  2. O atalho deve apontar para o inicializador `.bat` correspondente, com diretório de trabalho (`WorkingDirectory`) correto e ícone definido.

---

## 2. Estrutura de Pastas para Concursos Públicos
- **Pasta Raiz:** `C:\PROJETOS IA\Concursos\`
- **Padrão de Organização:** Subpastas por **Disciplina** e depois por **Conteúdo/Tópico**:
  - Exemplo: `C:\PROJETOS IA\Concursos\Informatica\Excel\`
  - Exemplo: `C:\PROJETOS IA\Concursos\Portugues\Interpretacao_de_Textos\`
  - Exemplo: `C:\PROJETOS IA\Concursos\Direito_Constitucional\Artigo_5\`

---

## 3. Metodologia de Extração de Aulas (Os 4 Pilares de Alta Retenção)
Para qualquer aula em vídeo (YouTube ou arquivo) fornecida pelo usuário para estudo de concursos:
1. **Pilar 1 - Resumo Estruturado & Conceitos-Chave:**
   - Sintaxes, definições formais, regras, parâmetros e funcionamento.
2. **Pilar 2 - Raio-X de Banca & Pegadinhas:**
   - Análise crítica das armadilhas mais comuns de bancas (Cebraspe, FGV, FCC, Vunesp).
3. **Pilar 3 - Esquematização & Flashcards (Anki):**
   - Mnemônicos, tabelas comparativas e cartões prontos para importação no Anki (formato tab-separated).
4. **Pilar 4 - Mini-Simulado de Fixação:**
   - Questões estilo banca com gabarito fundamentado passo a passo.

### Arquivos obrigatórios gerados por aula na respectiva subpasta:
- `Aula_XX_[Tema]_[Professor].md` (Material de estudo formatado com os 4 pilares)
- `Flashcards_[Tema]_Anki.txt` (Cartões no padrão do Anki)
- `Transcricao_Cronometrada_[Tema].txt` (Com marcas de tempo em segundos)
- `Transcricao_Completa_[Tema].txt` (Texto contínuo na íntegra)

---

## 4. Painel de Estudos Centralizado com IA Integrada
- Manter o painel em `C:\PROJETOS IA\Concursos\` (`index.html`, `servidor.py`, `abrir_painel.bat`).
- O painel possui botões para:
  - **"✨ Gerar Novos Flashcards com IA"**: Lê a transcrição da aula e gera cartões de alta retenção no Anki.
  - **"⚡ Gerar Novo Simulado com IA"**: Gera novas questões inéditas com filtro por banca (Cebraspe, FGV, etc.) e correção instantânea.

---

## 5. Nome Oficial do Projeto e Domínio de Publicação
- **Nome Oficial do Projeto:** `aprovacao-concursos`
- **Domínio Final na Vercel:** `aprovacao-concursos.vercel.app`
- **Repositório GitHub:** `https://github.com/henriquerosa2019/concursos-ia-plataforma.git`
- **Identidade da Plataforma:** Projeto Aprovação • Método 4 Pilares de Alta Retenção (Resumo, Raio-X, Flashcards Anki, Modo Prova Cebraspe & Caderno de Erros).

---

## 6. Comunicação com o Usuário: Resposta Direta a Perguntas (?) Antes de Ações
- Sempre que o usuário fizer uma pergunta (mensagem contendo `?` ou solicitando dúvidas/informações):
  1. O assistente deve **responder diretamente à pergunta em primeiro lugar**, com clareza e objetividade, antes de apresentar ações, execuções ou códigos.
  2. Priorizar sempre a resposta explicativa imediata à dúvida colocada pelo usuário.

---

## 7. Isolamento Absoluto de Dados de Novos Usuários (Zero Resíduos)
- Todo novo usuário cadastrado na plataforma deve iniciar com a conta 100% virgem e estritamente isolada:
  1. **Proibição de Migração Resíduo:** É terminantemente proibido migrar dados de sessões de teste ou sessões anônimas (`migrateTrialDataToUser`) para contas recém-criadas. Novos alunos iniciam com `cards_details: {}`, `cebraspe_history: []` e quotas zeradas.
  2. **Zero Contaminação de Caderno de Erros:** O Caderno de Erros e revisões nunca deve carregar resíduos de outros usuários gravados em pastas compartilhadas (`revisoes_erros.json`). Cada aluno possui seu isolamento em `userdata/reviews_{user}_...` ou Supabase.
  3. **Preservação dos Arquivos Oficiais de Aula:** Flashcards gerados por IA sob demanda do aluno devem ser associados ao perfil do usuário (`userdata/cards_{user}_...`) e nunca sobrescrever ou poluir os arquivos originais da disciplina (`Flashcards_*.txt`).

---

## 8. Ferramenta Master de Zerar Dados do Usuário (Reset Master no Painel e Supabase)
- O painel Master conta com o botão oficial **"🧹 Zerar Dados"** na tabela de alunos (endpoint `/api/master/user/reset-data`):
  1. Zera instantaneamente todo o progresso de repetição espaçada SM-2 (`progresso_estudos.json` e `progresso_usuario` no Supabase).
  2. Limpa o Caderno de Erros e revisões pendentes (`revisoes_usuario` no Supabase e `userdata/reviews_*`).
  3. Zera os simulados realizados e o histórico de pontuação Cebraspe.
  4. Redefine quotas e limites de importação em `usuarios.json`.
  5. Limpa as chaves no `localStorage` do navegador do aluno.
  6. Finalidade: permitir testes contínuos, limpos e fidedignos com o mesmo e-mail de usuário.

---

## 9. Padrão de Raio-X com Pegadinhas Reais e Aprofundadas da Banca (Pilar 2)
- O botão **"⚡ Gerar Raio-X & Pegadinhas com IA"** deve sempre entregar pegadinhas reais, detalhadas e técnicas da disciplina e banca específica:
  1. **Excel / PROCV:** Regra do 3º argumento (número de índice vs letra), omissão do 4º argumento (aproximada 1 vs exata 0), erro `#N/D` vs `#REF!`, busca estritamente para a direita (impossível para a esquerda, exigindo PROCX), maiúsculas/minúsculas indiferentes e aninhamento de funções (`MAIOR`/`SE`).
  2. **Direito Constitucional (Art. 5º):** Mnemônico RAÇÃO (apenas Racismo e Grupos Armados são imprescritíveis), 3T+H (inafiançáveis e insuscetíveis de graça/anistia, mas prescritíveis), Inviolabilidade de domicílio durante a NOITE (ordem judicial NUNCA à noite, apenas durante o DIA).
  3. **Direito Administrativo (Atos):** Mnemônico COFIFOMOB, Convalidação restrita a Forma não essencial e Competência não exclusiva (FO-CO), Anulação (ilegalidade, Ex Tunc) vs Revogação (conveniência/oportunidade, Ex Nunc).
  4. **Redes e Informática:** TCP (orientado à conexão, handshake em 3 vias) vs UDP (não orientado, sem confirmação, veloz), Portas padrão (HTTP 80 vs HTTPS 443, SSH 22, DNS 53).
  5. **Proibição de Templates Genéricos:** Nunca exibir textos ou fallbacks genéricos de direito administrativo em tópicos de informática ou exatas. Priorizar sempre a Seção 2 da aula existente ou o banco curado específico da matéria.

---

## 10. Instrução-Mestra de Qualidade (MASTER_STUDY_ENGINE) para os 4 Pilares
- **Regra Fundamental Inegociável:** "Nunca produzir simplesmente um resumo da transcrição. Transformar a aula em material de estudo de ALTO VALOR AGREGADO para concursos públicos, preservando a fidelidade ao conteúdo original e aumentando sua utilidade pedagógica para um candidato."
- **Arquitetura:** `TRANSCRIÇÃO → ANÁLISE PEDAGÓGICA (MASTER_STUDY_ENGINE) → 4 PILARES`.
- **Regras Gerais Obrigatórias:**
  1. Use a transcrição como fonte primária dos fatos apresentados na aula, sem inventar informações não sustentadas.
  2. Elimine repetições, vícios de linguagem, conversas paralelas e trechos sem valor didático.
  3. Dê preferência a: definições, conceitos nucleares, diferenças entre conceitos, classificações, exceções, regras, causas e consequências, contraexemplos e palavras-chave.
  4. Trate termos como "atenção", "cuidado", "pegadinha", "prova", "banca", "importante", "não confunda", "sempre", "nunca", "exceto" como prioridade máxima de revisão.
  5. Organize com foco em responder: "O que o candidato precisa saber deste trecho para acertar a questão?" e "Como a banca poderia transformar este conteúdo em questão?".
- **Especialização dos 4 Pilares:**
  - **Pilar 1 (Resumo & Síntese):** Apostila condensada didática. Aplicar sempre a sequência: `CONCEITO → EXPLICAÇÃO → EXEMPLO → CUIDADO/EXCEÇÃO → COMO PODE SER COBRADO`.
  - **Pilar 2 (Raio-X das Bancas & Pegadinhas):** Análise sob perspectiva da banca (Cebraspe, FGV, etc.): 1. Conhecimento correto; 2. Erro/confusão provável; 3. Como a questão explora essa confusão; 4. Regra de Ouro / Mnemônico de Defesa.
  - **Pilar 3 (Flashcards Anki & Esquematização):** Unidades atômicas de memória (uma ideia principal por cartão). **REGRA OBRIGATÓRIA DE MNEMÔNICOS:** "Você deverá criar sempre mnemônicos, dadas as importâncias deles para os alunos, em especial em Direito Administrativo, Direito Constitucional, Direito Penal e demais matérias onde os mnemônicos são muito utilizados."
  - **Pilar 4 (Mini-Simulado de Fixação):** Questões inéditas, distratores plenamente plausíveis, com gabarito fundamentado, explicação de por que os distratores estão errados e ponto de aprendizagem nuclear.

---

## 11. Instrução-Mestra de Ingestão e Preparação de Conteúdo (MASTER_INGESTION_ENGINE)
- **Princípio Fundamental Inegociável:** "Nunca gerar diretamente os quatro pilares a partir de uma entrada bruta sem antes realizar a etapa de INGESTÃO, NORMALIZAÇÃO, ESTRUTURAÇÃO e VALIDAÇÃO do conteúdo."
- **Fluxo Arquitetural Completo:**
  ```
  FONTE ORIGINAL (YouTube / PDF / Texto)
         ↓
  SOURCE_PROCESSOR (Detecção automática de formato e extração)
         ↓
  CONTENT_NORMALIZER (Limpeza de ruídos/vícios sem alterar significado)
         ↓
  KNOWLEDGE_EXTRACTOR (Identificação de conceitos, regras, exceções e pegadinhas)
         ↓
  KNOWLEDGE_UNIT_BUILDER (Construção das Unidades de Conhecimento #UK atômicas)
         ↓
  SOURCE_TRACEABILITY (Vinculação de cada conceito a timestamp [MM:SS] ou página)
         ↓
  QUALITY_CONTROL_ENGINE (Score de Qualidade da Fonte e verificação de conflitos)
         ↓
  BASE DE CONHECIMENTO DA AULA (Fonte única normalizada)
         ↓
  MASTER_STUDY_ENGINE → 4 PILARES (Resumo, Raio-X, Flashcards, Simulado)
         ↓
  EXACT_POINT_ENGINE (Navegação imediata ao ponto exato do vídeo/PDF)
  ```
- **Regras Mandatórias de Fidelidade e Guardrails:**
  1. **ORGANIZAR ≠ INVENTAR:** A IA pode reordenar e estruturar pedagogicamente, mas é estritamente proibido inventar fatos, teorias ou regras não sustentadas pela fonte.
  2. **CORRIGIR TRANSCRIÇÃO ≠ MODIFICAR CONCEITO:** Corrigir apenas falhas fonéticas evidentes de OCR/ASR, preservando termos técnicos e jargões.
  3. **RESUMIR ≠ OMITIR CONHECIMENTO ESSENCIAL:** Não cortar exceções, prazos, mnemônicos ou ressalvas ditas pelo professor.
  4. **INTERPRETAR ≠ ATRIBUIR:** Nunca atribuir afirmações não feitas pelo professor ou autor do documento.
- **Padrão das Unidades de Conhecimento (#UK):**
  Cada unidade atômica extraída deve conter:
  - `id`: Sequencial (#001, #002...)
  - `tema` e `subtema`
  - `tipo`: Conceito, Definição, Regra, Exceção, Classificação, Comparação, Exemplo, Contraexemplo, Causa/Consequência, Fórmula, Palavra-chave ou Pegadinha potencial
  - `conteudo`: Explicação clara e objetiva
  - `exemplo`: Caso concreto
  - `confusao_comum`: Distinção crítica para prova
  - `origem`: Tipo ('video' | 'pdf' | 'texto'), `timestamp_inicio` / `timestamp_fim` (ou `pagina`)
  - `importancia_pedagogica`: CRÍTICA, ALTA, MÉDIA, BAIXA
  - `potencial_cobranca`: ALTO, MÉDIO, BAIXO
- **Detecção de Conteúdo de Ouro (GOLD_CONTENT_DETECTION):**
  Varredura ativa de gatilhos de prova: *"atenção"*, *"cuidado"*, *"não confunda"*, *"importante"*, *"cai muito"*, *"banca"*, *"prova"*, *"pegadinha"*, *"exceto"*, *"somente"*, *"sempre"*, *"nunca"*, *"diferentemente"*, *"ao contrário"*. O sistema registra que o professor enfatizou o ponto sem garantia dogmática de cobrança.
- **Detecção de Conflitos e Incertezas:**
  Se duas partes da fonte apresentarem informações divergentes, a IA não escolhe arbitrariamente: registra o conflito, analisa o contexto e sinaliza a ressalva.
- **Score de Qualidade da Fonte (SOURCE_QUALITY):**
  Cálculo de métricas internas: completude (%), clareza (%), rastreabilidade (%) e potenciais ambiguidades, orientando o rigor pedagógico do motor.
- **Consumo Unificado pelos 4 Pilares:**
  Todos os quatro pilares (Resumo, Raio-X, Flashcards Anki e Simulado) e o recurso Ponto Exato devem OBRIGATORIAMENTE consumir a mesma Base de Conhecimento estruturada, garantindo coerência absoluta de 100% entre todas as ferramentas de estudo.
