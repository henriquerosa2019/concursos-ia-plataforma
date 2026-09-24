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
- **Regra Fundamental de Preservação (NUNCA DELETAR):** Ao gerar Raio-X / Pegadinhas adicionais para uma aula, é terminantemente proibido deletar ou substituir as que já existem. O sistema deve **apenas acrescentar** as novas pegadinhas abaixo das anteriores, preservando integralmente o acervo acumulado do aluno.
- **Banca e Foco Específico:** Respeitar com rigor a banca examinadora selecionada (Cebraspe, FGV, FCC, Vunesp, etc.) e o foco específico informado pelo usuário no modal.
- **Modelo Obrigatório do Pilar 2 — Raio-X:**
  Para cada ponto importante identificado sob a perspectiva de prova de concurso público:
  1. **O conhecimento correto:** Explicação técnica e direta da regra ou conceito.
  2. **O erro ou confusão provável:** Identificação da confusão, inversão, palavra absoluta ou pegadinha.
  3. **Como uma questão poderia explorar essa confusão:** Formulação ou assertiva da banca para induzir ao erro.
  4. **Como o aluno deve evitar o erro:** Dica definitiva, regra prática ou mnemônico para gabaritar.
- **Precisão e Cautela:** Não inventar cobrança específica de uma banca se não estiver fundamentada na informação disponível. Utilizar fórmulas como *"possível forma de cobrança"* ou *"ponto com potencial de cobrança"* quando a cobrança for doutrinária ou genérica.
- **Bancos Curados de Alta Retenção:**
  1. **Excel / PROCV:** Regra do 3º argumento (número de índice vs letra), omissão do 4º argumento (aproximada 1 vs exata 0), erro `#N/D` vs `#REF!`, busca estritamente para a direita (impossível para a esquerda, exigindo PROCX), maiúsculas/minúsculas indiferentes e aninhamento de funções (`MAIOR`/`SE`).
  2. **Direito Constitucional (Art. 5º):** Mnemônico RAÇÃO (apenas Racismo e Grupos Armados são imprescritíveis), 3T+H (inafiançáveis e insuscetíveis de graça/anistia, mas prescritíveis), Inviolabilidade de domicílio durante a NOITE (ordem judicial NUNCA à noite, apenas durante o DIA).
  3. **Direito Administrativo (Atos):** Mnemônico COFIFOMOB, Convalidação restrita a Forma não essencial e Competência não exclusiva (FO-CO), Anulação (ilegalidade, Ex Tunc) vs Revogação (conveniência/oportunidade, Ex Nunc).
  4. **Redes e Informática:** TCP (orientado à conexão, handshake em 3 vias) vs UDP (não orientado, sem confirmação, veloz), Portas padrão (HTTP 80 vs HTTPS 443, SSH 22, DNS 53).
  5. **Proibição de Templates Genéricos:** Nunca exibir textos ou fallbacks genéricos de direito administrativo em tópicos de informática ou exatas. Priorizar sempre a Seção 2 da aula existente ou o banco curado específico da matéria.

---

## 10. Processamento Master de PDFs para Concursos (Base de Conhecimento Estruturada & Rastreabilidade)
Quando a fonte for um arquivo PDF:
- **O PDF é uma FONTE DE CONHECIMENTO**, não apenas um texto corrido para resumo superficial.
- **Rastreabilidade Pedagógica & Distinção Rigorosa:**
  - `source_type: AUTHOR`: Conteúdo explicitamente ensinado pelo professor/autor no PDF (com número da página e seção de origem).
  - `source_type: AI_INFERENCE`: Organização, agrupamento e deduções lógicas estruturadas diretamente do texto do material.
  - `source_type: AI_SUGGESTION`: Insights inéditos, questões e mnemônicos complementares sugeridos pela IA para prova.
- **Mnemônicos do Autor (ATENÇÃO ESPECIAL):**
  - Identificar e preservar rigorosamente TODOS os mnemônicos, acrônimos e macetes do autor com página de origem.
  - NUNCA atribuir ao autor um mnemônico criado pela IA. Se a IA sugerir um, rotular como *"Mnemônico sugerido pela IA"*.
- **Pegadinhas e Alertas do Autor:**
  - Capturar alertas ("cuidado", "não confunda", "pegadinha", "atenção", palavras restritivas).
  - Rótulo visível na plataforma: 👨‍🏫 `[MATERIAL DO AUTOR - Pág. XX]` vs 🤖 `[ANÁLISE COMPLEMENTAR DA IA]`.
- **Estrutura de Unidades de Conhecimento (`knowledge_unit`):**
  - `conceito`, `definicao`, `explicacao`, `exemplo`, `excecao`, `comparacao`, `palavras_chave`, `mnemonico`, `pegadinha`, `dica_autor`, `potencial_cobranca`, `importancia_pedagogica`, `fonte`, `pagina`, `secao`, `source_type`.
- **Alimentação dos 4 Pilares:**
  - Pilar 1: Resumo hierárquico com definições formais, regras, tabelas comparativas e mnemônicos do autor.
  - Pilar 2: Raio-X separando as pegadinhas explícitas do autor das pegadinhas mapeadas para a banca.
  - Pilar 3: Flashcards de alta retenção contendo a origem (Pág. XX) e os mnemônicos do material.
  - Pilar 4: Mini-simulado inédito focado nos pontos críticos e armadilhas identificadas.
