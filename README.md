# ⚖️ Tribunal Walker — FDI Moot Arena & Second Brain
### Ecossistema de Alta Performance em Arbitragem de Investimento Internacional
**Oradora / Lead Oralist:** Julia Azevedo Walker  
**Competição Alvo:** *FDI International Arbitration Moot (2026)*

---

## 🌟 Visão Geral do Ecossistema

O **Tribunal Walker** é um ambiente integrado de inteligência jurídica e simulação de sustentação oral projetado especificamente para a preparação de **Julia Azevedo Walker** no *FDI Moot*. O sistema une:

1. **Obsidian Second Brain**: Uma arquitetura de notas em padrão Zettelkasten / Notas Atômicas cobrindo todo o *Record* do caso, memoriais, jurisprudência ICSID/UNCITRAL/PCA, roteiros de discursos e histórico de performance.
2. **Plataforma Web Analítica & Simulador por Voz (Streamlit + Gemini Live)**: Uma arena interativa com bancada de árbitros virtuais dotados de inteligência artificial de ponta (Google Gemini), com interrupções por voz, cronômetro oficial regressivo, rubrica FDI de 100 pontos e conexão semântica direta com o Vault.

---

## 🏛️ Estrutura do Obsidian Vault

```text
Second Brain - Julia Walker/
├── 00_Inbox/                           # Captura rápida de insights e ideias
├── 01_Caso_FDI_Record/                 # Statement of Claim, Defense, PO1/PO2 e Clarifications
├── 02_Memorial_Argumentos/
│   ├── Jurisdiction_Admissibility/     # Salini test, standing, treaty shopping
│   ├── Merits/                         # FET breach, police powers, legitimate expectations
│   ├── Claimant/                       # Roteiros e teses de Claimant
│   └── Respondent/                     # Roteiros e teses de Respondent
├── 03_Jurisprudencia_Tratados/
│   ├── Precedentes_ICSID_PCA/          # Fichas de Salini, Biwater, Methanex, Phoenix Action
│   └── Tratados_Convencoes/            # VCLT Arts 31/32, Convenção ICSID Art. 25
├── 04_Sustentacao_Oral/
│   ├── Discursos_Abertura_Fechamento/  # Roteiros 14m, 10m, 5m e Rebuttal
│   ├── Banco_Perguntas_Arbitros/       # Caderno de objeções e perguntas hostis
│   └── Rubricas_Avaliacao/             # Rubrica oficial FDI Moot 100 pontos
├── 05_Performance_Oral/
│   ├── Caderno_Erros_Orais.md          # Histórico de correções e ajustes finos
│   ├── Metricas_Fluencia.md            # Metas de WPM e tempo de pausa
│   └── Rodadas/                        # Relatórios salvos automaticamente pelo simulador
├── 99_Sistema/Templates/               # Templates em YAML para novas notas
├── dashboard_walker.py                 # Aplicativo Streamlit da Arena
├── iniciar_arena_walker.bat            # Executável de 1-clique para Windows
├── requirements.txt                    # Dependências do projeto
└── README.md                           # Documentação completa
```

---

## 🚀 Como Iniciar em 1-Clique

### Opção 1: Pelo Inicializador Windows (Recomendado)
1. Dê um duplo clique no arquivo **`iniciar_arena_walker.bat`**.
2. O script instalará as dependências ausentes e abrirá a Arena automaticamente no navegador.

### Opção 2: Pelo Terminal / VS Code / Cursor
```bash
cd "C:\Users\franc\OneDrive\Desktop\Second Brain - Julia Walker"
pip install -r requirements.txt
streamlit run dashboard_walker.py
```

---

## 🔑 Configuração da Chave do Google Gemini (Gemini API Key)

Para que a bancada de árbitros virtuais faça as perguntas por voz e emita a nota da Rubrica FDI:

1. Obtenha sua chave gratuita no [Google AI Studio](https://aistudio.google.com/).
2. Você pode inserir a chave de duas maneiras:
   - **Na própria interface Web**: Abra a aba **`⚙️ CONFIGURAÇÃO & API GEMINI`**, cole sua chave no campo e clique em *Salvar Chave*.
   - **Via arquivo `.env` (Permanente)**: Crie um arquivo chamado `.env` na pasta raiz e adicione:
     ```env
     GEMINI_API_KEY="AIzaSySuaChaveAqui..."
     ```

---

## 🎙️ Fluxo de Treino Recomendado para Julia Walker

1. **Seleção de Perfil**: Na barra lateral, escolha se sustentará para **Claimant** ou **Respondent**, o perfil dos árbitros (*Presidente Rigoroso*, *Co-árbitro Técnico* ou *Tribunal Hostil*) e a intensidade da interrupção.
2. **Discurso Inicial**: Ative o microfone ou insira o início da sustentação.
3. **Intervenção Arbitral**: Clique em **`⚡ Submeter & Provocar Árbitros`** para ouvir a interjeição e a pergunta de cross-examination.
4. **Defesa**: Responda à pergunta mantendo a postura forense e aplicando o *Protocolo Ouro* (Saudação -> Resposta Direta em 3s -> Precedente -> Retorno ao Roadmap).
5. **Veredito**: Clique em **`📋 Veredito & Rubrica FDI`** para obter sua nota de 1 a 100, sugestões cirúrgicas de melhoria e salvar automaticamente a rodada no Vault.

---

*Desenvolvido com excelência forense e inteligência artificial de ponta para a consagração de Julia Azevedo Walker no FDI Moot.*
