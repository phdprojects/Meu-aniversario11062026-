import streamlit as str
import streamlit.components.v1 as components
from utils.db import supabase  # Garante que aponta para o teu utilitário de BD

str.set_page_config(page_title="Portaria Digital 3.0", page_icon="🎟️", layout="centered")

str.markdown("""
    <style>
    .title { text-align: center; color: #45f3ff; font-family: 'Helvetica Neue', sans-serif; }
    .subtitle { text-align: center; color: #66fcf1; margin-bottom: 30px; }
    </style>
    <h1 class="title">🛡️ Portaria Digital Elegante</h1>
    <p class="subtitle">Scanner de QR Code em Tempo Real</p>
""", unsafe_allow_html=True)

# 1. Injeção de Scanner Moderno em JavaScript (Instascan)
# Este bloco abre a câmara em modo vídeo e procura QR Codes frames por segundo
qrcode_scanner_html = """
<div style="text-align: center;">
    <video id="preview" style="width: 100%; max-width: 400px; border: 2px solid #45f3ff; border-radius: 10px; background: #000;"></video>
</div>
<script src="https://rawgit.com/schmich/instascan-builds/master/instascan.min.js"></script>
<script>
  let scanner = new Instascan.Scanner({ video: document.getElementById('preview'), mirror: false });
  scanner.addListener('scan', function (content) {
    // Envia o código lido de volta para o Streamlit instantaneamente
    window.parent.postMessage({type: 'streamlit:setComponentValue', value: content}, '*');
  });
  Instascan.Camera.getCameras().then(function (cameras) {
    if (cameras.length > 0) {
      // Usa a câmara traseira do telemóvel se disponível, senão usa a primeira
      let selectedCamera = cameras.find(c => c.name.toLowerCase().includes('back')) || cameras[0];
      scanner.start(selectedCamera);
    } else {
      console.error('Nenhuma câmara encontrada.');
    }
  }).catch(function (e) {
    console.error(e);
  });
</script>
"""

# Renderiza o scanner na página
codigo_detetado = components.html(qrcode_scanner_html, height=320, scrolling=False)

# 2. Processamento do Código detetado pelo JavaScript
if codigo_detetado:
    str.warning(f"🔍 Código detetado: {codigo_detetado}")
    
    # Faz a pesquisa no Supabase
    try:
        # Assume que o teu QR code contém o ID do convidado
        resposta = supabase.table("convidados").select("*").eq("id", codigo_detetado).execute()
        
        if resposta.data:
            convidado = resposta.data[0]
            nome = convidado.get("nome")
            ja_entrou = convidado.get("chegou", False)
            
            if ja_entrou:
                str.error(f"❌ ATENÇÃO: {nome} já entrou no evento!")
                str.audio("https://www.soundjay.com/buttons/sounds/button-10.mp3") # Som de erro
            else:
                # Atualiza o estado de presença no Supabase
                supabase.table("convidados").update({"chegou": True}).eq("id", codigo_detetado).execute()
                str.success(f"✅ BEM-VINDO, {nome}! Entrada confirmada com sucesso! 🎉")
                str.balloons()
                str.audio("https://www.soundjay.com/buttons/sounds/button-09.mp3") # Som de sucesso
        else:
            str.error("❌ Código inválido ou não encontrado no Supabase.")
            
    except Exception as e:
        str.error(f"Erro ao ligar ao Supabase: {e}")

# Botão de segurança para digitação manual se necessário
with str.expander("⌨️ Validação Manual Alternativa"):
    id_manual = str.text_input("Insere o ID ou código único:")
    if str.button("Validar Manualmente"):
        if id_manual:
            # Corre a mesma lógica de validação do Supabase
            resposta = supabase.table("convidados").select("*").eq("id", id_manual).execute()
            if resposta.data:
                str.success(f"✅ Confirmado Manualmente: {resposta.data[0]['nome']}")
                str.balloons()