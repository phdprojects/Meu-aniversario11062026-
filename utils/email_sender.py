import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import qrcode
from io import BytesIO
from dotenv import load_dotenv

# Carrega as credenciais do ficheiro .env
load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

def gerar_qr_code_bytes(convidado_id: str) -> bytes:
    """
    Gera o QR Code contendo apenas o ID único (UUID) do convidado.
    Retorna os bytes da imagem em formato PNG.
    """
    # Configuramos o QR Code com cores escuras para combinar com o tema
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    # O conteúdo do QR Code será o ID do Supabase que usaremos no telemóvel para fazer o check-in
    qr.add_data(convidado_id)
    qr.make(fit=True)

    # Criamos a imagem (QR Code preto com fundo branco para máxima leitura da câmara)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Guarda a imagem em memória (BytesIO) para não encher o disco de ficheiros temporários
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()

def enviar_email_convite(nome_convidado: str, email_destino: str, convidado_id: str) -> bool:
    """
    Monta o email em formato HTML Premium (Festival Vibes) com o QR Code embutido
    e envia-o para o convidado através de SMTP.
    """
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        print("Erro: As credenciais SMTP não estão configuradas no ficheiro .env")
        return False

    try:
        # 1. Configuração da mensagem Multipart
        msg = MIMEMultipart("related")
        msg["From"] = f"Aniversário Gonaldo Manuel 🎂 <{SMTP_EMAIL}>"
        msg["To"] = email_destino
        msg["Subject"] = "🎟️ O Teu Convite Digital Exclusivo — Gonaldo's Bday"

        # 2. Template HTML Premium (Inspirado no "One Last Summer Dance")
        # Usamos tons escuros, dourados elegantes e cantos arredondados modernos
        html_conteudo = f"""
        <html>
        <body style="margin: 0; padding: 0; background-color: #0a0a0a; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;">
            <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 500px; background-color: #121212; border: 1px solid #1c1c1c; margin-top: 30px; margin-bottom: 30px; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
                
                <tr>
                    <td align="center" style="background: linear-gradient(135deg, #bdc3c7 0%, #2c3e50 100%); padding: 40px 20px; text-align: center; border-bottom: 2px solid #E5A93C;">
                        <span style="font-size: 11px; letter-spacing: 4px; color: #ffffff; text-transform: uppercase; font-weight: 500; opacity: 0.8;">WHITE SAND MOUNTAINS & MORE</span>
                        <h1 style="color: #E5A93C; font-size: 24px; font-weight: 300; letter-spacing: 2px; margin: 15px 0 5px 0; text-transform: uppercase;">ONE LAST SUMMER DANCE</h1>
                        <p style="color: #ffffff; font-size: 13px; margin: 0; opacity: 0.9; letter-spacing: 1px;">GONALDO MANUEL BDAY EDITION</p>
                    </td>
                </tr>

                <tr>
                    <td style="padding: 30px 25px; text-align: center;">
                        <p style="color: #ffffff; font-size: 16px; margin-top: 0; font-weight: 400; text-align: left;">
                            Olá, <strong style="color: #E5A93C;">{nome_convidado}</strong>!
                        </p>
                        <p style="color: #b3b3b3; font-size: 14px; line-height: 1.6; text-align: left; margin-bottom: 25px;">
                            O teu <strong>acesso digital exclusivo</strong> foi gerado com sucesso pelo sistema. Para entrares no evento de forma rápida e ecológica, basta apresentares o QR Code abaixo à entrada através do teu telemóvel. <strong>Não precisas de imprimir nada.</strong>
                        </p>

                        <table align="center" border="0" cellpadding="0" cellspacing="0" style="background-color: #1a1a1a; padding: 20px; border-radius: 12px; border: 1px solid #262626; margin: 20px auto;">
                            <tr>
                                <td align="center">
                                    <img src="cid:qrcode_img" width="180" height="180" style="display: block; border-radius: 8px;" alt="O Teu QR Code de Acesso" />
                                </td>
                            </tr>
                            <tr>
                                <td align="center" style="padding-top: 12px;">
                                    <span style="color: #888888; font-size: 11px; letter-spacing: 1px; text-transform: uppercase;">Código de Segurança Único</span><br/>
                                    <code style="color: #e67e22; font-size: 12px; font-weight: bold; font-family: monospace;">{convidado_id[:8].upper()}-{convidado_id[-8:].upper()}</code>
                                </td>
                            </tr>
                        </table>

                        <p style="margin-top: 25px; margin-bottom: 15px;">
                            <a href="cid:qrcode_img" download="meu_convite_gonaldo.png" style="background-color: #E5A93C; color: #000000; padding: 12px 28px; font-size: 14px; font-weight: bold; text-decoration: none; border-radius: 30px; display: inline-block; letter-spacing: 0.5px; box-shadow: 0 4px 15px rgba(229,169,60,0.3);">
                                📥 Guardar QR Code no Telemóvel
                            </a>
                        </p>
                    </td>
                </tr>

                <tr>
                    <td style="padding: 20px; background-color: #0d0d0d; text-align: center; border-top: 1px solid #1a1a1a;">
                        <p style="font-size: 11px; color: #666666; margin: 0; line-height: 1.5;">
                            Convite digital válido e verificado de forma automática pela portaria.<br/>
                            ✨ Vamos celebrar juntos com zero papel! ✨
                        </p>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
        
        # Anexa o corpo HTML estruturado
        msg_html = MIMEText(html_conteudo, "html")
        msg.attach(msg_html)

        # 3. Gerar o QR Code em memória e embutir como anexo "Inline" (Content-ID)
        qr_bytes = gerar_qr_code_bytes(convidado_id)
        msg_image = MIMEImage(qr_bytes)
        # Este ID tem de bater exatamente com o <img src="cid:qrcode_img"> definido no HTML acima
        msg_image.add_header("Content-ID", "<qrcode_img>")
        msg_image.add_header("Content-Disposition", "inline", filename="qrcode.png")
        msg.attach(msg_image)

        # 4. Processo de Autenticação e Envio via Servidor SMTP
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls() # Inicia a encriptação de transporte TLS segura
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.sendmail(SMTP_EMAIL, email_destino, msg.as_string())
            
        print(f"📧 Sucesso! Convite enviado com QR Code para: {email_destino}")
        return True

    except Exception as e:
        print(f"❌ Erro crítico ao enviar o email para {email_destino}: {e}")
        return False