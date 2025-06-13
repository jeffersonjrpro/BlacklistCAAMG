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

# Carrega variáveis de ambiente
load_dotenv()

# Configurar logging para Windows Server
log_file = os.path.join(os.path.dirname(__file__), 'app.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/app.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configurações do Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL', "https://fawgofnpdzyxvgupplwb.supabase.co")
SUPABASE_KEY = os.getenv('SUPABASE_KEY', "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZhd2dvZm5wZHp5eHZndXBwbHdiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDM3ODQ5ODIsImV4cCI6MjA1OTM2MDk4Mn0.yc4Aok9wlVlz5YfHKQsgNREPpyAZ47TW7JBt6bVYZvc")

# Inicializa cliente Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def debug_print(message):
    """Função para debug com log em arquivo"""
    print(message, flush=True)
    logger.info(message)

def is_valid_email(email):
    """Verifica se o formato do email é válido"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Template HTML moderno para descadastro
UNSUBSCRIBE_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% if status == 'success' %}Descadastro Realizado{% else %}Erro no Descadastro{% endif %} - CAAMG</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            padding: 40px;
            max-width: 500px;
            width: 100%;
            text-align: center;
            animation: slideUp 0.6s ease-out;
        }
        @keyframes slideUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .icon {
            font-size: 64px;
            margin-bottom: 20px;
            animation: bounce 1s ease-in-out;
        }
        @keyframes bounce {
            0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
            40% { transform: translateY(-10px); }
            60% { transform: translateY(-5px); }
        }
        .success { color: #27ae60; }
        .error { color: #e74c3c; }
        h1 {
            color: #2c3e50;
            margin-bottom: 20px;
            font-size: 28px;
            font-weight: 600;
        }
        .message {
            color: #7f8c8d;
            font-size: 16px;
            line-height: 1.6;
            margin-bottom: 30px;
        }
        .email-display {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            border-left: 4px solid #3498db;
        }
        .email-text {
            font-family: monospace;
            font-size: 16px;
            color: #2c3e50;
            font-weight: 600;
        }
        .footer {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ecf0f1;
            color: #95a5a6;
            font-size: 14px;
        }
        .logo {
            color: #3498db;
            font-weight: bold;
            font-size: 18px;
        }
        .contact-info {
            background: #e8f4fd;
            border-radius: 10px;
            padding: 15px;
            margin-top: 20px;
            font-size: 14px;
            color: #2c3e50;
        }
    </style>
</head>
<body>
    <div class="container">
        {% if status == 'success' %}
            <div class="icon success">✅</div>
            <h1>Descadastro Realizado!</h1>
            <p class="message">Seu e-mail foi removido da nossa lista de contatos com sucesso.</p>
            
            <div class="email-display">
                <div class="email-text">📧 {{ email }}</div>
            </div>
            
            <p class="message">
                <strong>Você não receberá mais e-mails desta lista.</strong><br>
                
            </p>
            
            
        {% else %}
            <div class="icon error">❌</div>
            <h1>Erro no Descadastro</h1>
            <p class="message">{{ message }}</p>
            <p class="message">Tente novamente ou entre em contato com nosso suporte.</p>
        {% endif %}
        
        <div class="footer">
            <div class="logo">CAAMG</div>
            
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    """Página inicial moderna"""
    return """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sistema de Blacklist - CAAMG</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: white;
                padding: 20px;
            }
            .container { max-width: 800px; margin: 0 auto; padding: 40px 20px; }
            .header { text-align: center; margin-bottom: 50px; }
            .logo { font-size: 48px; margin-bottom: 20px; }
            h1 { font-size: 36px; margin-bottom: 10px; }
            .subtitle { font-size: 18px; opacity: 0.9; }
            .card {
                background: rgba(255,255,255,0.1);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 30px;
                margin: 20px 0;
                border: 1px solid rgba(255,255,255,0.2);
            }
            .endpoint {
                background: rgba(255,255,255,0.05);
                border-radius: 10px;
                padding: 15px;
                margin: 10px 0;
                border-left: 4px solid #3498db;
            }
            .method { 
                color: #2ecc71; 
                font-weight: bold; 
                font-family: monospace;
            }
            .url { 
                color: #f39c12; 
                font-family: monospace;
                word-break: break-all;
            }
            .description { 
                color: rgba(255,255,255,0.8); 
                margin-top: 5px;
            }
            .status {
                display: flex;
                justify-content: space-between;
                align-items: center;
                background: rgba(46, 204, 113, 0.2);
                border-radius: 10px;
                padding: 15px;
                margin-top: 30px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">🚫</div>
                <h1>Sistema de Blacklist</h1>
                <p class="subtitle">CAAMG - Docker Container</p>
            </div>
            
            <div class="card">
                <h2>📡 Endpoints Disponíveis</h2>
                
                <div class="endpoint">
                    <div><span class="method">GET</span> <span class="url">/status</span></div>
                    <div class="description">Status do sistema e estatísticas</div>
                </div>
                
                <div class="endpoint">
                    <div><span class="method">GET</span> <span class="url">/unsubscribe?email=EMAIL</span></div>
                    <div class="description">Descadastrar e-mail da lista</div>
                </div>
                
                <div class="endpoint">
                    <div><span class="method">GET</span> <span class="url">/blacklist</span></div>
                    <div class="description">Listar todos os e-mails bloqueados</div>
                </div>
                
                <div class="endpoint">
                    <div><span class="method">GET</span> <span class="url">/blacklist/hashes</span></div>
                    <div class="description">Listar hashes MD5 da blacklist</div>
                </div>
                
                <div class="endpoint">
                    <div><span class="method">GET</span> <span class="url">/check?email=EMAIL</span></div>
                    <div class="description">Verificar se e-mail está na blacklist</div>
                </div>
            </div>
            
            <div class="status">
                <span>🟢 Sistema Online</span>
                <span>Docker Container</span>
            </div>
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
        'platform': 'Docker Container',
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
    format_type = request.args.get('format', 'html')  # MUDANÇA: HTML por padrão
    
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
            # Atualizar registro existente
            response = supabase.table('advs').update({
                'blacklist': True,
                'data_bloqueio': datetime.now().isoformat(),
                'motivo': motivo
            }).eq('email', email.lower().strip()).execute()
        else:
            # Criar novo registro
            response = supabase.table('advs').insert({
                'email': email.lower().strip(),
                'blacklist': True,
                'data_bloqueio': datetime.now().isoformat(),
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
            'server': 'Docker Container'
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
            'server': 'Docker Container'
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
            'server': 'Docker Container',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao buscar blacklist: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'server': 'Docker Container'
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
            'server': 'Docker Container'
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
    return jsonify({
        'status': 'error',
        'message': 'Página não encontrada',
        'error': '404 Not Found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Página de erro 500 personalizada"""
    return jsonify({
        'status': 'error',
        'message': 'Erro interno do servidor',
        'error': '500 Internal Server Error'
    }), 500

if __name__ == '__main__':
    # Configurações para Docker
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    debug_print(f"Iniciando servidor na porta {port}")
    debug_print(f"Modo debug: {debug_mode}")
    debug_print("🐳 Executando em container Docker")
    
    # Para produção em Docker, usar apenas Flask
    app.run(host='0.0.0.0', port=port, debug=debug_mode)