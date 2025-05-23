import os
import sys
import logging
from flask import Flask, request, jsonify, render_template_string
import json
import hashlib
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv
import traceback

# Configurações para Windows Server
if os.name == 'nt':  # Windows
    # Configurar encoding
    import locale
    locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')

# Carrega variáveis de ambiente
load_dotenv()

# Configurar logging para Windows Server
log_file = os.path.join(os.path.dirname(__file__), 'app.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configurações do Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL', "https://fawgofnpdzyxvgupplwb.supabase.co")
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY', "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZhd2dvZm5wZHp5eHZndXBwbHdiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDM3ODQ5ODIsImV4cCI6MjA1OTM2MDk4Mn0.yc4Aok9wlVlz5YfHKQsgNREPpyAZ47TW7JBt6bVYZvc")

# Inicializa cliente Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def debug_print(message):
    """Função para debug com log em arquivo"""
    print(message, flush=True)
    logger.info(message)

def is_valid_email(email):
    """Verifica se o formato do email é válido"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def render_success_page(message):
    """Renderiza página de sucesso para descadastramento"""
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
    """Renderiza página de erro para descadastramento"""
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

@app.route('/')
def home():
    """Rota principal com informações básicas da API"""
    debug_print("Acesso à página inicial")
    return """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>API de Descadastramento - Windows Server</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
            .container { text-align: center; }
            .info { background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0; }
            .server-info { background: #e6f3ff; padding: 15px; border-radius: 8px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚫 API de Descadastramento</h1>
            <div class="server-info">
                <h3>🖥️ Windows Server + IIS</h3>
                <p>Sistema rodando em ambiente Windows</p>
            </div>
            <div class="info">
                <h3>Endpoints Disponíveis:</h3>
                <p><strong>GET /unsubscribe?email=EMAIL</strong> - Descadastrar por e-mail</p>
                <p><strong>GET /blacklist</strong> - Consultar lista de descadastrados</p>
                <p><strong>GET /blacklist/hashes</strong> - Consultar hashes da blacklist</p>
                <p><strong>GET /status</strong> - Status do sistema</p>
            </div>
            <p>Sistema funcionando corretamente! ✅</p>
            <p><small>Integrado com Supabase - Windows Server</small></p>
        </div>
    </body>
    </html>
    """

@app.route('/status')
def status():
    """Rota de status do sistema"""
    try:
        # Teste de conexão com Supabase
        response = supabase.table('advs').select('*').limit(1).execute()
        supabase_status = "✅ Conectado"
    except Exception as e:
        supabase_status = f"❌ Erro: {str(e)}"
    
    status_info = {
        'status': 'running',
        'platform': 'Windows Server + IIS',
        'python_version': sys.version,
        'supabase': supabase_status,
        'timestamp': datetime.now().isoformat()
    }
    
    return jsonify(status_info)

@app.route('/unsubscribe')
def unsubscribe():
    """Descadastrar email da lista"""
    email = request.args.get('email')
    email_id = request.args.get('id')
    motivo = request.args.get('motivo', 'Descadastro via API')
    format_type = request.args.get('format', 'json')
    
    if not email and not email_id:
        error_msg = 'Email ou ID é obrigatório'
        if format_type == 'html':
            return render_template_string(UNSUBSCRIBE_TEMPLATE, 
                status='error', message=error_msg)
        return jsonify({'status': 'error', 'message': error_msg}), 400
    
    try:
        if email_id:
            # Buscar por hash MD5
            response = supabase.table('advs').select('*').execute()
            target_record = None
            
            for record in response.data:
                if record.get('email'):
                    record_hash = hashlib.md5(record['email'].lower().strip().encode()).hexdigest()
                    if record_hash == email_id.lower():
                        target_record = record
                        email = record['email']
                        break
            
            if not target_record:
                error_msg = 'Email não encontrado'
                if format_type == 'html':
                    return render_template_string(UNSUBSCRIBE_TEMPLATE, 
                        status='error', message=error_msg)
                return jsonify({'status': 'error', 'message': error_msg}), 404
        
        # Verificar se email existe na tabela
        existing = supabase.table('advs').select('*').eq('email', email.lower().strip()).execute()
        
        if existing.data:
            # Atualizar registro existente - USAR data_bloqueio
            response = supabase.table('advs').update({
                'blacklist': True,
                'data_bloqueio': datetime.now().isoformat(),  # CORRIGIDO
                'motivo': motivo
            }).eq('email', email.lower().strip()).execute()
        else:
            # Criar novo registro - USAR data_bloqueio
            response = supabase.table('advs').insert({
                'email': email.lower().strip(),
                'blacklist': True,
                'data_bloqueio': datetime.now().isoformat(),  # CORRIGIDO
                'motivo': motivo,
                'nome': 'Descadastrado'
            }).execute()
        
        logger.info(f"✅ Email {email} adicionado à blacklist")
        
        success_msg = f'Email {email} descadastrado com sucesso!'
        timestamp = datetime.now().isoformat()
        
        if format_type == 'html':
            return render_template_string(UNSUBSCRIBE_TEMPLATE, 
                status='success', email=email, motivo=motivo, timestamp=timestamp)
        
        return jsonify({
            'status': 'success',
            'message': success_msg,
            'email': email,
            'motivo': motivo,
            'timestamp': timestamp,
            'server': 'Ubuntu Server'
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar unsubscribe: {str(e)}")
        error_msg = f'Erro interno: {str(e)}'
        
        if format_type == 'html':
            return render_template_string(UNSUBSCRIBE_TEMPLATE, 
                status='error', message=error_msg)
        
        return jsonify({
            'status': 'error',
            'message': 'Erro interno do servidor',
            'error': str(e),
            'server': 'Ubuntu Server'
        }), 500

@app.route('/blacklist')
def get_blacklist():
    """Listar todos os emails na blacklist"""
    try:
        response = supabase.table('advs').select('email, data_bloqueio, motivo, nome').eq('blacklist', True).execute()  # CORRIGIDO
        
        blacklist_data = []
        for record in response.data:
            blacklist_data.append({
                'email': record.get('email'),
                'data_bloqueio': record.get('data_bloqueio'),  # CORRIGIDO
                'motivo': record.get('motivo'),
                'nome': record.get('nome')
            })
        
        return jsonify({
            'status': 'success',
            'total': len(blacklist_data),
            'blacklist': blacklist_data,
            'server': 'Ubuntu Server',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao buscar blacklist: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'server': 'Ubuntu Server'
        }), 500

@app.route('/blacklist/hashes')
def get_blacklist_hashes():
    """Rota que retorna apenas os hashes MD5 dos emails na blacklist"""
    try:
        response = supabase.table('advs').select('email').eq('blacklist', True).execute()
        hashes = []
        for record in response.data:
            if record.get('email'):
                email_hash = hashlib.md5(record['email'].encode()).hexdigest()
                hashes.append(email_hash)
        
        return jsonify({
            'status': 'success',
            'total': len(hashes),
            'blacklist': hashes,
            'server': 'Windows Server + IIS'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Erro ao carregar hashes da blacklist',
            'error': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Página de erro 404 personalizada"""
    return render_error_page("Página Não Encontrada", "A página que você está procurando não existe.")

@app.errorhandler(500)
def internal_error(error):
    """Página de erro 500 personalizada"""
    return render_error_page("Erro Interno", "Ocorreu um erro interno no servidor.")

if __name__ == '__main__':
    # Configurações para Windows Server
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    debug_print(f"Iniciando servidor na porta {port}")
    debug_print(f"Modo debug: {debug_mode}")
    
    # Para Windows Server, usar waitress ao invés do servidor Flask padrão
    try:
        from waitress import serve
        debug_print("Usando Waitress WSGI Server")
        serve(app, host='0.0.0.0', port=port, threads=6)
    except ImportError:
        debug_print("Waitress não encontrado, usando servidor Flask padrão")
        app.run(host='0.0.0.0', port=port, debug=debug_mode)
