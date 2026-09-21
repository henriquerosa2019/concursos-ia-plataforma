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


