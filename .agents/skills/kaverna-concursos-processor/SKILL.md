---
name: kaverna-concursos-processor
description: >-
  Processamento especializado de apostilas e materiais em PDF do Kaverna Concursos (Prof. Rodrigo Motta),
  garantindo a identificacao precisa do tema, mapa mental semantico correspondente,
  reaproveitamento na integra de questoes reais de concursos anteriores para o Mini-Simulado (Pilar 4)
  e geracao de Flashcards Anki (Pilar 3) com zero reticencias (...) para maxima retencao.
---

# Kaverna Concursos PDF Processor: Mini-Simulados & Flashcards na Íntegra

Esta skill padroniza o fluxo de ingestão e processamento de apostilas do **Kaverna Concursos** (especialmente do **Prof. Rodrigo Motta** e outros docentes da instituição), assegurando que o acervo de questões de provas anteriores presente no PDF seja aproveitado sem perdas ou alterações.

---

## 1. Identificação Automática de Materiais Kaverna

Reconheça a apostila por qualquer uma das assinaturas textuais no cabeçalho, rodapé ou corpo do material:
- `Kaverna Concursos`, `KVERNA 2026`, `KAVERNA`
- `Prof. Rodrigo Motta`, `@profrodrigomotta`, `Professor Rodrigo Motta - Direito Administrativo`
- Marcadores de questões: `JÁ CAIU EM PROVA, MOTTA?`, `JÁ CAIU EM PROVA?`, `EXERCÍCIOS DE FIXAÇÃO`
- Numerações de questões com padrão: `01) (CARGO / ÓRGÃO / ANO / BANCA)` ou `\(\b[A-Z0-9\s/–\-\.]+\)`

---

## 2. Pilar 4: Mini-Simulado com Conteúdo na Íntegra (Regra Inviolável)

Sempre que a fonte for um PDF do Kaverna:
1. **Reaproveitamento 100% Fidedigno:**
   - As questões de provas anteriores contidas na apostila DEVEM ser incorporadas **exatamente como constam no PDF**.
   - **NÃO** resumir o enunciado.
   - **NÃO** alterar as alternativas `(A)`, `(B)`, `(C)`, `(D)`, `(E)` ou itens de `(C) CERTO` / `(E) ERRADO`.
   - **NÃO** inventar questões genéricas enquanto houver questões reais no material.
2. **Preservação do Cabeçalho de Concurso:**
   - Manter o cabeçalho original com Órgão, Cargo, Ano e Banca:
     - Exemplo: `(SEAD-GO / AOCP / 2022)`
     - Exemplo: `(PGM-RECIFE / CEBRASPE / 2022)`
     - Exemplo: `(TJ-RR / FGV / 2024)`
3. **Gabarito e Comentários Fundamentados:**
   - Comentar cada item com base na letra da lei correspondente e nas explicações teóricas do próprio PDF.
4. **Formatação e Segmentação Impecável:**
   - Cada questão deve ser separada individualmente, contendo cabeçalho, enunciado e alternativas interativas próprias.
   - É estritamente vedado aglomerar opções ou múltiplas questões no corpo do enunciado.
   - O motor de extração do PDF preserva quebras de linha (`Td`, `T*`, `ET`) e regex balanceada para literais com parênteses escapados, garantindo que `(A)` a `(E)` não sejam achatados em uma única linha.
   - No frontend, `.quiz-q` possui `white-space: pre-line; line-height: 1.65;` e `normalizeQuizItem` conta com auto-recuperação de opções se embutidas no texto.

---

## 3. Pilar 3: Flashcards Anki Sem Reticências (`...`)

1. **Origem Direta das Questões e Regras:**
   - Cada flashcard deve ser construído a partir das questões reais extraídas e dos pontos mais cobrados nas páginas do material.
2. **Proibição Total de Reticências (`...`):**
   - É expressamente proibido o uso de reticências (`...`) para truncar frases, assertivas ou regras.
   - Pergunta (`q`) e resposta (`a`) devem trazer o texto completo, permitindo ao aluno ler e memorizar os dispositivos normativos e jurisprudenciais por inteiro.
3. **Formatação Anki Tab-Separated:**
   - Manter a compatibilidade com exportação/importação direta no Anki (`pergunta \t resposta`).

---

## 4. Prevenção de Conflitos e Vinculação de Mapa Mental

1. **Auto-Detecção do Tema Exato:**
   - Não utilizar filtros genéricos pela disciplina (ex: não classificar todo material de *Direito Administrativo* como *Poderes Administrativos*).
   - Identificar palavras-chave nucleares do tópico:
     - *Licitações / Lei 14.133* -> Tópico `Licitacoes_Lei_14133` com mapa mental dedicado de Licitações (22 nós).
     - *Atos Administrativos* -> Tópico `Atos_Administrativos`.
     - *Administração Direta e Indireta* -> Tópico `Administracao_Direta_e_Indireta`.
     - *Agentes e Servidores Públicos (Lei 8.112)* -> Tópico específico de Servidores.
2. **Nós do Mapa Mental:**
   - Cada nó deve conter `id`, `titulo`, `tipo` (`root`, `category`, `rule`, `concept`, `comparison`, `exception`, `trap`, `mnemonic`), `pagina` de referência na apostila e `resumo`.

---

## 5. Checklist de Verificação antes de Publicar
- [ ] O tema foi identificado corretamente sem colidir com outros ramos da disciplina?
- [ ] As questões do simulado contêm o enunciado completo com cabeçalho de banca original?
- [ ] As opções (A-E ou Certo/Errado) estão completas e sem cortes?
- [ ] Os flashcards estão livres de qualquer reticência (`...`)?
- [ ] O catálogo `preseeded_topics.json` e seus espelhos foram atualizados?
- [ ] O build de produção (`node build.js`) foi executado com sucesso?
