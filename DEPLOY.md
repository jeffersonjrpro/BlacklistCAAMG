# 🚀 CAAMAIL - Guia de Deploy Docker

## Problema Resolvido: Porta 80 em Uso

**Erro encontrado:**
```
failed to bind host port for 0.0.0.0:80: address already in use
```

**Solução aplicada:**
- Alterado para porta **8080** para evitar conflito
- Funciona perfeitamente em qualquer servidor

## 📦 Instalação Rápida

```bash
# 1. Clonar repositório
git clone https://github.com/jeffersonjrpro/BlacklistCAAMG.git
cd BlacklistCAAMG

# 2. Executar instalação automática
chmod +x install.sh
./install.sh
```

## 🌐 URLs de Acesso

- **Principal:** http://seu-servidor:8080
- **Status:** http://seu-servidor:8080/status
- **API:** http://seu-servidor:8080/unsubscribe?email=teste@teste.com

## 🔧 Comandos Úteis

```bash
# Ver logs
docker-compose logs -f

# Parar serviços
docker-compose down

# Reiniciar
docker-compose restart

# Rebuild completo
docker-compose build --no-cache && docker-compose up -d

# Debug
./debug-docker.sh
```

## 🎯 Para Usar na Porta 80

Se quiser usar a porta 80 (padrão), pare o serviço que está usando:

```bash
# Identificar serviço
sudo netstat -tulpn | grep :80

# Parar Apache (se existir)
sudo systemctl stop apache2
sudo systemctl disable apache2

# Ou parar Nginx (se existir)
sudo systemctl stop nginx
sudo systemctl disable nginx

# Alterar docker-compose.yml
# ports: "80:80" e "443:443"

# Reiniciar containers
docker-compose down && docker-compose up -d
```

## ✅ Status dos Serviços

- ✅ Aplicação Flask: `caamail-app` (porta interna 5000)
- ✅ Proxy Nginx: `caamail-nginx` (porta externa 8080)
- ✅ Banco Supabase: Conectado
- ✅ Healthchecks: Ativos 