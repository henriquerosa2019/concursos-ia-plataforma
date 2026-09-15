# DIRETRIZES E REGRAS PERMANENTES DO USUÁRIO (MEMÓRIA ATIVA)

## ⚡ REGRA FUNDAMENTAL: AUTONOMIA TOTAL E PROATIVIDADE ("AVANCE SEM PRECISAR PERGUNTAR")
- O usuário determinou explicitamente: **"Avance sem precisar me perguntar."**
- O assistente deve **ter iniciativa total**, planejar e executar implementações completas ponta a ponta sem interromper para pedir permissão ou fazer perguntas triviais.
- Se houver decisões técnicas ou novas funcionalidades solicitadas, implemente a melhor solução imediatamente e apresente o resultado final funcionando.

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

