# INFORMÁTICA PARA CONCURSOS - Aula 01: Microsoft Word & LibreOffice Writer
**Professor:** Prof. Fabrício Melo (Gran Cursos Online)
**Link da Aula:** [Assistir no YouTube](https://www.youtube.com/watch?v=m6CIohBQVwc)  
**Carga Horária:** 50 minutos  
**Categoria:** Pacote Office e Softwares de Escritório  
**Incidência em Provas:** ★★★★★ (Cebraspe, FGV, FCC, Vunesp)

---

## 1. Resumo Estruturado e Conceitos-Chave

### A. Diferenças Críticas de Atalhos: Word (PT-BR) vs. Writer (PT-BR)
As bancas adoram trocar os atalhos do Microsoft Word pelos do LibreOffice Writer (que se baseia nos atalhos em inglês).

| Comando | Microsoft Word (Português) | LibreOffice Writer (Português) | Macete de Memorização |
| :--- | :--- | :--- | :--- |
| **Negrito** | `Ctrl + N` | `Ctrl + B` (Bold) | Word usa a inicial em português; Writer usa a inicial em inglês. |
| **Salvar** | `Ctrl + B` | `Ctrl + S` (Save) | No Word, B é de "salvar" (Back / B-guardar); no Writer, S de Save. |
| **Sublinhado** | `Ctrl + S` | `Ctrl + U` (Underline) | No Word, S é de Sublinhado; no Writer, U de Underline. |
| **Itálico** | `Ctrl + I` | `Ctrl + I` (Italic) | Igual em ambos. |
| **Imprimir** | `Ctrl + P` | `Ctrl + P` (Print) | Igual em ambos. |
| **Localizar** | `Ctrl + L` | `Ctrl + F` (Find) | Word: L de Localizar; Writer: F de Find. |
| **Substituir** | `Ctrl + U` | `Ctrl + H` | Word: U de alterar/substitUir; Writer: H. |
| **Novo Documento** | `Ctrl + O` | `Ctrl + N` (New) | Word: O de "outrO documento"; Writer: N de New. |
| **Abrir Documento** | `Ctrl + A` | `Ctrl + O` (Open) | Word: A de Abrir; Writer: O de Open. |
| **Alinhamento Centralizado** | `Ctrl + E` | `Ctrl + E` | Letra do meio de cEntro. |
| **Alinhamento Justificado** | `Ctrl + J` | `Ctrl + J` | J de Justificar. |

---

### B. Quebras de Página vs. Quebras de Seção
Um dos assuntos mais cobrados pelo Cebraspe e FGV.

1. **Quebra de Página (`Ctrl + Enter`):**
   - Apenas move o ponto de inserção para o topo da página seguinte.
   - **NÃO altera formatações estruturais** (orientação retrato/paisagem, margens, número de colunas, cabeçalho e rodapé continuam idênticos aos da página anterior).

2. **Quebra de Seção:**
   - Cria uma partição independente no documento.
   - **Permite que a nova seção tenha:**
     - Orientação diferente (ex: Página 1 e 2 em Retrato; Página 3 em Paisagem para caber uma tabela grande).
     - Diferentes margens.
     - Cabeçalhos e rodapés desvinculados (ex: numeração de páginas começando apenas no Capítulo 1, sem número na Capa e Sumário).
     - Número de colunas diferente (ex: texto corrido vira 2 colunas jornalísticas na mesma página).
   - **Tipos de Quebra de Seção no Word:**
     - *Próxima Página:* Inicia a nova seção na página subsequente.
     - *Contínua:* Inicia a nova seção na mesma página (ideal para alternar entre 1 e 2 colunas).
     - *Página Par / Página Ímpar:* Muito usado para diagramação de livros frente e verso.

---

### C. Mala Direta (Mail Merge)
- **Definição:** Recurso que permite gerar cartas, envelopes, e-mails ou etiquetas personalizadas em massa a partir de um documento modelo e de uma fonte de dados externa (tabela do Excel, banco de dados Access, contatos do Outlook).
- **Três Elementos Essenciais:**
  1. *Documento Principal:* Contém o texto fixo que será comum a todos os destinatários.
  2. *Fonte de Dados:* A lista estruturada com os campos variáveis (Nome, Endereço, Matrícula).
  3. *Campos de Mesclagem:* Marcadores colocados no documento principal (ex: `<<Nome>>`) que serão substituídos pelos registros individuais.

---

## 2. Pontos Críticos de Banca & Pegadinhas

1. **Inversão de Salvar no Word vs Writer (Cebraspe):**
   - *Pegadinha:* A questão diz que no Microsoft Word o comando `Ctrl + S` salva as alterações do documento ativo.
   - *Verdade:* **Falso!** No Word, `Ctrl + S` aplica o estilo **Sublinhado**! Para salvar é `Ctrl + B`. O `Ctrl + S` salva no LibreOffice Writer e navegadores.

2. **Orientação Paisagem sem Quebra de Seção (FGV):**
   - *Pegadinha:* Um usuário deseja que a página 5 fique na horizontal (paisagem) e as demais na vertical. A banca diz que basta inserir uma quebra de página comum (`Ctrl + Enter`) e clicar em Orientação > Paisagem.
   - *Verdade:* **Falso!** Se não houver **Quebra de Seção**, a alteração de orientação será aplicada a **todo o documento**!

3. **Substituir o Número da Página na Capa (FCC):**
   - *Pegadinha:* Dizer que para não exibir número de página na capa é obrigatório apagar o rodapé da primeira página.
   - *Verdade:* O Word possui a opção nativa "Primeira Página Diferente" no menu Cabeçalho e Rodapé, ou exige a desvinculação da Seção 2 em relação à Seção 1.

---

## 3. Mini-Simulado de Fixação com Gabarito Comentado

### Questão 1 (CEBRASPE)
No Microsoft Word em português, ao pressionar simultaneamente as teclas Ctrl + S sobre um trecho de texto selecionado, o programa salvará o documento em disco no diretório padrão.
- **Gabarito:** **ERRADO**
- **Comentário:** No MS Word em português, `Ctrl + S` aplica o formato **Sublinhado**. O comando de salvar é `Ctrl + B`.

### Questão 2 (FGV)
Para formatar um trecho específico de um relatório em duas colunas, mantendo o restante do texto da mesma página em coluna única, deve-se inserir antes e depois do trecho:
A) Uma quebra de página simples.  
B) Uma quebra de seção contínua.  
C) Um espaçamento de parágrafo duplo.  
D) Uma quebra de linha manual (Shift + Enter).  
- **Gabarito:** **B**
- **Comentário:** A quebra de seção contínua permite alterar a quantidade de colunas na mesma folha sem pular de página.

---

## 4. Esquematização & Flashcards (Anki)
Importe o arquivo `Flashcards_Word_Anki.txt` para praticar a repetição espaçada.
