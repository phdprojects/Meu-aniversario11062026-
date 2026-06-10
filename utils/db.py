import os
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

# Força o carregamento das variáveis do ficheiro .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# LOG DE DEPURAÇÃO: Isto vai aparecer no teu terminal do iMac para confirmarmos a chave
if SUPABASE_KEY:
    print(f"🚀 [SISTEMA]: Supabase inicializado com a chave: {SUPABASE_KEY[:15]}... (Token JWT detetado)")
else:
    print("❌ [ERRO]: Chave SUPABASE_KEY não encontrada no ficheiro .env!")

# Inicializa o cliente do Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def adicionar_convidado(nome: str, email: str):
    """
    Insere um novo convidado na base de dados do Supabase.
    Retorna o ID se sucesso, "ERRO_CONEXAO" se houver falha de API, ou None se for duplicado.
    """
    try:
        dados = {"nome": nome, "email": email.strip().lower()}
        resposta = supabase.table("convidados").insert(dados).execute()
        
        if resposta.data:
            return resposta.data[0]["id"]
        return None
        
    except Exception as e:
        erro_str = str(e)
        # Se o erro for de autenticação (Chave inválida)
        if "401" in erro_str or "Invalid API key" in erro_str:
            print(f"\n🚨 [ERRO DE AUTENTICAÇÃO]: A chave do Supabase foi rejeitada. Verifica o .env.\nDetalhes: {e}")
            return "ERRO_CONEXAO"
        
        # Se for erro de duplicado (409 Conflict), o e registra no log mas retorna None
        print(f"ℹ️ [INFO]: Tentativa de registo falhou ou email duplicado: {e}")
        return None

def realizar_checkin(convidado_id: str):
    """
    Faz a validação do QR Code na portaria e atualiza o estado para compareceu = True.
    """
    try:
        # 1. Procura o convidado pelo ID que veio no QR Code
        resposta = supabase.table("convidados").select("nome", "compareceu").eq("id", convidado_id).execute()
        
        if not resposta.data:
            return "nao_encontrado", None
        
        convidado = resposta.data[0]
        nome = convidado["nome"]
        
        # 2. Verifica se já entrou
        if convidado["compareceu"]:
            return "ja_entrou", nome
        
        # 3. Se tudo ok, marca como presente e guarda a hora
        agora = datetime.utcnow().isoformat()
        supabase.table("convidados").update({
            "compareceu": True,
            "confirmado_em": agora
        }).eq("id", convidado_id).execute()
        
        return "sucesso", nome
        
    except Exception as e:
        print(f"❌ [ERRO NO CHECKIN]: {e}")
        return "erro", None