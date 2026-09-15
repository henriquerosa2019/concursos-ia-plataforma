# 🎓 Plataforma Definitiva de Estudos para Concursos Públicos
### Inteligência Artificial • Metodologia dos 4 Pilares • Supabase • Deploy Vercel

Uma plataforma de alta retenção mnemônica desenvolvida sob medida para preparação de concursos públicos (Cebraspe, FGV, FCC, Vunesp). Conecta extração de videoaulas do YouTube e PDFs a uma arquitetura moderna em nuvem com **Supabase** e publicação instantânea no **GitHub** e **Vercel**.

---

## ⚡ Os 4 Pilares de Alta Retenção

1. **Pilar 1 — Resumo Estruturado & Conceitos-Chave:** Sintaxe, definições formais, regras, parâmetros e funcionamento (disponível em Modo Leitura Apostila/Word e Leitura Contínua, com temas Claro/Escuro).
2. **Pilar 2 — Raio-X de Banca & Pegadinhas:** Análise crítica de pegadinhas frequentes de bancas examinadoras.
3. **Pilar 3 — Esquematização & Flashcards (Anki):** Cartões otimizados para Repetição Espaçada (SM-2 nativo) e exportação `.txt` direta para o Anki.
4. **Pilar 4 — Mini-Simulado de Fixação:** Questões inéditas estilo banca com cronômetro oficial Cebraspe (1 errada anula 1 certa) e caderno de erros persistente.
5. **⭐ Momentos-Chave com Minutagem Real:** Mapeamento exato segundo a segundo das falas do professor, abrindo o YouTube no instante exato da explicação.

---

## ☁️ Configuração do Banco de Dados no Supabase (1 Clique)

Para ter o banco de dados na nuvem e eliminar qualquer inconsistência de pastas locais:

1. Crie uma conta gratuita em [supabase.com](https://supabase.com) e crie um novo projeto.
2. No menu lateral do Supabase, clique em **SQL Editor**.
3. Abra o arquivo [`supabase_schema.sql`](supabase_schema.sql) deste repositório, cole no SQL Editor e clique em **Run**.
4. Vá em **Project Settings** ➔ **API** e copie:
   - **Project URL** (ex: `https://xyz.supabase.co`)
   - **anon / public key**
5. No painel de estudos (ou no arquivo `config.json`), clique no botão **☁️ Supabase** na barra superior e cole sua URL e Chave.
6. Clique em **🚀 Sincronizar Tudo do Meu Computador para a Nuvem** para subir todas as suas matérias existentes em poucos segundos!

---

## 🚀 Como Publicar no GitHub

Para salvar seu projeto no GitHub:

1. Abra o terminal na pasta do projeto:
   ```bash
   git add .
   git commit -m "feat: Versão completa com Supabase e Vercel"
   ```
2. Crie um novo repositório no seu [GitHub](https://github.com/new) (ex: `concursos-ia-plataforma`).
3. Vincule e envie os arquivos:
   ```bash
   git remote add origin https://github.com/SEU_USUARIO/concursos-ia-plataforma.git
   git branch -M main
   git push -u origin main
   ```

---

## 🌐 Como Publicar na Vercel (Hospedagem Gratuita)

1. Acesse [vercel.com](https://vercel.com) e faça login com sua conta do GitHub.
2. Clique em **Add New...** ➔ **Project** e selecione o repositório `concursos-ia-plataforma`.
3. Na seção **Environment Variables**, adicione:
   - `SUPABASE_URL`: sua URL do Supabase
   - `SUPABASE_ANON_KEY`: sua chave pública do Supabase
   - `GEMINI_API_KEY`: sua chave do Google Gemini (opcional, para gerar IA na nuvem)
4. Clique em **Deploy**.
5. Pronto! Em menos de 1 minuto seu aplicativo estará no ar em um link público seguro HTTPS (ex: `https://concursos-ia.vercel.app`) acessível no computador, tablet ou celular!

---

## 💻 Execução Local (Windows)

- Para abrir a plataforma localmente a qualquer momento:
  - Dê duplo clique no atalho na Área de Trabalho: **"Central Concursos IA"**
  - Ou execute `abrir_painel.bat`.
- O servidor local iniciará na porta `http://localhost:8095` com navegador aberto automaticamente.

---

## 📁 Estrutura do Projeto

```
C:\PROJETOS IA\Concursos/
├── index.html                   # Interface do Painel de Estudos (SPA Moderna)
├── servidor.py                  # Servidor Local Python com Multi-IA & REST API
├── supabase_client.py           # Integração nativa Python com o Supabase
├── supabase_schema.sql          # Script SQL completo para criar as tabelas no Supabase
├── vercel.json                  # Roteamento e Serverless Functions para deploy na Vercel
├── package.json                 # Metadados e scripts de build
├── api/
│   └── ai.js                    # Serverless handler para geração com IA na Vercel
├── config.json                  # Configurações locais de chaves e provedores
├── abrir_painel.bat             # Inicializador do servidor local
└── [Disciplinas]/               # Pastas organizadas por Matéria e Conteúdo
    ├── Informatica/Excel/
    ├── Direito_Administrativo/
    └── Raciocinio_Logico/
```

---

## 🛡️ Licença

Distribuído sob a licença MIT. Desenvolvido para máxima aprovação em concursos públicos.
