from flask import Flask, request, jsonify
import json
import os
import hashlib
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv
import sys
import logging

# Configurar logging para aparecer no Render
logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Forçar flush dos prints
def debug_print(message):
    print(message, flush=True)
    logger.info(message)

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
    Retorna o email se encontrado.
    """
    try:
        # Busca todos os registros e verifica o hash localmente
        response = supabase.table('advs').select('*').execute()
        
        for record in response.data:
            if record.get('email'):  # Mudança: emils → email
                record_hash = hashlib.md5(record['email'].encode()).hexdigest()
                if record_hash == email_hash:
                    return record['email']
        return None
    except Exception as e:
        print(f"Erro ao buscar email no Supabase: {e}")
        return None

def update_blacklist_status(email, status):
    """
    Atualiza o status de blacklist no Supabase.
    """
    try:
        data = {
            'blacklist': status,
            'data_bloqueio': datetime.now().isoformat(),
            'motivo': 'Descadastro via link'
        }
        
        response = supabase.table('advs').update(data).eq('email', email).execute()  # Mudança: emils → email
        return {'success': len(response.data) > 0, 'data': response.data}
    except Exception as e:
        print(f"Erro ao atualizar blacklist no Supabase: {e}")
        return {'success': False, 'error': str(e)}

def get_blacklisted_emails():
    """
    Retorna todos os emails que estão na blacklist.
    """
    try:
        response = supabase.table('advs').select('email, data_bloqueio, motivo').eq('blacklist', True).execute()  # Mudança: emils → email
        return response.data
    except Exception as e:
        print(f"Erro ao buscar blacklist no Supabase: {e}")
        return []

def get_blacklisted_hashes():
    """
    Retorna todos os hashes MD5 dos emails que estão na blacklist.
    """
    try:
        response = supabase.table('advs').select('email').eq('blacklist', True).execute()  # Mudança: emils → email
        hashes = []
        for record in response.data:
            if record.get('email'):  # Mudança: emils → email
                email_hash = hashlib.md5(record['email'].encode()).hexdigest()
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

@app.route('/unsubscribe', methods=['GET'])
def unsubscribe():
    """
    Endpoint para descadastramento de emails - VERSÃO DEBUG
    """
    email = request.args.get('email')
    
    debug_print(f"=== DEBUG INICIO === Email recebido: {email}")
    
    if not email:
        debug_print("=== DEBUG === Sem email fornecido")
        return render_error_page("Email obrigatório", "Forneça um email válido.")
    
    if not is_valid_email(email):
        debug_print(f"=== DEBUG === Email inválido: {email}")
        return render_error_page("Email inválido", "Formato de email inválido.")
    
    try:
        debug_print(f"=== DEBUG === Tentando inserir no Supabase: {email}")
        
        # Inserção direta e simples com nome correto da coluna
        result = supabase.table('advs').insert({
            'email': email,  # ← Nome correto da coluna
            'blacklist': True,
            'data_bloqueio': datetime.now().isoformat(),
            'motivo': 'Descadastro via link',
            'gestor': 'Sistema',
            'nome': 'Descadastrado'
        }).execute()
        
        debug_print(f"=== DEBUG === Resultado Supabase: {result}")
        debug_print(f"=== DEBUG === Dados inseridos: {len(result.data)} registros")
        
        if result.data:
            debug_print("=== DEBUG === SUCESSO! Renderizando página de sucesso")
            return render_success_page(f"Email {email} descadastrado com sucesso!")
        else:
            debug_print("=== DEBUG === FALHA! Nenhum dado retornado")
            return render_error_page("Erro", "Falha ao descadastrar.")
            
    except Exception as e:
        debug_print(f"=== DEBUG ERRO === {str(e)}")
        import traceback
        debug_print(f"=== DEBUG TRACEBACK === {traceback.format_exc()}")
        return render_error_page("Erro interno", f"Erro: {str(e)}")

def add_to_blacklist_by_email(email):
    """
    Adiciona email à blacklist. Se não existir, cria novo registro.
    Se existir, apenas atualiza o status de blacklist.
    """
    try:
        debug_print(f"[DEBUG] Tentando adicionar à blacklist: {email}")
        
        # Primeiro, verifica se o email já existe
        response = supabase.table('advs').select('*').eq('email', email).execute()  # Mudança: emils → email
        debug_print(f"[DEBUG] Busca existente - encontrados: {len(response.data)} registros")
        
        if response.data:
            # Email existe, atualiza registro
            debug_print(f"[DEBUG] Email existe, atualizando registro...")
            result = supabase.table('advs').update({
                'blacklist': True,
                'data_bloqueio': datetime.now().isoformat(),
                'motivo': 'Descadastro via link'
            }).eq('email', email).execute()  # Mudança: emils → email
            debug_print(f"[DEBUG] Update realizado: {len(result.data)} registros atualizados")
        else:
            # Email não existe, cria novo registro com TODOS os campos possíveis
            debug_print(f"[DEBUG] Email não existe, criando novo registro...")
            novo_registro = {
                'email': email,  # Mudança: emils → email
                'blacklist': True,
                'data_bloqueio': datetime.now().isoformat(),
                'motivo': 'Descadastro via link',
                'gestor': 'Sistema',
                'nome': 'Usuário Descadastrado',
                'empresa': 'Descadastrado',
                'telefone': '',
                'cargo': '',
                'setor': '',
                'observacoes': 'Descadastrado automaticamente via link'
            }
            
            result = supabase.table('advs').insert(novo_registro).execute()
            debug_print(f"[DEBUG] Insert realizado: {len(result.data)} registros criados")
        
        debug_print(f"[DEBUG] Operação concluída com sucesso")
        return {'success': True, 'data': result.data}
        
    except Exception as e:
        debug_print(f"[ERROR] Erro ao adicionar à blacklist: {str(e)}")
        debug_print(f"[ERROR] Tipo do erro: {type(e).__name__}")
        import traceback
        debug_print(f"[ERROR] Traceback: {traceback.format_exc()}")
        return {'success': False, 'error': str(e)}

def add_hash_to_blacklist(email_hash):
    """
    Adiciona apenas o hash à blacklist quando o email não é encontrado.
    """
    try:
        # Cria registro com hash, sem email específico
        result = supabase.table('advs').insert({
            'email': f'hash_{email_hash}@descadastrado.com',  # Mudança: emils → email
            'blacklist': True,
            'data_bloqueio': datetime.now().isoformat(),
            'motivo': 'Descadastro via hash - email não encontrado',
            'gestor': 'Sistema',
            'nome': 'Hash Descadastrado'
        }).execute()
        
        return {'success': True, 'data': result.data}
    except Exception as e:
        print(f"Erro ao adicionar hash à blacklist: {str(e)}")
        return {'success': False, 'error': str(e)}

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

@app.route('/test-supabase')
def test_supabase():
    """
    Rota de teste para verificar conexão com Supabase
    """
    try:
        # Teste 1: Listar registros existentes para ver a estrutura
        response = supabase.table('advs').select('*').limit(5).execute()
        debug_print(f"Teste SELECT: {len(response.data)} registros encontrados")
        
        # Mostrar estrutura da tabela
        if response.data:
            debug_print(f"Estrutura da tabela: {list(response.data[0].keys())}")
            debug_print(f"Primeiro registro: {response.data[0]}")
        
        return jsonify({
            'status': 'success',
            'select_count': len(response.data),
            'table_structure': list(response.data[0].keys()) if response.data else [],
            'sample_record': response.data[0] if response.data else None,
            'message': 'Estrutura da tabela descoberta!'
        })
        
    except Exception as e:
        debug_print(f"Erro no teste Supabase: {str(e)}")
        return jsonify({
            'status': 'error',
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

def render_success_page(message):
    """
    Renderiza página de sucesso para descadastramento
    """
    return f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Descadastramento Realizado</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }}
            .success {{ background: #e6ffe6; border: 1px solid #99ff99; padding: 20px; border-radius: 8px; text-align: center; }}
            .icon {{ font-size: 48px; margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <div class="success">
            <div class="icon">✅</div>
            <h2>Descadastramento Realizado com Sucesso!</h2>
            <p>{message}</p>
            <p><small>Você não receberá mais e-mails desta lista.</small></p>
        </div>
    </body>
    </html>
    """

def render_error_page(titulo, message):
    """
    Renderiza página de erro para descadastramento
    """
    return f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Erro no Descadastramento</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }}
            .error {{ background: #ffe6e6; border: 1px solid #ff9999; padding: 20px; border-radius: 8px; text-align: center; }}
            .icon {{ font-size: 48px; margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <div class="error">
            <div class="icon">❌</div>
            <h2>{titulo}</h2>
            <p>{message}</p>
            <p><small>Tente novamente ou entre em contato conosco.</small></p>
        </div>
    </body>
    </html>
    """

def is_valid_md5(hash_string):
    """
    Verifica se a string é um hash MD5 válido
    """
    import re
    return bool(re.match(r'^[a-f0-9]{{32}}$', hash_string.lower()))

if __name__ == '__main__':
    # Configuração para desenvolvimento local e produção
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)