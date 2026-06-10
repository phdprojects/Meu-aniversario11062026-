import streamlit as st
from streamlit_qrcode_scanner import qrcode_scanner
from utils.db import supabase
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

st.set_page_config(page_title="Portaria Digital 3.0", page_icon="🎟️", layout="centered")

st.markdown("""
    <style>
    .title { text-align: center; color: #45f3ff; font-family: 'Helvetica Neue', sans-serif; }
    .subtitle { text-align: center; color: #66fcf1; margin-bottom: 30px; }
    </style>
    <h1 class="title">🛡️ Portaria Digital Elegante</h1>
    <p class="subtitle">Scanner de QR Code em Tempo Real</p>
""", unsafe_allow_html=True)

# Função rápida interna para enviar o e-mail de agradecimento (Brinde)
def enviar_email_agradecimento(nome, email_destino):
    try:
        smtp_email = os.getenv("SMTP_EMAIL")
        smtp_password = os.getenv("SMTP_PASSWORD")
        
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "🥂 Obrigado pela tua presença no Gonaldo's Bday Fest!"
        msg["From"] = f"Gonaldo Manuel <{smtp_email}>"
        msg["To"] = email_destino

        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #0b0c10; color: #ffffff; padding: 20px; text-align: center;">
                <div style="max-width: 450px; margin: 0 auto; background-color: #1f2833; padding: 30px; border-radius: 15px; border: 1px solid #45f3ff;">
                    <h2 style="color: #45f3ff;">Já estás lá dentro! 🎉</h2>
                    <p>Olá <b>{nome}</b>,</p>
                    <p>Obrigado por 設定es presença neste dia tão importante. A tua entrada foi validada com sucesso!</p>
                    <p style="color: #66fcf1; font-weight: bold;">Prepara-se para a pista de dança. Bebe um copo por nossa conta! 🥂</p>
                    <hr style="border: 0; border-top: 1px solid #45f3ff; margin: 20px 0;">
                    <p style="font-size: 12px; color: #8d99ae;">One Last Summer Dance • Lisboa</p>
                </div>
            </body>
        </html>
        """
        msg.attach(MIMEText(html, "html"))
        server = smtplib.SMTP(os.getenv("SMTP_SERVER", "smtp.gmail.com"), int(os.getenv("SMTP_PORT", 587)))
        server.starttls()
        server.login(smtp_email, smtp_password)
        server.sendmail(smtp_email, email_destino, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Erro ao enviar agradecimento para {email_destino}: {e}")
        return False

if "scanner_key" not in st.session_state:
    st.session_state.scanner_key = 0

codigo_limpo = qrcode_scanner(key=f"qr_scanner_{st.session_state.scanner_key}")

if codigo_limpo:
    st.info(f"🔍 Código detetado: {codigo_limpo}")
    
    try:
        resposta = supabase.table("convidados").select("*").eq("id", codigo_limpo).execute()
        
        if resposta.data:
            convidado = resposta.data[0]
            nome = convidado.get("nome")
            email = convidado.get("email")
            ja_entrou = convidado.get("compareceu", False)
            
            if ja_entrou:
                st.error(f"❌ ATENÇÃO: {nome} já entrou no evento!")
            else:
                # 1. Atualiza o status na tabela principal
                supabase.table("convidados").update({"compareceu": True}).eq("id", codigo_limpo).execute()
                
                # 2. NOVO: Regista no Relatório de Presenças (a hora é guardada automaticamente pelo Supabase)
                supabase.table("relatorio_presencas").insert({
                    "convidado_id": codigo_limpo,
                    "nome_convidado": nome
                }).execute()
                
                st.success(f"✅ BEM-VINDO, {nome}! Presença registada no relatório! 🎉")
                
                # 3. NOVO: Dispara o E-mail de Brinde/Agradecimento na hora
                with st.spinner("A enviar brinde digital por e-mail..."):
                    if enviar_email_agradecimento(nome, email):
                        st.toast(f"📩 E-mail de agradecimento enviado para {nome}!")
                
                st.balloons()
                
                if st.button("Fazer Scan ao Próximo"):
                    st.session_state.scanner_key += 1
                    st.rerun()
        else:
            st.error("❌ Código inválido ou não encontrado no Supabase.")
            if st.button("Tentar Novamente"):
                st.rerun()
                
    except Exception as e:
        st.error(f"Erro no fluxo de validação: {e}")

# Janela de contingência manual
with st.expander("⌨️ Validação Manual Alternativa"):
    id_manual = st.text_input("Insere o ID ou código único:")
    if st.button("Validar Manualmente"):
        if id_manual:
            resposta = supabase.table("convidados").select("*").eq("id", id_manual).execute()
            if resposta.data:
                conv = resposta.data[0]
                supabase.table("convidados").update({"compareceu": True}).eq("id", id_manual).execute()
                supabase.table("relatorio_presencas").insert({"convidado_id": id_manual, "nome_convidado": conv['nome']}).execute()
                
                st.success(f"✅ Confirmado Manualmente: {conv['nome']}!")
                enviar_email_agradecimento(conv['nome'], conv['email'])
                st.balloons()