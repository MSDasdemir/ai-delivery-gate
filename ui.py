import streamlit as st

def setup(title, eyebrow, subtitle, workflow):
    st.set_page_config(page_title=title+' | Senan Dasdemir',page_icon='◈',layout='wide')
    st.markdown("""<style>
    .stApp { background:#f5f7fb; color:#16263f; }
    .block-container { max-width:1240px; padding-top:2.4rem; padding-bottom:3rem; }
    h1 { letter-spacing:-.045em; font-weight:750 !important; }
    [data-testid="stMetric"] {background:white;border:1px solid #dce4ef;border-radius:14px;padding:20px;}
    [data-testid="stMetricLabel"] {color:#596b83;}
    [data-testid="stSidebar"] {background:#eaf0f7;}
    [data-testid="stExpander"] {background:white;border-radius:12px;}
    .eyebrow {color:#246f91;font-weight:700;letter-spacing:.15em;font-size:.72rem;margin-bottom:.6rem;}
    .subtitle {font-size:1.1rem;color:#526780;margin-top:-.4rem;}
    .workflow {border-left:3px solid #0d9488;padding:9px 15px;margin:16px 0 22px;color:#38616b;background:#edf6f5;}
    </style>""",unsafe_allow_html=True)
    st.markdown(f'<div class="eyebrow">SENAN DASDEMIR / {eyebrow}</div>',unsafe_allow_html=True)
    st.title(title)
    st.markdown(f'<p class="subtitle">{subtitle}</p><div class="workflow">{workflow}</div>',unsafe_allow_html=True)

def ai_controls():
    st.divider()
    st.subheader('Local AI')
    enabled=st.toggle('Enable Ollama',value=False)
    model=st.text_input('Installed model name',value='qwen2.5:1.5b',disabled=not enabled)
    st.caption('Optional local generation at 127.0.0.1:11434. No paid API. Model download and sufficient RAM are required.')
    return enabled,model
