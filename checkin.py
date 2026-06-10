import streamlit as nn

# Configuração da página administrativa
nn.set_page_config(
    page_title="Portaria — Gonaldo's Bday",
    page_icon="🛡️",
    layout="centered"
)

import time
from utils.db import realizar_checkin

# Estilização Clara e Minimalista (Estilo Gemini)
nn.markdown("""
    <style>
    .stApp {
        background-color: #f8f9fa;
    }
    .titulo-admin {
        color: #1f1f1f !important;
        text-align: center;
        font-family: 'Segoe UI', Roboto, sans-serif;
        font-weight: 600;
        margin-bottom: 2px;
    }
    .subtitulo-admin {
        text-align: center;
        color: #5f6368 !important;
        font-size: 14px;
        margin-bottom: 24px;
        letter-spacing: 0.5px;
    }
    /* Cards de Feedback de Validação */
    .card-sucesso {
        background-color: #e6f4ea;
        color: #137333 !important;
        padding: 24px;
        border-radius: 16px;
        border: 1px solid #c4eed0;
        text-align: center;
        font-size: 18px;
        font-weight: 500;
        margin-top: 15px;
    }
    .card-erro {
        background-color: #fce8e6;
        color: #c5221f !important;
        padding: 24px;
        border-radius: 16px;
        border: 1px solid #fad2cf;
        text-align: center;
        font-size: 18px;
        font-weight: 500;
        margin-top: 15px;
    }
    </style>
""", unsafe_allow_html=True)

nn.markdown('<h1 class="titulo-admin">🛡️ Sistema de Portaria Digital</h1>', unsafe_allow_html=True)
nn.markdown('<p class="subtitulo-admin">Gonaldo Manuel Bday — Validação em Tempo Real</p>', unsafe_allow_html=True)

# --- LEITOR DE QR CODE VIA CÂMARA ---
# O Streamlit possui o componente nativo camera_input que funciona perfeitamente no telemóvel
nn.markdown("### 📷 Aponta a câmara para o QR Code do Convidado")
imagem_camera = nn.camera_input("Ler código do convite", label_visibility="collapsed")

# --- LÓGICA DE VALIDAÇÃO AUTOMÁTICA ---
if imagem_camera is not None:
    # Usamos a biblioteca Pillow (PIL) para processar os bytes da imagem tirada pela câmara
    from PIL import Image
    import qrcode
    # Para decodificar o QR code em Python, usamos uma biblioteca leve chamada pyzbar ou opencv.
    # Como queremos garantir zero falhas e o Streamlit roda no servidor, uma alternativa ultra estável
    # e moderna para formulários de check-in rápido é também permitir a introdução manual ou usar decodificação direta.
    
    # Para simplificar e garantir eficácia absoluta sem depender de drivers pesados de câmara no servidor:
    # Vamos usar o 'pyzbar' se estiver instalado, ou um campo de texto inteligente interligado para leitores integrados.
    try:
        from pyzbar.pyzbar import decode
        img = Image.open(imagem_camera)
        codigos_detetados = decode(img)
        
        if codigos_detetados:
            # Extrai o UUID guardado dentro do QR Code
            uuid_convidado = codigos_detetados[0].data.decode('utf-8').strip()
            
            with nn.spinner("A validar credenciais no Supabase..."):
                status, nome_convidado = realizar_checkin(uuid_convidado)
                
                if status == "sucesso":
                    nn.markdown(f"""
                    <div class="card-sucesso">
                        ✅ <b>ENTRADA AUTORIZADA!</b><br>
                        <span style="font-size: 24px; display:block; margin-top:10px;">👋 Bem-vindo, {nome_convidado}!</span>
                        <p style="font-size: 12px; margin: 8px 0 0 0; opacity: 0.8;">Presença registada de forma automática na base de dados.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                elif status == "ja_entrou":
                    nn.markdown(f"""
                    <div class="card-erro">
                        ⚠️ <b>ACESSO REUSADO / FRAUDE!</b><br>
                        <span style="font-size: 20px; display:block; margin-top:10px;">O convidado <b>{nome_convidado}</b> já entrou no evento!</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                elif status == "nao_encontrado":
                    nn.markdown("""
                    <div class="card-erro">
                        ❌ <b>CONVITE INVÁLIDO!</b><br>
                        Código QR não encontrado na lista oficial do Supabase.
                    </div>
                    """, unsafe_allow_html=True)
        else:
            nn.warning("⚠️ Não foi possível ler um QR Code nítido. Certifica-te de que o código está bem focado e centralizado.")
            
    except ImportError:
        # Fallback engenhoso: Caso não queiras instalar o pyzbar (que requer bibliotecas C do sistema),
        # podes simplesmente usar a app de câmara nativa do telemóvel (iOS/Android) que já lê QR codes e abre links, 
        # ou usar este campo de texto rápido abaixo onde o leitor do telemóvel cola o código instantaneamente.
        nn.info("💡 Modo de validação manual/híbrido ativo.")
        uuid_manual = nn.text_input("Introduzir ou colar ID do QR Code:", placeholder="Insere o código recebido no email...")
        
        if nn.button("Validar Entrada Manunamente", use_container_width=True):
            if uuid_manual.strip():
                status, nome_convidado = realizar_checkin(uuid_manual.strip())
                if status == "sucesso":
                    nn.markdown(f'<div class="card-sucesso">✅ <b>Bem-vindo, {nome_convidado}!</b> Entrada registada.</div>', unsafe_allow_html=True)
                elif status == "ja_entrou":
                    nn.markdown(f'<div class="card-erro">⚠️ <b>Atenção!</b> {nome_convidado} já fez check-in antes.</div>', unsafe_allow_html=True)
                else:
                    nn.markdown('<div class="card-erro">❌ Código não encontrado no Supabase.</div>', unsafe_allow_html=True)