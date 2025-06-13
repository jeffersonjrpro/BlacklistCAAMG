#!/bin/bash

# Script de Instalação CAAMAIL - Docker + Nginx
# Autor: CAAMAIL Team
# Data: $(date)

set -e

echo "🚀 CAAMAIL - Instalação Docker + Nginx"
echo "======================================"

# Verificar se está na pasta correta
if [ ! -f "main.py" ]; then
    echo "❌ Erro: Arquivo main.py não encontrado!"
    echo "Execute este script na pasta do projeto BlacklistCAAMG"
    exit 1
fi

# Verificar Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado! Instale primeiro:"
    echo "curl -fsSL https://get.docker.com | sh"
    exit 1
fi

# Verificar Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose não encontrado! Instalando..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

echo "✅ Pré-requisitos verificados"

# Criar arquivo .env se não existir
if [ ! -f ".env" ]; then
    echo "📝 Criando arquivo .env..."
    cp config.env .env
    echo "✅ Arquivo .env criado"
fi

# Parar containers existentes
echo "🛑 Parando containers existentes..."
docker-compose down 2>/dev/null || true

# Remover containers antigos
echo "🧹 Limpando containers antigos..."
docker container prune -f
docker image prune -f

# Build da aplicação
echo "🔨 Construindo imagem da aplicação..."
docker-compose build --no-cache

# Iniciar serviços
echo "🚀 Iniciando serviços..."
docker-compose up -d

# Aguardar serviços
echo "⏳ Aguardando serviços iniciarem..."
sleep 30

# Verificar status
echo "🔍 Verificando status dos serviços..."
docker-compose ps

# Testar aplicação
echo "🧪 Testando aplicação..."
if curl -f http://localhost:8080/status > /dev/null 2>&1; then
    echo "✅ Aplicação funcionando!"
else
    echo "⚠️  Aplicação ainda inicializando..."
fi

echo ""
echo "🎉 INSTALAÇÃO CONCLUÍDA!"
echo "========================"
echo ""
echo "📍 URLs de Acesso:"
echo "   • Local: http://localhost:8080"
echo "   • Status: http://localhost:8080/status"
echo "   • Nginx Health: http://localhost:8080/nginx-health"
echo ""
echo "🔧 Comandos Úteis:"
echo "   • Ver logs: docker-compose logs -f"
echo "   • Parar: docker-compose down"
echo "   • Reiniciar: docker-compose restart"
echo "   • Rebuild: docker-compose build --no-cache && docker-compose up -d"
echo ""
echo "📋 Configurar DNS:"
echo "   caamail.caamg.com.br:8080 → $(curl -s ifconfig.me)"
echo ""
echo "✅ Setup completo!"