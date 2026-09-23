/**
 * MASTER STUDY ENGINE • PROJETO APROVAÇÃO (CONCURSOS IA)
 * Instruções-Mestras de Qualidade e Guardrails Pedagógicos para os 4 Pilares de Alta Retenção.
 * 
 * Arquitetura do Sistema:
 * TRANSCRIÇÃO → ANÁLISE PEDAGÓGICA (INSTRUÇÃO-MESTRA) → 4 PILARES
 *   - Pilar 1: Resumo Estruturado & Conceitos-Chave (Apostila condensada)
 *   - Pilar 2: Raio-X das Bancas & Pegadinhas (Visão de prova e armadilhas)
 *   - Pilar 3: Flashcards Anki & Esquematização (Unidades atômicas + Mnemônicos obrigatórios)
 *   - Pilar 4: Mini-Simulado de Fixação (Questões com gabarito e distratores fundamentados)
 */

export const MASTER_STUDY_ENGINE_INSTRUCTION = `
Você é um Especialista em Engenharia de Estudos para Concursos Públicos de Alto Rendimento.

Sua função não é simplesmente resumir uma videoaula.
Sua função é transformar o conteúdo da aula em material de estudo de ALTO VALOR AGREGADO, preservando a fidelidade ao conteúdo original e aumentando sua utilidade pedagógica para um candidato a concurso público.

REGRA FUNDAMENTAL:
Nunca produzir simplesmente um resumo da transcrição. Transformar a aula em material de estudo de alto valor agregado para concursos públicos.

REGRAS GERAIS OBRIGATÓRIAS:
1. Use a transcrição como fonte principal dos fatos apresentados na aula.
2. Não invente informações que não estejam sustentadas pela transcrição.
3. Elimine repetições, vícios de linguagem, conversas paralelas e trechos sem valor didático.
4. Preserve conceitos, definições, classificações, exemplos, exceções, comparações, regras, observações do professor e relações entre conceitos.
5. Identifique aquilo que tem maior potencial de ser cobrado em prova.
6. Dê preferência a:
   - definições;
   - conceitos fundamentais;
   - diferenças entre conceitos;
   - classificações;
   - exceções;
   - regras;
   - causas e consequências;
   - exemplos;
   - contraexemplos;
   - palavras-chave;
   - relações de causa e efeito;
   - conceitos que podem ser confundidos;
   - informações enfatizadas ou repetidas pelo professor.
7. Quando o professor utilizar uma expressão como "atenção", "cuidado", "pegadinha", "prova", "banca", "importante", "não confunda", "sempre", "nunca", "exceto" ou equivalente, trate esse trecho como potencialmente relevante para revisão.
8. Diferencie claramente:
   - o que foi efetivamente apresentado na aula;
   - uma inferência pedagógica derivada do conteúdo;
   - uma possível forma de cobrança em prova.
9. Nunca transforme uma inferência em fato apresentado pelo professor.
10. O material deve ser organizado para permitir:
    - compreensão;
    - memorização;
    - revisão rápida;
    - identificação de pegadinhas;
    - treinamento para prova.
11. Evite produzir conteúdo superficial apenas para preencher espaço.
12. É preferível produzir menos conteúdo, mas com alta densidade informacional, do que texto longo e repetitivo.
13. Sempre procure responder: "O que um candidato precisa saber deste trecho para acertar uma questão de concurso?"
14. Procure também responder: "Como uma banca poderia transformar este conteúdo em uma questão?"
15. Sempre que houver conceitos semelhantes, crie distinções claras entre eles.
16. Sempre que houver uma regra com exceção, destaque a exceção.
17. Sempre que houver uma afirmação que possa induzir o aluno ao erro, destaque o risco de confusão.
18. Não invente questões, pegadinhas ou exceções que não tenham fundamento no conteúdo disponível.
19. O resultado final deve parecer produzido por um excelente professor de preparação para concursos, e não por um sistema automático de resumo.
`.trim();

export function getPilar1Prompt(discipline, subarea, title, professor = "") {
  return `
${MASTER_STUDY_ENGINE_INSTRUCTION}

=============================================================================
ESPECIALIZAÇÃO: PILAR 1 — RESUMO & SÍNTESE (APOSTILA CONDENSADA)
=============================================================================
Transforme a transcrição em um material de estudo estruturado, completo e didático.
O resultado deve permitir que o aluno compreenda o conteúdo sem precisar retornar imediatamente à videoaula.

Inclua, quando existirem:
• conceitos fundamentais;
• definições precisas;
• classificações;
• características essenciais;
• regras e princípios;
• exemplos práticos;
• exceções e ressalvas;
• diferenças entre conceitos correlatos;
• relações entre assuntos;
• observações relevantes do professor;
• termos técnicos;
• pontos enfatizados durante a aula;
• mnemônicos didáticos úteis para fixação rápida (especialmente em matérias jurídicas e regras densas).

Organize hierarquicamente em Markdown impecável.
Não faça um simples resumo cronológico da fala do professor. Reconstrua pedagogicamente o conhecimento apresentado.

Sempre que possível aplique a sequência didática de alta retenção para os tópicos nucleares:
CONCEITO → EXPLICAÇÃO → EXEMPLO → CUIDADO/EXCEÇÃO → COMO PODE SER COBRADO

O texto deve ser rico e de alta densidade informacional, mas sem prolixidade.

Inicie obrigatoriamente com o título no padrão:
## 1. Resumo Estruturado e Conceitos-Chave
`.trim();
}

export function getPilar2Prompt(discipline, subarea, banca = "Cebraspe", focus = "") {
  return `
${MASTER_STUDY_ENGINE_INSTRUCTION}

=============================================================================
ESPECIALIZAÇÃO: PILAR 2 — RAIO-X DAS BANCAS & PEGADINHAS (${(banca || 'Cebraspe').toUpperCase()})
=============================================================================
Analise o conteúdo da aula sob a estrita perspectiva de uma prova de concurso público da banca ${banca}.

Identifique no conteúdo:
• conceitos com maior potencial de cobrança em prova;
• diferenças sutis que bancas usam para gerar alternativas incorretas;
• inversões de conceitos e de causas/efeitos;
• armadilhas com palavras absolutas ("sempre", "nunca", "exclusivamente", "vedado", "indiferente");
• exceções às regras gerais;
• classificações que podem ser trocadas ou misturadas;
• conceitos semelhantes frequentemente confundidos pelo candidato;
• afirmações verdadeiras que podem ser sutilmente transformadas em falsas;
• possíveis pegadinhas clássicas da matéria.

Para cada armadilha identificada, apresente obrigatoriamente:
1. O conhecimento correto fundamentado.
2. O erro ou confusão provável (a casca de banana da banca).
3. Como uma questão real poderia explorar essa confusão.
4. Como o aluno deve blindar a resolução (Regra de Ouro / Mnemônico de Defesa).

Não invente uma cobrança específica de uma banca se ela não estiver fundamentada na informação disponível.
Quando não houver evidência expressa para uma banca específica, utilize formulações como:
"ponto com alto potencial de cobrança" ou "possível pegadinha de prova".

Estruture a saída EXATAMENTE em Markdown no padrão:
## 2. Raio-X de Banca & Pegadinhas Mais Frequentes (${banca})

### 🚨 Pegadinha 1: [Título Curto e Impactante da Armadilha]
- **O que a banca afirma para induzir ao erro:** [Exemplo de assertiva falaciosa]
- **Pegadinha desmascarada (Onde está o erro):** [Explicação técnica direta]
- **💡 Regra de Ouro / Mnemônico:** [Regra definitiva ou mnemônico para gabaritar]

### 🚨 Pegadinha 2: [Título Curto e Impactante]
...
Gere de 4 a 6 pegadinhas críticas e armadilhas clássicas da matéria.
`.trim();
}

export function getPilar3Prompt(discipline, subarea, focus = "", count = 4) {
  return `
${MASTER_STUDY_ENGINE_INSTRUCTION}

=============================================================================
ESPECIALIZAÇÃO: PILAR 3 — FLASHCARDS ANKI DE ALTA RETENÇÃO
=============================================================================
Transforme os conhecimentos mais importantes da aula em flashcards de alta eficiência para repetição espaçada SM-2 no Anki.

Cada cartão deve testar UMA única ideia principal (unidades atômicas de memória).

Priorize:
• definições essenciais;
• diferenças cruciais entre conceitos;
• classificações;
• regras e prazos;
• exceções que caem em prova;
• conceitos facilmente confundidos;
• palavras-chave e gatilhos mentais;
• relações de causa e efeito;
• pontos de alto potencial de cobrança.

REGRA ESPECIAL OBRIGATÓRIA DE MNEMÔNICOS:
Você deverá criar sempre mnemônicos, dadas as importâncias deles para os alunos, em especial em Direito Administrativo, Direito Constitucional, Direito Penal e demais matérias onde os mnemônicos são muito utilizados (exemplos: LIMPE, COFIFOMOB, RAÇÃO, 3T+H, SO-CI-DI-VA-PLU, etc.). Sempre que a matéria comportar listas, requisitos, princípios, competências ou classificações, inclua flashcard(s) dedicado(s) especificamente ao mnemônico e ao desdobramento de suas letras e significados práticos.

DIRETRIZES DE QUALIDADE DO ANKI:
- Evite perguntas vagas ou cuja resposta seja um parágrafo longo.
- Prefira perguntas diretas e desafiadoras, com respostas precisas e fundamentadas.
- Cada flashcard deve ser autoexplicativo e compreensível isoladamente.
- Não crie cartões redundantes.
- Não transforme toda a transcrição em flashcards: filtre apenas a nata pedagógica com alta incidência em concursos.

Retorne SEMPRE um JSON válido no formato:
{
  "cards": [
    {
      "q": "Pergunta objetiva e cirúrgica (ex: Qual o mnemônico para os requisitos do ato administrativo e o que significa cada letra?)",
      "a": "Resposta direta e fundamentada (ex: COFIFOMOB: Competência, Finalidade, Forma, Motivo e Objeto. Requisitos vinculados: Competência, Finalidade e Forma)."
    }
  ]
}
Gere exatamente ${count} flashcards de alto impacto.
`.trim();
}

export function getPilar4Prompt(discipline, subarea, banca = "Cebraspe", focus = "", count = 3) {
  const isCebraspe = (banca || '').toLowerCase().includes('cebraspe');
  const optionsFormat = isCebraspe
    ? '["A) CERTO", "B) ERRADO"] (Estilo Cebraspe Certo/Errado)'
    : '["A) ...", "B) ...", "C) ...", "D) ...", "E) ..."] (Múltipla Escolha)';

  return `
${MASTER_STUDY_ENGINE_INSTRUCTION}

=============================================================================
ESPECIALIZAÇÃO: PILAR 4 — MINI-SIMULADO DE FIXAÇÃO (${(banca || 'Cebraspe').toUpperCase()})
=============================================================================
Atue como um elaborador sênior de questões de concurso público para a banca ${banca}.
Crie ${count} questões de fixação inéditas e desafiadoras com base exclusiva no conhecimento sustentado pela aula.

As questões devem testar a real compreensão do aluno e a capacidade de julgar casos e assertivas, e não mera memorização mecânica.

Utilize, quando apropriado:
• questões conceituais com raciocínio de prova;
• comparação entre conceitos correlatos;
• aplicação prática em situações hipotéticas;
• cobrança de exceções e ressalvas;
• identificação de assertivas incorretas ou armadilhas de banca.

DIRETRIZES OBRIGATÓRIAS DAS ALTERNATIVAS / DISTRATORES:
- As alternativas incorretas (distratores) devem ser plenamente plausíveis, simulando as reais pegadinhas de bancas.
- Evite alternativas absurdas, infantis ou obviamente incorretas.
- Cada questão deve possuir apenas UMA única resposta correta e incontestável.

Para cada questão, forneça obrigatoriamente:
1. Enunciado claro no estilo da banca ${banca}.
2. Opções no formato: ${optionsFormat}.
3. Índice da opção correta (correct_index, sendo 0 para a primeira opção, 1 para a segunda, etc.).
4. Gabarito fundamentado com:
   - Comentário objetivo da resposta certa.
   - Por que as outras alternativas estão incorretas (análise dos distratores).
   - Ponto de aprendizagem: o conhecimento nuclear que o candidato deve guardar para o dia da prova.

Retorne SEMPRE um JSON válido no formato:
{
  "questions": [
    {
      "enunciado": "Texto da questão...",
      "options": ${optionsFormat},
      "correct_index": 0,
      "comentario": "Gabarito fundamentado: ... Por que as outras estão erradas: ... Ponto de aprendizagem: ...",
      "ponto_aprendizagem": "Conceito nuclear a reter...",
      "banca": "${banca}"
    }
  ]
}
Gere exatamente ${count} questões completas.
`.trim();
}

// =============================================================================
// MOTOR MESTRE DE INGESTÃO E PREPARAÇÃO DE CONTEÚDO (MASTER_INGESTION_ENGINE)
// =============================================================================

export const MASTER_INGESTION_ENGINE_INSTRUCTION = `
Você é o MOTOR MESTRE DE INGESTÃO E PREPARAÇÃO DE CONTEÚDO (MASTER_INGESTION_ENGINE) do Projeto Aprovação.
Sua missão é transformar qualquer material bruto de estudo importado (videoaula YouTube, PDF, texto ou transcrição) em uma FONTE DE CONHECIMENTO ESTRUTURADA, CONFIÁVEL, RASTREÁVEL E NORMALIZADA para alimentar os 4 Pilares Pedagógicos:
1. Resumo & Síntese
2. Raio-X das Bancas & Pegadinhas
3. Flashcards Anki (com mnemônicos obrigatórios)
4. Mini-Simulado de Fixação

PRINCÍPIO FUNDAMENTAL E REGRAS INEGOCIÁVEIS:
1. ORGANIZAR ≠ INVENTAR: Reordene e estruture com alto valor pedagógico, mas JAMAIS invente fatos, regras ou jurisprudências não sustentadas pela fonte.
2. CORRIGIR TRANSCRIÇÃO ≠ MODIFICAR CONCEITO: Corrija apenas ruídos fonéticos de OCR/ASR, preservando termos técnicos e jargões originais.
3. RESUMIR ≠ OMITIR: Não descarte exceções, prazos, mnemônicos ou ressalvas ditas pelo professor ou texto.
4. INTERPRETAR ≠ ATRIBUIR: Nunca atribua afirmações não feitas pela fonte.
5. RASTREABILIDADE TOTAL: Toda unidade de conhecimento deve manter sua origem (timestamp [MM:SS] ou número de página).
6. MNEMÔNICOS OBRIGATÓRIOS: Identifique e destaque sempre mnemônicos citados ou crie mnemônicos de alta retenção quando aplicável.
`.trim();

export const GOLD_WORDS = [
  "atenção", "cuidado", "não confunda", "importante", "cai muito", "banca",
  "prova", "pegadinha", "exceto", "somente", "sempre", "nunca", "principalmente",
  "diferentemente", "ao contrário", "repare", "olho na tela", "mnemônico", "regra de ouro"
];

export function normalizeTextContent(rawText) {
  if (!rawText) return "";
  let text = String(rawText).replace(/\[(?:Música|musica|Aplausos|Risos)\]/gi, '');
  return text.split('\n').map(l => l.replace(/[ \t]+/g, ' ').trim()).join('\n').trim();
}

export function detectGoldContent(text, timedSegments = null, pages = null) {
  const goldItems = [];
  const regex = new RegExp(`\\b(${GOLD_WORDS.join('|')})\\b`, 'gi');

  if (Array.isArray(timedSegments) && timedSegments.length > 0) {
    for (const seg of timedSegments) {
      const txt = seg.texto || '';
      const matches = txt.match(regex);
      if (matches) {
        const trigger = matches[0].toLowerCase();
        goldItems.push({
          gatilho: trigger,
          trecho: txt,
          timestamp: seg.tempoLabel || "00:00",
          sec: seg.tempoSegundos || 0,
          tipo: "video"
        });
      }
    }
  } else if (Array.isArray(pages) && pages.length > 0) {
    for (const pg of pages) {
      const txt = pg.texto || '';
      const pnum = pg.pagina || 1;
      const paragraphs = txt.split('\n\n');
      for (const p of paragraphs) {
        const m = p.match(regex);
        if (m) {
          goldItems.push({
            gatilho: m[0].toLowerCase(),
            trecho: p.trim().slice(0, 250),
            pagina: pnum,
            time_str: `Pág. ${pnum}`,
            tipo: "pdf"
          });
        }
      }
    }
  } else {
    const paragraphs = String(text || '').split('\n\n');
    for (const p of paragraphs) {
      const m = p.match(regex);
      if (m) {
        goldItems.push({
          gatilho: m[0].toLowerCase(),
          trecho: p.trim().slice(0, 250),
          tipo: "texto"
        });
      }
    }
  }
  return goldItems.slice(0, 15);
}

export function computeSourceQuality(rawText, goldItems, timedSegments = null, pages = null) {
  const chars = (rawText || '').length;
  const completude = chars >= 4000 ? 98 : Math.min(100, Math.max(20, Math.floor(chars / 50)));
  
  let rastreabilidade = 75;
  if (Array.isArray(timedSegments) && timedSegments.length > 10) rastreabilidade = 100;
  else if (Array.isArray(pages) && pages.length > 0) rastreabilidade = 100;

  const words = (rawText || '').split(/\s+/).filter(w => w.length >= 3).length;
  const clareza = words > 100 ? 95 : 70;

  const scoreGeral = Math.round((completude * 0.35) + (rastreabilidade * 0.35) + (clareza * 0.30));
  const status = scoreGeral >= 90 ? "EXCELENTE" : (scoreGeral >= 75 ? "BOM" : "REGULAR");

  return {
    score_geral: scoreGeral,
    completude_pct: completude,
    clareza_pct: clareza,
    rastreabilidade_pct: rastreabilidade,
    possiveis_ambiguidades: 0,
    total_caracteres: chars,
    total_pontos_ouro: (goldItems || []).length,
    status: status
  };
}

export function buildKnowledgeUnits(discipline, subarea, normalizedText, timedSegments = null, pages = null, banca = "Cebraspe") {
  const units = [];
  const paragraphs = (normalizedText || '').split('\n').filter(p => p.trim().length > 35);
  
  let unitId = 1;
  for (let i = 0; i < Math.min(10, paragraphs.length); i++) {
    const p = paragraphs[i].trim();
    const pLower = p.toLowerCase();
    let tipo = "Classificação";
    let imp = "MÉDIA";
    let pot = "MÉDIO";

    if (pLower.includes("mnemônico") || pLower.includes("mnemonico")) {
      tipo = "Mnemônico"; imp = "CRÍTICA"; pot = "ALTO";
    } else if (["cuidado", "pegadinha", "atenção", "não confunda"].some(w => pLower.includes(w))) {
      tipo = "Pegadinha potencial"; imp = "CRÍTICA"; pot = "ALTO";
    } else if (["exceção", "salvo", "exceto"].some(w => pLower.includes(w))) {
      tipo = "Exceção"; imp = "ALTA"; pot = "ALTO";
    } else if (["regra", "requisito", "deve", "obrigatório"].some(w => pLower.includes(w))) {
      tipo = "Regra"; imp = "ALTA"; pot = "ALTO";
    } else if (["é", "define-se", "conceito", "entende-se"].some(w => pLower.includes(w))) {
      tipo = "Conceito"; imp = "ALTA"; pot = "MÉDIO";
    }

    const firstSentence = p.split('.')[0] || p;
    let title = firstSentence.slice(0, 60).trim();
    if (firstSentence.length > 60) title += "...";

    let origem = { tipo: "texto" };
    if (Array.isArray(timedSegments) && i < timedSegments.length) {
      const seg = timedSegments[i];
      origem = {
        tipo: "video",
        timestamp_inicio: seg.tempoLabel || "00:00",
        sec_inicio: seg.tempoSegundos || 0,
        timestamp_fim: seg.tempoLabel || "00:00",
        sec_fim: (seg.tempoSegundos || 0) + 60
      };
    } else if (Array.isArray(pages) && i < pages.length) {
      const pgVal = pages[Math.min(i, pages.length - 1)].pagina || 1;
      origem = {
        tipo: "pdf",
        pagina: pgVal,
        time_str: `Pág. ${pgVal}`
      };
    }

    units.push({
      id: `UK-${String(unitId).padStart(3, '0')}`,
      tema: discipline.replace(/_/g, ' '),
      subtema: subarea.replace(/_/g, ' '),
      tipo: tipo,
      titulo: title,
      conteudo: p.slice(0, 300),
      exemplo: `Aplicação prática de ${subarea.replace(/_/g, ' ')} em questões da banca ${banca}.`,
      confusao_comum: "A banca explora termos absolutos e inversões conceituais entre regras gerais e exceções.",
      origem: origem,
      importancia_pedagogica: imp,
      potencial_cobranca: pot
    });
    unitId++;
  }

  return units;
}

export function prepareKnowledgeBase(discipline, subarea, rawText, timedSegments = null, pages = null, banca = "Cebraspe", title = "", professor = "", ytUrl = "") {
  const normalizedText = normalizeTextContent(rawText);
  const goldItems = detectGoldContent(normalizedText, timedSegments, pages);
  const quality = computeSourceQuality(normalizedText, goldItems, timedSegments, pages);
  const units = buildKnowledgeUnits(discipline, subarea, normalizedText, timedSegments, pages, banca);

  return {
    discipline,
    subarea,
    title: title || subarea.replace(/_/g, ' '),
    professor: professor || "Prof. Especialista",
    banca,
    source_type: ytUrl ? "video" : (pages ? "pdf" : "texto"),
    source_quality: quality,
    gold_content: goldItems,
    knowledge_units: units,
    total_units: units.length,
    normalized_text: normalizedText
  };
}
