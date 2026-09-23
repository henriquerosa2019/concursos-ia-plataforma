# INFORMATICA - INFORMÁTICA - REDES DE COMPUTADORES
**Professor:** Prof. Fabio Augusto  
**Link da Aula:** [Assistir no YouTube](https://www.youtube.com/watch?v=FkTh68O86Zw)  
**Duração:** 50 minutos  
**Categoria:** Edital de Concursos Públicos  

---

## 1. Resumo Estruturado e Conceitos-Chave

### A. Modelo OSI (7 Camadas) vs Modelo TCP/IP
- **CONCEITO:** Arquiteturas de referência em camadas para comunicação em rede.
- **Mnemônico das 7 Camadas do Modelo OSI (da 1 à 7):**
  - **F**ísica (Bits, cabos, sinais)
  - **E**nlace (Quadros/Frames, endereço MAC, Switch)
  - **R**ede (Pacotes, endereço IP, Roteador)
  - **T**ransporte (Segmentos, portas, TCP e UDP)
  - **S**essão (Estabelecimento e encerramento de conexões)
  - **A**presentação (Criptografia, compressão e formatação)
  - **A**plicação (Interface com o usuário: HTTP, DNS, FTP)
- **Mnemônico:** `F-E-R-T-S-A-A`.

---

### B. Protocolos de Transporte: TCP vs UDP
- **CONCEITO:**
  - **TCP (Transmission Control Protocol):** Orientado à conexão, confiável, garante entrega e ordem dos pacotes por confirmação (Handshake em 3 vias: SYN, SYN-ACK, ACK).
  - **UDP (User Datagram Protocol):** Não orientado à conexão, sem garantia de entrega, sem retransmissão, porém extremamente veloz (streaming, voz sobre IP, jogos online).
- **CUIDADO / EXCEÇÃO:** UDP NÃO retransmite pacotes perdidos! Se houver perda, a aplicação gerencia ou descarta.
- **COMO PODE SER COBRADO:** A banca afirmará que UDP controla fluxo e congestão. Errado: quem faz controle de fluxo e erro é o TCP.

---

## 2. Raio-X de Banca & Pegadinhas Mais Frequentes (Cebraspe)

### 🚨 Pegadinha 1: TCP vs UDP em Transmissões em Tempo Real
- **O que a banca afirma para induzir ao erro:** "Em transmissões de vídeo ao vivo (streaming) e VoIP, emprega-se prioritariamente o protocolo TCP por ser necessária a retransmissão imediata de qualquer pacote perdido."
- **Pegadinha desmascarada (Onde está o erro):** Em streaming e chamadas ao vivo, a velocidade é primordial; um pacote de voz que chega com atraso por retransmissão é inútil. Por isso, usa-se **UDP** (sem handshake e sem retransmissão).
- **💡 Regra de Ouro / Mnemônico:** "Voz e Vídeo correm com UDP (Um Disparo Rápido); Arquivo e Banco conferem com TCP (Tem Confirmação de Pacote)!"

### 🚨 Pegadinha 2: Hub vs Switch vs Roteador
- **O que a banca afirma para induzir ao erro:** "O switch opera na camada de rede com base no protocolo IP, encaminhando pacotes por broadcast para todos os computadores."
- **Pegadinha desmascarada (Onde está o erro):** O **Switch** atua na camada de Enlace (Camada 2) e usa endereços **MAC** físicos; envia dados em unicast pela tabela CAM. Quem atua na camada de rede (Camada 3) com endereço IP é o **Roteador**. Quem manda broadcast burro para todos na camada física é o **Hub**.
- **💡 Regra de Ouro / Mnemônico:** "Hub é burro (broadcast); Switch é esperto (MAC/Enlace); Roteador é inteligente (IP/Rede)!"
