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

## 10. Processamento Master de PDFs para Concursos: Pilar 1 — Resumo & Síntese Pedagógica de Alto Valor
Quando a fonte for um arquivo PDF:
- **O PDF é uma FONTE DE CONHECIMENTO**, e a fonte original é a autoridade. O objetivo é transformar o conteúdo extraído do PDF em um material de estudo claro, completo, organizado, didático e de alto valor agregado, reconstruindo pedagogicamente o conhecimento sem inventar nada.
- **Fórmula do Pilar 1:** `Fidelidade à fonte + reconstrução pedagógica + enriquecimento estrutural − invenção`.

### Regra Fundamental de Fidelidade
Utilize somente informações efetivamente presentes na fonte ou claramente derivadas da organização lógica do conteúdo.
NÃO:
1. inventar informações, exemplos, mnemônicos, pegadinhas, regras ou exceções;
2. atribuir ao autor uma interpretação criada pela IA;
3. transformar uma informação comum em "dica do autor";
4. transformar qualquer frase curta ou lista em mnemônico.

### Estrutura Dinâmica do Resumo (Sem Seções Artificiais)
Organizar em estrutura lógica e progressiva:
1. Visão geral do assunto
2. Conceitos fundamentais
3. Definições
4. Classificações
5. Características
6. Regras e requisitos
7. Diferenças entre conceitos
8. Exceções (`⚠️ EXCEÇÃO:` com origem de página)
9. Exemplos presentes na fonte
10. Observações importantes do autor
11. Mnemônicos efetivamente presentes na fonte
12. Pegadinhas/alertas efetivamente mencionados pelo autor
13. Pontos de atenção para revisão
*Não é obrigatório preencher todas as seções. Se determinada categoria não existir na fonte, NÃO criar seção artificial.*

### Distinção Rigorosa de Categorias de Memorização & Alertas:
- 🧠 **Mnemônico do autor:** Somente quando a fonte apresentar uma estrutura/técnica criada especificamente para facilitar a memorização (ex: `ComFiForMob = Competência + Finalidade + Forma + Motivo + Objeto`, sigla/acrônimo deliberado ou palavra formada pelas iniciais). MACETE DE PROVA, lista de conceitos, ou frases como "atenção, isso cai em prova" NÃO são mnemônicos. Se não houver no PDF, NÃO criar seção de mnemônicos do autor.
- 💡 **Dica do autor:** Orientações e observações expressas do professor/autor no PDF que NÃO sejam mnemônicos.
- 🤖 **Mnemônico sugerido pela IA:** Se a IA considerar útil sugerir um mnemônico próprio, deve ficar FORA do conteúdo do autor e ser rotulado explicitamente como `💡 Mnemônico sugerido pela IA`.
- ⚠️ **Pegadinha/alerta do autor:** Somente quando o professor/material efetivamente alertar contra armadilha ou confusão (com página).
- 🔎 **Ponto de confusão identificado pela IA:** Mapeamento complementar de potenciais confusões realizado pela IA para a banca.

### Regra de Tabelas e Quadros
- NUNCA criar uma tabela contendo coluna chamada "Regra Geral do Autor", "Ponto do Professor" ou equivalente se o conteúdo dessa coluna não estiver explicitamente presente na fonte.
- Quando a tabela for uma síntese construída pela IA, identificá-la obrigatoriamente como:
  *"Síntese estruturada pela IA a partir do conteúdo da fonte."*

### Auto-Verificação Obrigatória (Check Final do Pilar 1 antes da entrega)
1. Existe algum mnemônico que não seja realmente um mnemônico? → REMOVER.
2. Existe alguma informação criada pela IA apresentada como sendo do autor? → CORRIGIR.
3. Existe algum "macete de prova" classificado como mnemônico? → REMOVER DA CATEGORIA MNEMÔNICO.
4. Existem frases fragmentadas? → RECONSTRUIR em frases completas e coerentes.
5. Existem conceitos importantes que foram apenas copiados sem explicação? → EXPLICAR com clareza.
6. Alguma exceção foi inventada? → REMOVER.
7. Algum exemplo foi inventado e apresentado como sendo do autor? → CORRIGIR.
8. Alguma tabela ou quadro foi criado pela IA? → Identificar como "Síntese da IA".
9. O resumo permite estudar sem voltar imediatamente ao PDF? → Se não, aprofundar os conceitos fundamentais.
10. O resumo está maior apenas porque repetiu o PDF? → REDUZIR REPETIÇÕES.
11. O resumo está curto porque eliminou conhecimento relevante? → RECUPERAR conteúdo importante.
12. Todos os mnemônicos, dicas e alertas existentes no PDF foram preservados? → VERIFICAR.
