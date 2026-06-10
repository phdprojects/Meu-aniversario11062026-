import streamlit as st
from streamlit_qrcode_scanner import qrcode_scanner
from utils.db import supabase

st.set_page_config(page_title="Portaria Digital 3.0", page_icon="🎟️", layout="centered")

st.markdown("""
    <style>
    .title { text-align: center; color: #45f3ff; font-family: 'Helvetica Neue', sans-serif; }
    .subtitle { text-align: center; color: #66fcf1; margin-bottom: 30px; }
    </style>
    <h1 class="title">🛡️ Portaria Digital Elegante</h1>
    <p class="subtitle">Scanner de QR Code em Tempo Real</p>
""", unsafe_allow_html=True)

if "scanner_key" not in st.session_state:
    st.session_state.scanner_key = 0

# Ativa o scanner de vídeo em tempo real
codigo_limpo = qrcode_scanner(key=f"qr_scanner_{st.session_state.scanner_key}")

if codigo_limpo:
    st.info(f"🔍 Código detetado: {codigo_limpo}")
    
    try:
        # Faz a pesquisa direta na tabela convidados
        resposta = supabase.table("convidados").select("*").eq("id", codigo_limpo).execute()
        
        if resposta.data:
            convidado = resposta.data[0]
            nome = convidado.get("nome")
            # AJUSTE: Mudado de 'chegou' para 'compareceu' conforme a tua base de dados
            ja_entrou = convidado.get("compareceu", False)
            
            if ja_entrou:
                st.error(f"❌ ATENÇÃO: {nome} já entrou no evento!")
            else:
                # AJUSTE: Faz o update na coluna correta 'compareceu'
                supabase.table("convidados").update({"compareceu": True}).eq("id", codigo_limpo).execute()
                st.success(f"✅ BEM-VINDO, {nome}! Entrada confirmada com sucesso! 🎉")
                st.balloons()
                
                if st.button("Fazer Scan ao Próximo"):
                    st.session_state.scanner_key += 1
                    st.rerun()
        else:
            st.error("❌ Código inválido ou não encontrado no Supabase.")
            if st.button("Tentar Novamente"):
                st.rerun()
                
    except Exception as e:
        st.error(f"Erro ao ligar ao Supabase: {e}")

# Janela de contingência manual
with st.expander("⌨️ Validação Manual Alternativa"):
    id_manual = st.text_input("Insere o ID ou código único:")
    if st.button("Validar Manualmente"):
        if id_manual:
            resposta = supabase.table("convidados").select("*").eq("id", id_manual).execute()
            if resposta.data:
                # AJUSTE: Faz o update manual na coluna 'compareceu'
                supabase.table("convidados").update({"compareceu": True}).eq("id", id_manual).execute()
                st.success(f"✅ Confirmado Manualmente: {resposta.data[0]['nome']}!")
                st.balloons()