import streamlit as st

# 1. Configuração da Página (Design e Ícone)
st.set_page_config(
    page_title="Inscrição — Gonaldo's Bday Fest",
    page_icon="🎟️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

import time
from utils.db import adicionar_convidado
from utils.email_sender import enviar_email_convite

# 2. Estilização CSS Minimalista "Estilo Gemini"
st.markdown("""
    <style>
    /* Fundo suave e moderno */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Fontes e Títulos */
    .titulo-principal {
        color: #1f1f1f !important;
        text-align: center;
        font-family: 'Google Sans', sans-serif;
        font-weight: 500;
        letter-spacing: -0.5px;
        font-size: 36px;
        margin-bottom: 5px;
    }
    .subtitulo {
        text-align: center;
        color: #5f6368 !important;
        font-family: 'Roboto', sans-serif;
        font-size: 14px;
        font-weight: 500;
        letter-spacing: 1.5px;
        margin-bottom: 30px;
        text-transform: uppercase;
    }
    
    /* Card central estilo Gemini */
    .gemini-card {
        background-color: #ffffff;
        padding: 30px;
        border-radius: 24px;
        border: 1px solid #e0e2e6;
        box-shadow: 0 1px 2px rgba(60,64,67,0.3), 0 1px 3px rgba(60,64,67,0.15);
        margin-bottom: 25px;
    }

    /* Inputs de Texto Limpos */
    .stTextInput>div>div>input {
        background-color: #ffffff !important;
        color: #1f1f1f !important;
        border: 1px solid #747775 !important;
        border-radius: 12px !important;
        padding: 12px 16px !important;
    }
    .stTextInput>div>div>input:focus {
        border-color: #0b57d0 !important;
        box-shadow: 0 0 0 2px rgba(11, 87, 208, 0.2) !important;
    }
    
    /* Botão de Submissão Azul Google */
    .stButton>button {
        background-color: #0b57d0 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 100px !important;
        padding: 14px 28px !important;
        font-weight: 500 !important;
        width: 100%;
        font-size: 16px !important;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #0842a0 !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.2);
    }

    /* Esconder bordas padrão do Streamlit */
    div[data-testid="stForm"] {
        border: none !important;
        padding: 0 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- CABEÇALHO ---
st.markdown('<h1 class="titulo-principal">One Last Summer Dance</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitulo">Gonaldo Manuel Bday Edition — 11 Junho</p>', unsafe_allow_html=True)

# 3. Card de Informação Estilo Gemini
st.markdown("""
<div class="gemini-card">
    <p style="margin: 0; font-size: 16px; line-height: 1.6; text-align: center; color: #3c4043 !important;">
        Parabéns, Programador! 🎂<br>
        Introduz o teu <b>Nome</b> e <b>Email</b> para gerares o teu convite inteligente.<br>
        O QR Code de acesso será enviado instantaneamente para a tua caixa de entrada.
    </p>
</div>
""", unsafe_allow_html=True)

# --- FORMULÁRIO DE INSCRIÇÃO ---
with st.form(key="formulario_convite", clear_on_submit=True):
    nome = st.text_input("Nome Completo", placeholder="Como queres no convite?")
    email = st.text_input("Email", placeholder="onde vais receber o QR Code?")
    
    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    
    # Botão com a sintaxe correta
    submetido = st.form_submit_button("Gerar meu Convite Digital")

# --- LÓGICA DE PROCESSAMENTO ---
if submetido:
    if not nome.strip() or not email.strip():
        st.error("⚠️ Ups! Precisamos do teu nome e email para o convite.")
    elif "@" not in email or "." not in email:
        st.error("⚠️ Verifica o formato do email introduzido.")
    else:
        with st.spinner("A processar o teu acesso via Supabase..."):
            # 1. Tenta gravar no Supabase
            convidado_id = adicionar_convidado(nome, email)
            
            # 2. Verifica se houve erro de ligação à base de dados
            if convidado_id == "ERRO_CONEXAO":
                st.error("❌ Erro Crítico: Não foi possível autenticar no Supabase. Verifica as credenciais no terminal.")
            
            # 3. Verifica se o registo foi bem sucedido (UUID gerado)
            elif convidado_id:
                # 4. Tenta enviar o email
                sucesso_email = enviar_email_convite(nome, email, convidado_id)
                
                if sucesso_email:
                    st.success(f"🔥 Fantástico, {nome}! O teu convite está a caminho.")
                    st.balloons()
                    st.markdown(f"""
                        <div style="background-color: #e8f0fe; padding: 20px; border-radius: 16px; border: 1px solid #aecbfa; text-align: center;">
                            <p style="margin: 0; color: #1a73e8 !important; font-weight: 500; font-size: 15px;">
                                📩 Verifica o email: <b>{email}</b><br>
                                <span style="font-size: 13px; font-weight: 400;">(Não te esqueças de ver na pasta de Promoções ou Spam)</span>
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning("⚠️ O teu lugar está reservado no sistema, mas houve uma falha ao enviar o email. Avisa o Gonaldo!")
            
            # 5. Se o convidado_id for None, significa que o email já existe (Unique Constraint)
            else:
                st.error("❌ Este email já se encontra na lista de convidados!")

# Rodapé minimalista
st.markdown("<p style='text-align: center; color: #9aa0a6; font-size: 12px; margin-top: 50px;'>Powered by Python & Supabase • Gonaldo Manuel © 2026</p>", unsafe_allow_html=True)