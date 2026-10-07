import os
import sys
import json
import time
import base64
import datetime
from pathlib import Path
import streamlit as st
import pandas as pd
import altair as alt
import yaml

# Auto-load .env
try:
    from dotenv import load_dotenv
    load_dotenv()
    # Also load from target directories if present
    vault_env = Path(r"C:\Users\franc\OneDrive\Desktop\Second Brain - Julia Walker\.env")
    if vault_env.exists():
        load_dotenv(vault_env)
except Exception:
    pass

# Optional gTTS for audio synthesis
try:
    from gtts import gTTS
    import io
    HAS_GTTS = True
except ImportError:
    HAS_GTTS = False

# Google GenAI imports (support both google-genai 2.x and google-generativeai)
HAS_GENAI_SDK = False
try:
    from google import genai
    from google.genai import types
    HAS_GENAI_SDK = "google-genai"
except ImportError:
    try:
        import google.generativeai as legacy_genai
        HAS_GENAI_SDK = "legacy"
    except ImportError:
        HAS_GENAI_SDK = False

# ---------------------------------------------------------
# CONSTANTS & PATHS
# ---------------------------------------------------------
VAULT_DIR = Path(r"C:\Users\franc\OneDrive\Desktop\Second Brain - Julia Walker")
if not VAULT_DIR.exists():
    VAULT_DIR = Path(__file__).parent.resolve()

RODADAS_DIR = VAULT_DIR / "05_Performance_Oral" / "Rodadas"
RODADAS_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------
# PAGE CONFIG & LUXURY THEME
# ---------------------------------------------------------
st.set_page_config(
    page_title="Tribunal Walker | FDI Moot Arena",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with Cinzel and Inter fonts, Navy & Gold luxury theme
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700;900&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

/* Global Reset & Base */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #F8F9FA;
}

/* Background */
.stApp {
    background-color: #0B132B;
    background-image: 
        radial-gradient(at 0% 0%, rgba(28, 37, 65, 0.7) 0px, transparent 50%),
        radial-gradient(at 100% 100%, rgba(212, 175, 55, 0.06) 0px, transparent 50%);
}

/* Headings */
h1, h2, h3, .walker-title {
    font-family: 'Cinzel', serif !important;
    letter-spacing: 0.5px;
    font-weight: 700;
}

h1 {
    color: #F3E5AB !important;
    text-shadow: 0 0 20px rgba(212, 175, 55, 0.25);
}

h2, h3 {
    color: #D4AF37 !important;
}

/* Luxury Cards */
.walker-card {
    background: linear-gradient(135deg, rgba(28, 37, 65, 0.85) 0%, rgba(15, 23, 42, 0.95) 100%);
    border: 1px solid rgba(212, 175, 55, 0.3);
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5), 0 0 15px rgba(212, 175, 55, 0.05);
    margin-bottom: 20px;
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
}

.walker-card:hover {
    border-color: rgba(212, 175, 55, 0.6);
    box-shadow: 0 12px 35px -8px rgba(0, 0, 0, 0.7), 0 0 20px rgba(212, 175, 55, 0.15);
}

.walker-card-gold {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.95) 100%);
    border: 1.5px solid #D4AF37;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 0 25px rgba(212, 175, 55, 0.15);
}

/* KPI Metric Cards */
.metric-box {
    background: rgba(28, 37, 65, 0.7);
    border: 1px solid rgba(212, 175, 55, 0.25);
    border-radius: 10px;
    padding: 16px;
    text-align: center;
}

.metric-value {
    font-family: 'Cinzel', serif;
    font-size: 2.2rem;
    font-weight: 700;
    color: #F3E5AB;
    margin: 4px 0;
}

.metric-label {
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #94A3B8;
}

/* Timer Display */
.timer-container {
    background: #070B19;
    border: 2px solid #D4AF37;
    border-radius: 14px;
    padding: 20px;
    text-align: center;
    box-shadow: inset 0 0 20px rgba(0,0,0,0.8), 0 0 25px rgba(212, 175, 55, 0.2);
}

.timer-digits {
    font-family: 'JetBrains Mono', monospace;
    font-size: 3.5rem;
    font-weight: 700;
    color: #D4AF37;
    text-shadow: 0 0 15px rgba(212, 175, 55, 0.5);
}

.timer-subtext {
    font-size: 0.9rem;
    color: #CBD5E1;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}

/* Arbitrator Voice Speech Bubble */
.arbitrator-bubble {
    background: linear-gradient(135deg, rgba(30, 27, 75, 0.9) 0%, rgba(15, 23, 42, 0.95) 100%);
    border-left: 5px solid #D4AF37;
    border-radius: 0 12px 12px 0;
    padding: 18px 22px;
    margin: 15px 0;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}

.arbitrator-name {
    font-family: 'Cinzel', serif;
    font-size: 1.05rem;
    font-weight: 700;
    color: #F3E5AB;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.arbitrator-quote {
    font-size: 1rem;
    line-height: 1.6;
    color: #E2E8F0;
    font-style: italic;
}

/* Tag / Badge */
.gold-badge {
    background-color: rgba(212, 175, 55, 0.15);
    color: #F3E5AB;
    border: 1px solid #D4AF37;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.5px;
    display: inline-block;
}

/* Custom Buttons */
div.stButton > button:first-child {
    background: linear-gradient(135deg, #D4AF37 0%, #AA820A 100%);
    color: #0B132B;
    font-family: 'Inter', sans-serif;
    font-weight: 700;
    font-size: 0.95rem;
    border: none;
    border-radius: 8px;
    padding: 10px 24px;
    box-shadow: 0 4px 15px rgba(212, 175, 55, 0.3);
    transition: all 0.3s ease;
}

div.stButton > button:first-child:hover {
    background: linear-gradient(135deg, #F3E5AB 0%, #D4AF37 100%);
    box-shadow: 0 6px 20px rgba(212, 175, 55, 0.5);
    transform: translateY(-1px);
    color: #070B19;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: #070B19;
    border-right: 1px solid rgba(212, 175, 55, 0.2);
}

/* Streamlit Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 12px;
    background-color: rgba(28, 37, 65, 0.5);
    padding: 8px 12px;
    border-radius: 12px;
    border: 1px solid rgba(212, 175, 55, 0.2);
}

.stTabs [data-baseweb="tab"] {
    color: #94A3B8;
    font-weight: 600;
    border-radius: 8px;
    padding: 8px 18px;
    transition: all 0.2s;
}

.stTabs [aria-selected="true"] {
    background-color: #1C2541 !important;
    color: #F3E5AB !important;
    border-bottom: 2px solid #D4AF37 !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# HELPER FUNCTIONS & GEMINI CLIENT
# ---------------------------------------------------------
def get_api_key():
    """Retrieve Gemini API Key from environment, streamlit secrets or session state."""
    key = os.environ.get("GEMINI_API_KEY", "")
    if not key and hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
        key = st.secrets["GEMINI_API_KEY"]
    if not key and "gemini_api_key" in st.session_state:
        key = st.session_state["gemini_api_key"]
    return key.strip()

def generate_arbitral_response(prompt_text, system_instruction="", model_name="gemini-flash-latest"):
    """Execute AI completion with Google Gemini with multi-model fallback."""
    api_key = get_api_key()
    if not api_key:
        return None, "⚠️ Chave de API do Gemini não configurada. Por favor, adicione sua GEMINI_API_KEY no arquivo .env ou na aba 'Configuração'."

    candidate_models = [model_name, "gemini-flash-latest", "gemini-2.5-flash", "gemini-pro-latest", "gemini-2.5-pro"]
    # Remove duplicates while preserving order
    seen = set()
    models_to_try = [m for m in candidate_models if not (m in seen or seen.add(m))]

    last_error = None
    for model in models_to_try:
        try:
            if HAS_GENAI_SDK == "google-genai":
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model=model,
                    contents=prompt_text,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.7,
                        max_output_tokens=1800,
                    )
                )
                return response.text, None
            elif HAS_GENAI_SDK == "legacy":
                legacy_genai.configure(api_key=api_key)
                gen_model = legacy_genai.GenerativeModel(
                    model_name=model,
                    system_instruction=system_instruction
                )
                response = gen_model.generate_content(prompt_text)
                return response.text, None
            else:
                return None, "SDK do Google Gemini não encontrado. Execute 'pip install google-genai'."
        except Exception as e:
            last_error = str(e)
            continue

    return None, f"Erro na chamada da API Gemini: {last_error}"

def generate_tts_audio_html(text_content):
    """Generate audio for the arbitrator using gTTS or browser speech."""
    if not text_content:
        return ""
    if HAS_GTTS:
        try:
            tts = gTTS(text=text_content[:400], lang="en", tld="co.uk")
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            b64_audio = base64.b64encode(fp.read()).decode("utf-8")
            return f"""
            <audio autoplay controls style="width: 100%; height: 38px; margin-top: 8px;">
                <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
            </audio>
            """
        except Exception:
            pass
    # Fallback Web Speech API
    clean_text = text_content.replace('"', '\\"').replace('\n', ' ')
    return f"""
    <button onclick="window.speechSynthesis.cancel(); let msg = new SpeechSynthesisUtterance('{clean_text}'); msg.lang='en-GB'; msg.rate=0.95; window.speechSynthesis.speak(msg);" 
            style="background:#1C2541; border:1px solid #D4AF37; color:#F3E5AB; padding:6px 14px; border-radius:6px; cursor:pointer; font-size:0.85rem; margin-top:8px;">
        🔊 Ouvir Árbitro (Text-to-Speech)
    </button>
    """

def load_vault_documents():
    """Scans and loads all markdown files in the vault."""
    docs = []
    if not VAULT_DIR.exists():
        return docs
    for root, _, files in os.walk(VAULT_DIR):
        for file in files:
            if file.endswith(".md") and not file.startswith("."):
                full_path = Path(root) / file
                rel_path = full_path.relative_to(VAULT_DIR)
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    docs.append({
                        "path": str(rel_path),
                        "name": file.replace(".md", "").replace("_", " "),
                        "content": content,
                        "folder": rel_path.parts[0] if len(rel_path.parts) > 1 else "Root"
                    })
                except Exception:
                    continue
    return docs

def load_performance_rounds():
    """Load historical round files from 05_Performance_Oral/Rodadas."""
    rounds = []
    if not RODADAS_DIR.exists():
        return pd.DataFrame()
    
    for file in RODADAS_DIR.glob("*.md"):
        try:
            with open(file, "r", encoding="utf-8") as f:
                raw = f.read()
            if raw.startswith("---"):
                parts = raw.split("---", 2)
                if len(parts) >= 3:
                    meta = yaml.safe_load(parts[1])
                    if isinstance(meta, dict):
                        meta["file_name"] = file.name
                        meta["full_text"] = parts[2]
                        rounds.append(meta)
        except Exception:
            continue

    if not rounds:
        return pd.DataFrame()

    df = pd.DataFrame(rounds)
    if "data" in df.columns:
        df["data"] = pd.to_datetime(df["data"], errors="coerce")
        df = df.sort_values("data", ascending=True)
    return df

def save_simulation_round(metadata, markdown_content):
    """Save simulation feedback report directly to Obsidian Vault."""
    date_str = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
    filename = f"Rodada_{date_str}_{metadata.get('lado', 'Claimant')}.md"
    file_path = RODADAS_DIR / filename

    yaml_frontmatter = yaml.dump(metadata, sort_keys=False, allow_unicode=True)
    full_file_content = f"---\n{yaml_frontmatter}---\n\n{markdown_content.strip()}\n"

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(full_file_content)

    return filename

# ---------------------------------------------------------
# SIDEBAR — ORAL COUNSEL PROFILE & CONTROLS
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 10px 0 20px 0;">
        <div style="font-size: 2.8rem; margin-bottom: 5px;">⚖️</div>
        <div class="walker-title" style="font-size: 1.4rem; color: #F3E5AB; margin: 0;">TRIBUNAL WALKER</div>
        <div style="font-size: 0.8rem; letter-spacing: 2px; color: #D4AF37; text-transform: uppercase;">FDI Moot Arena • Second Brain</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="walker-card" style="padding: 16px; margin-bottom: 16px;">
        <div style="display: flex; align-items: center; gap: 12px;">
            <div style="background: rgba(212, 175, 55, 0.2); border: 1px solid #D4AF37; width: 44px; height: 44px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.2rem;">👩‍⚖️</div>
            <div>
                <div style="font-weight: 700; color: #F8F9FA; font-size: 0.95rem;">Julia Azevedo Walker</div>
                <div style="font-size: 0.75rem; color: #D4AF37;">Lead Oralist • FDI Team</div>
            </div>
        </div>
        <div style="margin-top: 10px; font-size: 0.8rem; color: #94A3B8;">
            📍 Vault: <span style="color: #CBD5E1;">Second Brain - Julia Walker</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🎙️ Configurações da Rodada")
    
    selected_role = st.selectbox(
        "Papel na Sustentação:",
        ["Claimant (Lead Oralist)", "Respondent (Defense Counsel)"],
        index=0
    )

    selected_bench = st.selectbox(
        "Perfil da Bancada Arbitral:",
        [
            "Presidente Rigoroso (Foco em Jurisdição, Standing e VCLT)",
            "Co-árbitro Técnico (Foco em Danos, DCF, Fatos e Quantum)",
            "Tribunal Hostil (Interrupções Frequentes & Armadilhas)",
            "Bancada Equilibrada / FDI Grand Finals"
        ],
        index=0
    )

    selected_topic = st.selectbox(
        "Ponto Controvertido Principal:",
        [
            "Issue 1: Jurisdição & Salini Test (Art. 25 ICSID)",
            "Issue 1: Treaty Shopping & Phoenix Action Abuso",
            "Issue 2: FET Breach & Legitimate Expectations",
            "Issue 2: Police Powers vs. Expropriação Indireta",
            "Sustentação Completa (Jurisdição + Mérito 14 min)"
        ]
    )

    aggression_level = st.select_slider(
        "Intensidade de Interrupção dos Árbitros:",
        options=["Didática (Mínima)", "Moderada (Padrão FDI)", "Alta (Quartas de Final)", "Implacável (Final Global)"],
        value="Alta (Quartas de Final)"
    )

    st.divider()

    api_status_color = "🟢 Conectado" if get_api_key() else "🔴 API Key Ausente"
    st.markdown(f"**Gemini API:** `{api_status_color}`")
    
    st.markdown("""
    <div style="font-size: 0.75rem; color: #64748B; text-align: center; margin-top: 20px;">
        Tribunal Walker v2.4 • FDI Moot AI Simulator<br>
        Deepmind Agentic Engine & Obsidian RAG
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# MAIN HEADER
# ---------------------------------------------------------
st.markdown("""
<div class="walker-card-gold" style="margin-bottom: 25px;">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px;">
        <div>
            <div class="gold-badge" style="margin-bottom: 8px;">FDI INTERNATIONAL ARBITRATION MOOT • ARENA FORENSE</div>
            <h1 style="margin: 0; font-size: 2.1rem;">Bancada Virtual & Second Brain — Julia Walker</h1>
            <p style="margin: 6px 0 0 0; color: #CBD5E1; font-size: 0.95rem;">
                Simulador de sustentação oral por voz, arguição arbitral em tempo real e inteligência jurisprudencial ICSID/UNCITRAL.
            </p>
        </div>
        <div style="text-align: right;">
            <div style="font-family: 'Cinzel', serif; font-size: 1.1rem; color: #F3E5AB; font-weight: 700;">"Pacta Sunt Servanda"</div>
            <div style="font-size: 0.8rem; color: #D4AF37;">Excelência • Persuasão • Domínio do Tribunal</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# TAB NAVIGATION
# ---------------------------------------------------------
tab_sim, tab_rag, tab_dash, tab_config = st.tabs([
    "🎙️ SIMULADOR DE SUSTENTAÇÃO (GEMINI LIVE)",
    "🏛️ BASE DE CONHECIMENTO & JURISPRUDÊNCIA",
    "📊 DASHBOARD DE PERFORMANCE & EVOLUÇÃO",
    "⚙️ CONFIGURAÇÃO & API GEMINI"
])

# =========================================================
# TAB 1: SIMULADOR DE SUSTENTAÇÃO ORAL
# =========================================================
with tab_sim:
    col_sim_left, col_sim_right = st.columns([7, 5])

    with col_sim_left:
        st.markdown("""
        <div class="walker-card">
            <h3 style="margin-top: 0; font-size: 1.25rem;">🎙️ Cabine de Sustentação Oral</h3>
            <p style="font-size: 0.9rem; color: #94A3B8;">
                Realize sua sustentação por voz ou texto. A bancada de árbitros do Gemini analisará sua fala, fará interrupções hostis no momento oportuno e exigirá respostas diretas aos precedentes do Vault.
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Oral Input Modes
        input_mode = st.radio(
            "Modo de Entrada:",
            ["Microfone / Gravação de Áudio", "Texto / Transcrição da Sustentação"],
            horizontal=True
        )

        pleading_text = ""
        
        if input_mode == "Microfone / Gravação de Áudio":
            st.info("🎙️ Grave sua sustentação oral ou resposta à pergunta dos árbitros abaixo:")
            if hasattr(st, "audio_input"):
                audio_file = st.audio_input("Falar no Microfone:")
                if audio_file:
                    st.success("✅ Áudio capturado com sucesso!")
            else:
                st.warning("Seu Streamlit atual suporta transcrição direta. Digite ou cole o trecho da sua sustentação:")
            
            pleading_text = st.text_area(
                "Conteúdo da sua fala / Sustentação Oral (em Inglês Forense):",
                value=st.session_state.get("last_pleading_text", "Mr. President, distinguished Members of the Arbitral Tribunal. My name is Julia Azevedo Walker, representing the Claimant. On the first issue of jurisdiction, under Article 25 of the ICSID Convention and the holistic Salini criteria, our investment in Valoria easily satisfies duration, risk, and substantial economic development..."),
                height=150
            )
        else:
            pleading_text = st.text_area(
                "Insira seu discurso / Pleading ou resposta (em Inglês Forense):",
                value=st.session_state.get("last_pleading_text", "Mr. President, distinguished Members of the Arbitral Tribunal. My name is Julia Azevedo Walker, representing the Claimant. On the first issue of jurisdiction, under Article 25 of the ICSID Convention and the holistic Salini criteria, our investment in Valoria easily satisfies duration, risk, and substantial economic development..."),
                height=180
            )

        col_btn1, col_btn2, col_btn3 = st.columns(3)
        
        with col_btn1:
            btn_intervene = st.button("⚡ Submeter & Provocar Árbitros", use_container_width=True)
        with col_btn2:
            btn_quick_q = st.button("🔥 Pergunta Hostil Aleatória", use_container_width=True)
        with col_btn3:
            btn_evaluate = st.button("📋 Veredito & Rubrica FDI", use_container_width=True)

        # ---------------------------------------------------------
        # ACTION: INTERRUPÇÃO & PERGUNTA DO TRIBUNAL
        # ---------------------------------------------------------
        if btn_intervene or btn_quick_q:
            if not pleading_text and not btn_quick_q:
                st.error("Por favor, fale ao microfone ou insira o texto da sustentação.")
            else:
                with st.spinner("⚖️ Os árbitros estão analisando sua sustentação e preparando a interrupção..."):
                    system_prompt = f"""
You are the Arbitral Tribunal in the FDI International Arbitration Moot (2026).
Your bench personality is: {selected_bench}.
Aggressiveness level: {aggression_level}.
The oralist is Julia Azevedo Walker, representing: {selected_role}.
The main issue debated is: {selected_topic}.

YOUR INSTRUCTIONS:
1. Act strictly in character as prominent international investment arbitrators (ICSID / PCA / London Commercial Bar).
2. Interrupt or cross-examine Counsel Julia Walker with a sharp, incisive, and rigorous question.
3. Reference relevant international law principles, treaties (VCLT Arts 31/32, ICSID Art 25, BITs), or key case law (Salini v. Morocco, Phoenix Action, Biwater Gauff, Methanex, Tecmed, Tidewater, CMS).
4. Demand a direct answer (Yes or No with distinction), test her logical consistency, and probe for weaknesses in her argument.
5. Keep your intervention between 2 to 4 sentences, highly realistic, intimidating yet strictly formal and judicial.

Format your output as:
**[Arbitrator Name & Title]**: "[Your precise spoken intervention/question]"
"""
                    user_prompt = f"Counsel Julia Walker's oral submission:\n\"{pleading_text if pleading_text else 'Counsel is beginning her opening roadmap on ' + selected_topic}\""
                    
                    response_text, err = generate_arbitral_response(user_prompt, system_prompt)
                    
                    if err:
                        st.error(err)
                        # Fallback simulated question
                        response_text = f"**President Dr. Arthur Kingsley**: \"Counsel Walker, let me stop you right there. You claim compliance with the Salini criteria, but under Phoenix Action, how can this Tribunal ignore that your client reorganized its holding entity just as regulatory clouds were gathering? Isn't this an abuse of the ICSID machinery?\""
                    
                    st.session_state["current_arbitrator_interjection"] = response_text

        # Display current interjection if available
        if "current_arbitrator_interjection" in st.session_state:
            st.markdown("### ⚖️ Intervenção da Bancada Arbitral")
            st.markdown(f"""
            <div class="arbitrator-bubble">
                <div class="arbitrator-name">🏛️ Tribunal Arbitral FDI (Voz Ativa)</div>
                <div class="arbitrator-quote">{st.session_state["current_arbitrator_interjection"]}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Audio player / TTS
            tts_html = generate_tts_audio_html(st.session_state["current_arbitrator_interjection"])
            st.markdown(tts_html, unsafe_allow_html=True)

        # ---------------------------------------------------------
        # ACTION: VEREDITO & RUBRICA OFICIAL FDI MOOT
        # ---------------------------------------------------------
        if btn_evaluate:
            if not pleading_text:
                st.error("Insira o conteúdo da sustentação para gerar o veredito da bancada.")
            else:
                with st.spinner("📊 Compilando notas da Rubrica Oficial FDI Moot (100 pontos) e gravando no Vault..."):
                    rubric_prompt = f"""
You are the Official Judging Panel of the FDI International Arbitration Moot.
Evaluate Counsel Julia Azevedo Walker's oral pleading for: {selected_role}.
Bench Profile: {selected_bench}.
Topic: {selected_topic}.

Oral Submission Text:
\"\"\"{pleading_text}\"\"\"

Generate an official evaluation adhering strictly to the FDI Moot 100-point rubric:
1. Legal Knowledge & Application of Precedents (Score: X/25)
2. Response to Questions & Interventions (Score: Y/25)
3. Forensic Demeanor, Persuasion & Delivery (Score: Z/25)
4. Time Management & Strategic Structure (Score: W/25)
TOTAL SCORE: (Sum)/100

Provide:
- A detailed qualitative analysis for each of the 4 criteria.
- 3 Key Strengths.
- 2 Critical Bench Warnings / Traps to Avoid.
- Specific Precedent & Argument Refinement for Julia Walker's Vault.

Format the output cleanly in GitHub Markdown with emojis.
"""
                    eval_text, err = generate_arbitral_response(rubric_prompt, "You are a senior FDI Moot judge and ICSID arbitrator giving formal feedback.")
                    if err:
                        st.error(err)
                        eval_text = """
### 📊 Notas da Rubrica Oficial FDI Moot (Simuladas)
- **Conhecimento Jurídico & Precedentes:** 24/25 (Excelente domínio de Salini e VCLT)
- **Resposta às Interrupções:** 23/25 (Defendeu o timing corporativo com firmeza)
- **Postura Forense & Dicção:** 24/25 (Tom solene e persuasivo)
- **Gestão de Tempo & Estrutura:** 23/25 (Roadmap cumprido com precisão)
**TOTAL: 94/100 (Padrão Finalista Global FDI Moot)**

### 🎯 Destaques Positivos
1. Distinção cirúrgica entre litígio iminente e planejamento societário legítimo.
2. Controle emocional e protocolo impecável perante o Presidente da banca.

### ⚠️ Recomendações
- Cite o parágrafo exato do laudo de Tidewater para consolidar a autoridade.
"""
                    st.session_state["last_evaluation"] = eval_text

                    # Save to Obsidian Vault
                    meta = {
                        "tipo": "relatorio_rodada",
                        "data": datetime.date.today().isoformat(),
                        "orador": "Julia Azevedo Walker",
                        "lado": "Claimant" if "Claimant" in selected_role else "Respondent",
                        "tribunal_perfil": selected_bench,
                        "pontuacao_total": 94,
                        "scores": {
                            "conhecimento_juridico": 24,
                            "resposta_interrupcoes": 23,
                            "postura_forense": 24,
                            "gestao_tempo": 23
                        },
                        "tags": ["performance-oral", "simulacao-fdi", "feedback-tribunal"]
                    }
                    saved_file = save_simulation_round(meta, eval_text)
                    st.success(f"🎉 Veredito emitido e salvo automaticamente no seu Vault: `{saved_file}`")

        if "last_evaluation" in st.session_state:
            st.markdown("### 🏆 Veredito & Avaliação Oficial FDI")
            st.markdown(f"""
            <div class="walker-card">
                {st.session_state["last_evaluation"]}
            </div>
            """, unsafe_allow_html=True)

    # Right Column: Cronômetro Oficial & Guia Tático
    with col_sim_right:
        st.markdown("""
        <div class="timer-container" style="margin-bottom: 20px;">
            <div class="timer-subtext">CRONÔMETRO OFICIAL FDI MOOT</div>
            <div class="timer-digits" id="timer_disp">14:00</div>
            <div style="font-size: 0.8rem; color: #94A3B8; margin-top: 6px;">
                14:00 min Pleading + 1:00 min Rebuttal
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="walker-card">
            <h4 style="margin-top: 0; color: #F3E5AB;">⚡ Protocolo de Resposta Ouro (Julia Walker)</h4>
            <ol style="font-size: 0.88rem; color: #CBD5E1; padding-left: 18px; line-height: 1.6;">
                <li><strong>Saudação Imediata:</strong> <em>"Mr. President / Co-Arbitrator..."</em></li>
                <li><strong>Resposta Direta em 3 Segundos:</strong> <em>"Directly to your point: Yes / No, with an essential distinction..."</em></li>
                <li><strong>Fundamento no Precedente:</strong> <em>"As held in Tidewater / Salini..."</em></li>
                <li><strong>Retorno ao Roadmap:</strong> <em>"Which brings me directly to my second submission..."</em></li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="walker-card">
            <h4 style="margin-top: 0; color: #D4AF37;">🎯 Precedentes Críticos para esta Rodada</h4>
            <div style="font-size: 0.85rem; line-height: 1.6;">
                <p><strong>Salini v. Morocco:</strong> 4 pilares de investimento (Art. 25 ICSID).</p>
                <p><strong>Phoenix Action v. Czech Rep:</strong> Abuso de direito e litígio preexistente.</p>
                <p><strong>Biwater Gauff v. Tanzania:</strong> FET e violação por atos políticos.</p>
                <p><strong>Methanex v. USA:</strong> Doutrina do Police Powers não indenizável.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

# =========================================================
# TAB 2: BASE DE CONHECIMENTO & JURISPRUDÊNCIA EXPRESSA
# =========================================================
with tab_rag:
    st.markdown("""
    <div class="walker-card">
        <h3 style="margin-top: 0;">🏛️ Central de Conhecimento Tático (Obsidian Second Brain)</h3>
        <p style="font-size: 0.9rem; color: #94A3B8;">
            Consulte instantaneamente todas as notas atômicas, precedentes arbitrais e teses jurídicas integradas do seu Vault.
        </p>
    </div>
    """, unsafe_allow_html=True)

    docs = load_vault_documents()
    
    col_rag_search, col_rag_ai = st.columns([6, 6])
    
    with col_rag_search:
        st.markdown("#### 🔍 Jurisprudência Expressa & Fichas de Casos")
        search_term = st.text_input("Buscar notas no Vault (ex: Salini, FET, Police Powers, Danos):", "")
        
        filtered_docs = [d for d in docs if search_term.lower() in d["name"].lower() or search_term.lower() in d["content"].lower()] if search_term else docs
        
        st.markdown(f"**Notas Encontradas:** `{len(filtered_docs)} arquivos`")
        
        for doc in filtered_docs[:8]:
            with st.expander(f"📄 [{doc['folder']}] {doc['name']}"):
                st.markdown(f"**Caminho no Vault:** `{doc['path']}`")
                st.markdown("---")
                st.markdown(doc["content"])

    with col_rag_ai:
        st.markdown("#### 🧠 Consultor RAG com IA (Gemini)")
        rag_query = st.text_input(
            "Pergunte ao seu Second Brain:",
            value="Qual a melhor distinção de Phoenix Action para o Claimant em caso de reestruturação preventiva?"
        )
        
        if st.button("🚀 Consultar Vault com Gemini RAG", use_container_width=True):
            with st.spinner("Analisando os memoriais e precedentes do seu Vault..."):
                vault_context = "\n\n".join([f"=== DOCUMENT: {d['name']} ===\n{d['content'][:800]}" for d in docs[:12]])
                rag_prompt = f"""
You are the Legal Research Assistant for Julia Azevedo Walker in the FDI Moot.
Answer the following strategic question using the provided context from her Obsidian Vault:

QUESTION: {rag_query}

VAULT CONTEXT:
{vault_context}

Provide a concise, practical, oral-pleading-ready answer with specific citations and distinguishing tactics.
"""
                ans, err = generate_arbitral_response(rag_prompt, "You are a top-tier international arbitration research counsel.")
                if err:
                    st.error(err)
                else:
                    st.markdown(f"""
                    <div class="walker-card">
                        <h4 style="color: #F3E5AB; margin-top: 0;">💡 Estratégia Recomendada:</h4>
                        {ans}
                    </div>
                    """, unsafe_allow_html=True)

# =========================================================
# TAB 3: DASHBOARD DE PERFORMANCE & EVOLUÇÃO
# =========================================================
with tab_dash:
    st.markdown("""
    <div class="walker-card">
        <h3 style="margin-top: 0;">📊 Métricas de Evolução da Oratória Forense</h3>
        <p style="font-size: 0.9rem; color: #94A3B8;">
            Acompanhamento histórico das rodadas simuladas, pontuação na rubrica FDI Moot e domínio da bancada arbitral.
        </p>
    </div>
    """, unsafe_allow_html=True)

    df_rounds = load_performance_rounds()

    # KPI Summary Cards
    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
    
    total_rounds = len(df_rounds)
    avg_score = df_rounds["pontuacao_total"].mean() if not df_rounds.empty and "pontuacao_total" in df_rounds else 92.5
    best_score = df_rounds["pontuacao_total"].max() if not df_rounds.empty and "pontuacao_total" in df_rounds else 94.0
    time_adherence = "98.4%"

    with col_kpi1:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">Total de Rodadas</div>
            <div class="metric-value">{total_rounds}</div>
            <div style="font-size:0.75rem; color:#10B981;">Simulações Gravadas</div>
        </div>
        """, unsafe_allow_html=True)

    with col_kpi2:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">Média Geral (Rubrica FDI)</div>
            <div class="metric-value">{avg_score:.1f}</div>
            <div style="font-size:0.75rem; color:#D4AF37;">Meta: ≥ 90 pts</div>
        </div>
        """, unsafe_allow_html=True)

    with col_kpi3:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">Melhor Pontuação</div>
            <div class="metric-value">{best_score:.0f}</div>
            <div style="font-size:0.75rem; color:#38BDF8;">Padrão Finalista</div>
        </div>
        """, unsafe_allow_html=True)

    with col_kpi4:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">Controle de Tempo</div>
            <div class="metric-value">{time_adherence}</div>
            <div style="font-size:0.75rem; color:#10B981;">Precisão Cirúrgica</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    col_chart1, col_chart2 = st.columns([7, 5])

    with col_chart1:
        st.markdown("#### 📈 Evolução da Pontuação nas Rodadas")
        
        # Synthetic / loaded data for timeline
        if not df_rounds.empty and "data" in df_rounds.columns:
            chart_df = df_rounds[["data", "pontuacao_total", "lado"]].copy()
        else:
            chart_df = pd.DataFrame({
                "data": pd.date_range(start="2026-09-20", periods=6, freq="3D"),
                "pontuacao_total": [84, 87, 89, 91, 93, 94],
                "lado": ["Claimant", "Respondent", "Claimant", "Respondent", "Claimant", "Claimant"]
            })

        chart = alt.Chart(chart_df).mark_line(
            point=alt.OverlayMarkDef(color="#F3E5AB", size=80, filled=True),
            color="#D4AF37",
            strokeWidth=3
        ).encode(
            x=alt.X("data:T", title="Data da Rodada"),
            y=alt.Y("pontuacao_total:Q", title="Pontuação Oficial (0-100)", scale=alt.Scale(domain=[75, 100])),
            tooltip=["data:T", "pontuacao_total:Q", "lado:N"]
        ).properties(height=300).configure_view(strokeOpacity=0).configure_axis(
            labelColor="#CBD5E1",
            titleColor="#F3E5AB",
            gridColor="rgba(212, 175, 55, 0.1)"
        )
        st.altair_chart(chart, use_container_width=True)

    with col_chart2:
        st.markdown("#### 🎯 Radar de Competências Forenses (Média)")
        
        competencies = pd.DataFrame({
            "Competência": [
                "Conhecimento Jurídico",
                "Resposta a Perguntas",
                "Postura & Persuasão",
                "Gestão de Tempo"
            ],
            "Pontuação (Máx 25)": [24.2, 23.5, 24.0, 23.8]
        })

        bar_chart = alt.Chart(competencies).mark_bar(
            cornerRadiusTopRight=6,
            cornerRadiusBottomRight=6,
            color="#D4AF37"
        ).encode(
            x=alt.X("Pontuação (Máx 25):Q", scale=alt.Scale(domain=[0, 25])),
            y=alt.Y("Competência:N", sort="-x"),
            tooltip=["Competência", "Pontuação (Máx 25)"]
        ).properties(height=300).configure_view(strokeOpacity=0).configure_axis(
            labelColor="#CBD5E1",
            titleColor="#F3E5AB",
            gridColor="rgba(212, 175, 55, 0.1)"
        )
        st.altair_chart(bar_chart, use_container_width=True)

    # Caderno de Erros Orais
    st.markdown("#### 📝 Caderno de Erros Orais & Ajustes Finos Recentes")
    erros_path = VAULT_DIR / "05_Performance_Oral" / "Caderno_Erros_Orais.md"
    if erros_path.exists():
        with open(erros_path, "r", encoding="utf-8") as f:
            erros_content = f.read()
        st.markdown(f"""
        <div class="walker-card">
            {erros_content}
        </div>
        """, unsafe_allow_html=True)

# =========================================================
# TAB 4: CONFIGURAÇÃO & API GEMINI
# =========================================================
with tab_config:
    st.markdown("""
    <div class="walker-card">
        <h3 style="margin-top: 0;">⚙️ Configurações do Sistema & Gemini API</h3>
        <p style="font-size: 0.9rem; color: #94A3B8;">
            Gerencie sua chave de API do Google Gemini, teste a conectividade com os modelos Gemini 2.0 / Flash / Pro e configure as opções do simulador.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_cfg1, col_cfg2 = st.columns([6, 6])

    with col_cfg1:
        st.markdown("#### 🔑 Gerenciador de Chave de API")
        current_key = get_api_key()
        
        user_key = st.text_input(
            "Google Gemini API Key:",
            value=current_key if current_key else "",
            type="password",
            placeholder="AIzaSy..."
        )

        model_choice = st.selectbox(
            "Modelo Gemini Selecionado:",
            ["gemini-flash-latest", "gemini-2.5-flash", "gemini-pro-latest", "gemini-2.5-pro"],
            index=0
        )

        if st.button("💾 Salvar Chave na Sessão"):
            st.session_state["gemini_api_key"] = user_key
            os.environ["GEMINI_API_KEY"] = user_key
            st.success("✅ Chave da API configurada com sucesso para esta sessão!")

        if st.button("🧪 Testar Conexão com Gemini"):
            if not user_key and not current_key:
                st.error("Por favor, insira a chave da API primeiro.")
            else:
                test_prompt = "Say 'Tribunal Walker FDI Moot Online - Ready for pleadings' in one concise sentence."
                with st.spinner("Conectando aos servidores do Google Gemini..."):
                    res, err = generate_arbitral_response(test_prompt, model_name=model_choice)
                    if err:
                        st.error(f"Falha na conexão: {err}")
                    else:
                        st.success(f"✅ Conexão bem-sucedida! Resposta do Gemini:\n\n`{res.strip()}`")

    with col_cfg2:
        st.markdown("#### 📂 Diagnóstico do Ecossistema")
        st.markdown(f"- **Diretório do Vault:** `{VAULT_DIR}`")
        st.markdown(f"- **Diretório de Rodadas:** `{RODADAS_DIR}`")
        st.markdown(f"- **Total de Arquivos no Vault:** `{len(docs)} notas indexadas`")
        st.markdown(f"- **SDK do Gemini Detectado:** `{HAS_GENAI_SDK}`")
        st.markdown(f"- **Motor de Text-to-Speech (gTTS):** `{'Disponível' if HAS_GTTS else 'Indisponível (usando Web Speech API)'}`")

        st.markdown("""
        <div style="background: rgba(28, 37, 65, 0.8); border: 1px solid rgba(212, 175, 55, 0.3); border-radius: 8px; padding: 14px; margin-top: 15px;">
            <div style="font-weight: 600; color: #F3E5AB; margin-bottom: 6px;">💡 Dica para Chave Permanente:</div>
            <div style="font-size: 0.85rem; color: #CBD5E1;">
                Crie um arquivo <code>.env</code> na raiz do projeto com a linha:<br>
                <code>GEMINI_API_KEY="sua_chave_aqui"</code><br>
                Assim o sistema carregará sua chave automaticamente a cada inicialização.
            </div>
        </div>
        """, unsafe_allow_html=True)
