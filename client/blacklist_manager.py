import requests
import hashlib
import os
import sys
from typing import Optional, List, Dict
import time
import logging

# Configurar logging para Windows
logger = logging.getLogger(__name__)

class BlacklistManager:
    """
    Gerenciador de blacklist de emails - Versão Windows Server
    """
    
    def __init__(self, api_url: str = "http://localhost:5000"):
        """
        Inicializa o gerenciador
        Para Windows Server, use: http://seu-servidor-windows:porta
        """
        self.api_url = api_url.rstrip('/')
        self.timeout = 10
        
        # Log de inicialização
        logger.info(f"BlacklistManager inicializado com API: {self.api_url}")
    
    def pode_enviar_email(self, email: str) -> bool:
        """
        Verifica se pode enviar email (True = pode enviar, False = bloqueado)
        """
        try:
            response = requests.get(f"{self.api_url}/blacklist/hashes", timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                email_hash = hashlib.md5(email.lower().encode()).hexdigest()
                is_blocked = email_hash in data.get('blacklist', [])
                
                if is_blocked:
                    logger.info(f"Email bloqueado: {email}")
                    
                return not is_blocked
            else:
                logger.warning(f"API retornou status {response.status_code}")
                return True  # Se der erro na API, permite envio
        except Exception as e:
            logger.error(f"Erro ao verificar blacklist: {str(e)}")
            return True  # Se der erro, permite envio (fail-safe)
    
    def filtrar_lista_emails(self, lista_emails: List[str]) -> Dict[str, List[str]]:
        """
        Filtra lista de emails, separando permitidos e bloqueados
        """
        try:
            response = requests.get(f"{self.api_url}/blacklist/hashes", timeout=self.timeout)
            if response.status_code == 200:
                blacklist_hashes = response.json().get('blacklist', [])
                
                permitidos = []
                bloqueados = []
                
                for email in lista_emails:
                    email_hash = hashlib.md5(email.lower().encode()).hexdigest()
                    if email_hash in blacklist_hashes:
                        bloqueados.append(email)
                    else:
                        permitidos.append(email)
                
                logger.info(f"Filtrados: {len(permitidos)} permitidos, {len(bloqueados)} bloqueados")
                
                return {
                    'permitidos': permitidos,
                    'bloqueados': bloqueados,
                    'total_permitidos': len(permitidos),
                    'total_bloqueados': len(bloqueados)
                }
            else:
                logger.warning(f"Erro na API, permitindo todos os emails")
                return {
                    'permitidos': lista_emails,
                    'bloqueados': [],
                    'total_permitidos': len(lista_emails),
                    'total_bloqueados': 0
                }
        except Exception as e:
            logger.error(f"Erro ao filtrar lista: {str(e)}")
            return {
                'permitidos': lista_emails,
                'bloqueados': [],
                'total_permitidos': len(lista_emails),
                'total_bloqueados': 0
            }
    
    def gerar_link_descadastro(self, email: str) -> str:
        """
        Gera link de descadastro direto por email
        """
        return f"{self.api_url}/unsubscribe?email={email}"
    
    def adicionar_link_html(self, email: str, html_content: str) -> str:
        """
        Adiciona link de descadastro ao HTML do email
        """
        link = self.gerar_link_descadastro(email)
        
        footer_html = f'''
        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; text-align: center;">
            <p style="font-size: 12px; color: #666; margin: 0;">
                Não deseja mais receber estes e-mails? 
                <a href="{link}" style="color: #666; text-decoration: underline;">
                    Clique aqui para se descadastrar
                </a>
            </p>
            <p style="font-size: 10px; color: #999; margin: 5px 0 0 0;">
                Sistema Windows Server - Descadastro automático
            </p>
        </div>
        '''
        
        # Adiciona antes do </body> se existir, senão no final
        if '</body>' in html_content.lower():
            return html_content.replace('</body>', f'{footer_html}</body>')
        else:
            return html_content + footer_html
    
    def obter_estatisticas(self) -> Dict:
        """
        Obtém estatísticas da blacklist
        """
        try:
            response = requests.get(f"{self.api_url}/blacklist", timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Estatísticas obtidas: {data.get('total', 0)} emails na blacklist")
                return data
            return {'status': 'error', 'total': 0}
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {str(e)}")
            return {'status': 'error', 'total': 0}
    
    def testar_conexao(self) -> bool:
        """
        Testa conexão com a API
        """
        try:
            response = requests.get(f"{self.api_url}/status", timeout=5)
            if response.status_code == 200:
                logger.info("Conexão com API OK")
                return True
            else:
                logger.warning(f"API retornou status {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Erro de conexão: {str(e)}")
            return False

# Exemplo de uso específico para Windows
def exemplo_uso_windows():
    """
    Exemplo de uso no Windows Server
    """
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('blacklist.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    # Inicializar (ajuste a URL para seu servidor)
    blacklist = BlacklistManager("http://localhost:5000")
    
    # Testar conexão
    if blacklist.testar_conexao():
        print("✅ Conexão OK")
    else:
        print("❌ Erro de conexão")
    
    # Exemplo de uso
    email_teste = "teste@exemplo.com"
    if blacklist.pode_enviar_email(email_teste):
        print(f"✅ Pode enviar para {email_teste}")
    else:
        print(f"❌ {email_teste} está bloqueado")

if __name__ == "__main__":
    exemplo_uso_windows()