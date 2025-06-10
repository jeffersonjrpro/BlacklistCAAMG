#!/bin/bash

echo "🔍 CAAMAIL - Debug Docker"
echo "========================"

echo "📋 Status dos containers:"
docker-compose ps

echo ""
echo "📊 Logs do nginx:"
docker-compose logs nginx --tail=20

echo ""
echo "📊 Logs da aplicação:"
docker-compose logs caamail-app --tail=10

echo ""
echo "🌐 Teste de conectividade:"
echo "Testando aplicação diretamente..."
curl -s http://localhost:5000/status | head -5

echo ""
echo "🔗 Redes Docker:"
docker network ls | grep caamail

echo ""
echo "💾 Volumes Docker:"
docker volume ls | grep caamail

echo ""
echo "🔍 Processos em execução:"
docker stats --no-stream

echo ""
echo "🚨 Containers com problemas:"
docker ps -a --filter "status=exited" 