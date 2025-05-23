from flask import Flask, request, jsonify
import json
import os
import hashlib
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

app = Flask(__name__)

# Configurações do Supabase
SUPABASE_URL = "https://fawgofnpdzyxvgupplwb.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZhd2dvZm5wZHp5eHZndXBwbHdiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDM3ODQ5ODIsImV4cCI6MjA1OTM2MDk4Mn0.yc4Aok9wlVlz5YfHKQsgNREPpyAZ47TW7JBt6bVYZvc"

# Inicializa cliente Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def is_valid_email(email):
    """
    Verifica se o formato do email é válido.
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def get_email_from_hash(email_hash):
    """
    Busca o email no Supabase usando o hash MD5.
    Retorna o registro completo se encontrado.
    """
    try:
        # Busca todos os registros e verifica o hash localmente
        # (Supabase não suporta hash MD5 diretamente na query)
        response = supabase.table('advs').select('*').execute()
        
        for record in response.data:
            if record.get('emils'):  # Verifica se o campo email existe
                record_hash = hashlib.md5(record['emils'].encode()).hexdigest()
                if record_hash == email_hash:
                    return record
        return None
    except Exception as e:
        print(f"Erro ao buscar email no Supabase: {e}")
        return None

def update_blacklist_status(record_id, email):
    """
    Atualiza o status de blacklist no Supabase.
    """
    try:
        data = {
            'blacklist': True,
            'data_bloqueio': datetime.now().isoformat(),
            'motivo': 'Descadastro via link'
        }
        
        response = supabase.table('advs').update(data).eq('id', record_id).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"Erro ao atualizar blacklist no Supabase: {e}")
        return False

def get_blacklisted_emails():
    """
    Retorna todos os emails que estão na blacklist.
    """
    try:
        response = supabase.table('advs').select('emils, data_bloqueio, motivo').eq('blacklist', True).execute()
        return response.data
    except Exception as e:
        print(f"Erro ao buscar blacklist no Supabase: {e}")
        return []

def get_blacklisted_hashes():
    """
    Retorna todos os hashes MD5 dos emails que estão na blacklist.
    """
    try:
        response = supabase.table('advs').select('emils').eq('blacklist', True).execute()
        hashes = []
        for record in response.data:
            if record.get('emils'):
                email_hash = hashlib.md5(record['emils'].encode()).hexdigest()
                hashes.append(email_hash)
        return hashes
    except Exception as e:
        print(f"Erro ao buscar hashes da blacklist: {e}")
        return []

@app.route('/')
def home():
    """
    Rota principal com informações básicas da API.
    """
    return """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>API de Descadastramento</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
            .container { text-align: center; }
            .info { background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚫 API de Descadastramento</h1>
            <div class="info">
                <h3>Endpoints Disponíveis:</h3>
                <p><strong>GET /unsubscribe?id=MD5_HASH</strong> - Descadastrar e-mail</p>
                <p><strong>GET /unsubscribe?email=EMAIL</strong> - Descadastrar por e-mail</p>
                <p><strong>GET /blacklist</strong> - Consultar lista de descadastrados</p>
                <p><strong>GET /blacklist/hashes</strong> - Consultar hashes da blacklist</p>
            </div>
            <p>Sistema funcionando corretamente! ✅</p>
            <p><small>Integrado com Supabase</small></p>
        </div>
    </body>
    </html>
    """

@app.route('/unsubscribe')
def unsubscribe():
    """
    Rota principal de descadastramento.
    Aceita tanto hash MD5 quanto email direto.
    """
    email_id = request.args.get('id')  # Hash MD5
    email_direct = request.args.get('email')  # Email direto
    
    # Verifica se pelo menos um parâmetro foi fornecido
    if not email_id and not email_direct:
        return """
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Erro - Parâmetro Necessário</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
                .error { background: #ffe6e6; border: 1px solid #ff9999; padding: 20px; border-radius: 8px; text-align: center; }
            </style>
        </head>
        <body>
            <div class="error">
                <h2>❌ Erro</h2>
                <p>ID do e-mail ou e-mail é obrigatório.</p>
                <p>Use: /unsubscribe?id=SEU_ID ou /unsubscribe?email=seu@email.com</p>
            </div>
        </body>
        </html>
        """, 400
    
    record = None
    
    # Se foi fornecido um hash MD5
    if email_id:
        # Verifica se o ID é um hash MD5 válido
        if len(email_id) != 32:
            return """
            <!DOCTYPE html>
            <html lang="pt-BR">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Erro - ID Inválido</title>
                <style>
                    body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
                    .error { background: #ffe6e6; border: 1px solid #ff9999; padding: 20px; border-radius: 8px; text-align: center; }
                </style>
            </head>
            <body>
                <div class="error">
                    <h2>❌ Erro</h2>
                    <p>ID fornecido não é um hash MD5 válido.</p>
                    <p>O ID deve ter 32 caracteres hexadecimais.</p>
                </div>
            </body>
            </html>
            """, 400
        
        # Busca o registro pelo hash
        record = get_email_from_hash(email_id)
    
    # Se foi fornecido um email direto
    elif email_direct:
        # Valida o formato do email
        if not is_valid_email(email_direct):
            return """
            <!DOCTYPE html>
            <html lang="pt-BR">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Erro - Email Inválido</title>
                <style>
                    body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
                    .error { background: #ffe6e6; border: 1px solid #ff9999; padding: 20px; border-radius: 8px; text-align: center; }
                </style>
            </head>
            <body>
                <div class="error">
                    <h2>❌ Erro</h2>
                    <p>Formato de e-mail inválido.</p>
                    <p>Use um e-mail válido como: usuario@exemplo.com</p>
                </div>
            </body>
            </html>
            """, 400
        
        # Busca o registro pelo email
        try:
            response = supabase.table('advs').select('*').eq('emils', email_direct).execute()
            if response.data:
                record = response.data[0]
        except Exception as e:
            print(f"Erro ao buscar email: {e}")
    
    # Se o registro não foi encontrado
    if not record:
        return """
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Email Não Encontrado</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
                .warning { background: #fff3cd; border: 1px solid #ffeaa7; padding: 20px; border-radius: 8px; text-align: center; }
            </style>
        </head>
        <body>
            <div class="warning">
                <h2>⚠️ Email Não Encontrado</h2>
                <p>O e-mail fornecido não foi encontrado em nossa base de dados.</p>
                <p>Você pode já não estar recebendo nossos e-mails.</p>
            </div>
        </body>
        </html>
        """
    
    # Verifica se já está na blacklist
    if record.get('blacklist'):
        return """
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Já Descadastrado</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
                .success { background: #e6ffe6; border: 1px solid #99ff99; padding: 20px; border-radius: 8px; text-align: center; }
            </style>
        </head>
        <body>
            <div class="success">
                <h2>✅ Confirmação</h2>
                <p>Seu e-mail já estava removido da lista.</p>
                <p>Você não receberá mais mensagens.</p>
            </div>
        </body>
        </html>
        """
    
    # Atualiza o status para blacklist
    if update_blacklist_status(record['id'], record['emils']):
        return """
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Descadastro Realizado</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
                .success { background: #e6ffe6; border: 1px solid #99ff99; padding: 20px; border-radius: 8px; text-align: center; }
            </style>
        </head>
        <body>
            <div class="success">
                <h2>✅ Sucesso!</h2>
                <p>Seu e-mail foi removido com sucesso da lista.</p>
                <p>Você não receberá mais mensagens.</p>
            </div>
        </body>
        </html>
        """
    else:
        return """
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Erro Interno</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
                .error { background: #ffe6e6; border: 1px solid #ff9999; padding: 20px; border-radius: 8px; text-align: center; }
            </style>
        </head>
        <body>
            <div class="error">
                <h2>❌ Erro</h2>
                <p>Erro interno do servidor. Tente novamente mais tarde.</p>
            </div>
        </body>
        </html>
        """, 500

@app.route('/blacklist')
def get_blacklist():
    """
    Rota que retorna todos os emails na blacklist com informações detalhadas.
    """
    try:
        blacklisted_emails = get_blacklisted_emails()
        return jsonify({
            'status': 'success',
            'total': len(blacklisted_emails),
            'blacklist': blacklisted_emails
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Erro ao carregar blacklist',
            'error': str(e)
        }), 500

@app.route('/blacklist/hashes')
def get_blacklist_hashes():
    """
    Rota que retorna apenas os hashes MD5 dos emails na blacklist.
    Útil para verificação rápida pelo app local.
    """
    try:
        hashes = get_blacklisted_hashes()
        return jsonify({
            'status': 'success',
            'total': len(hashes),
            'blacklist': hashes
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Erro ao carregar hashes da blacklist',
            'error': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    """
    Página de erro 404 personalizada.
    """
    return """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Página Não Encontrada</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
            .error { background: #ffe6e6; border: 1px solid #ff9999; padding: 20px; border-radius: 8px; text-align: center; }
        </style>
    </head>
    <body>
        <div class="error">
            <h2>❌ Página Não Encontrada</h2>
            <p>A página que você está procurando não existe.</p>
            <p><a href="/">Voltar ao início</a></p>
        </div>
    </body>
    </html>
    """, 404

if __name__ == '__main__':
    # Configuração para desenvolvimento local e produção
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)