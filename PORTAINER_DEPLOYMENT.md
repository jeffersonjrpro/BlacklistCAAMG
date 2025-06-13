# 🐳 Deployment via Portainer

## Pré-requisitos
- Docker instalado no servidor
- Portainer instalado e rodando
- Acesso ao endereço MAC do servidor (para verificar: `ip link show`)

## Método 1: Stack via Docker Compose

### 1. Acessar Portainer
- Acesse seu Portainer: `http://IP_DO_SERVIDOR:9000`
- Faça login com suas credenciais

### 2. Criar Stack
1. No menu lateral, clique em **Stacks**
2. Clique em **Add stack**
3. Nome: `blacklist-api`
4. Cole o conteúdo do `docker-compose.yml`:

```yaml
version: '3.8'

services:
  blacklist-api:
    image: blacklist-api:latest
    container_name: blacklist-api
    restart: unless-stopped
    ports:
      - "5000:5000"
    environment:
      - SUPABASE_URL=https://fawgofnpdzyxvgupplwb.supabase.co
      - SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZhd2dvZm5wZHp5eHZndXBwbHdiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDM3ODQ5ODIsImV4cCI6MjA1OTM2MDk4Mn0.yc4Aok9wlVlz5YfHKQsgNREPpyAZ47TW7JBt6bVYZvc
      - FLASK_ENV=production
      - TZ=America/Sao_Paulo
    volumes:
      - blacklist-logs:/app/logs
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:5000/status"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - blacklist-network

volumes:
  blacklist-logs:

networks:
  blacklist-network:
    driver: bridge
```

5. Clique em **Deploy the stack**

## Método 2: Build da Imagem no Portainer

### 1. Fazer Upload dos Arquivos
1. No menu lateral, clique em **Images**
2. Clique em **Build a new image**
3. Nome da imagem: `blacklist-api:latest`
4. Faça upload de um ZIP contendo:
   - `main.py`
   - `Dockerfile`
   - `requirements.txt`
   - `.dockerignore`

### 2. Criar Container
1. Vá para **Containers**
2. Clique em **Add container**
3. Configure:
   - **Nome**: `blacklist-api`
   - **Imagem**: `blacklist-api:latest`
   - **Portas**: `5000:5000`
   - **Variáveis de ambiente**:
     ```
     SUPABASE_URL=https://fawgofnpdzyxvgupplwb.supabase.co
     SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZhd2dvZm5wZHp5eHZndXBwbHdiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzE5NjczMzcsImV4cCI6MjA0NzU0MzMzN30.xvI-oMwEa45LsWpPNY89R8sJJOu8Q8AJJwM_KqXKWmw
     FLASK_ENV=production
     TZ=America/Sao_Paulo
     ```
   - **Volumes**: `/app/logs` → Volume nomeado `blacklist-logs`
   - **Restart policy**: Unless stopped

## Método 3: Via Git Repository (Recomendado)

### 1. Configurar Git Repository
1. No Portainer, vá para **Stacks**
2. Clique em **Add stack**
3. Selecione **Repository**
4. Configure:
   - **Nome**: `blacklist-api`
   - **Repository URL**: `https://github.com/jeffersonjrpro/BlacklistCAAMG`
   - **Reference**: `main`
   - **Compose file**: `docker-compose.yml`

### 2. Deploy
1. Clique em **Deploy the stack**
2. Aguarde o build e deploy automático

## Verificação do Deployment

### 1. Verificar Container
- Vá para **Containers**
- Verifique se `blacklist-api` está **running**
- Clique no container para ver logs

### 2. Testar API
- Acesse: `http://IP_DO_SERVIDOR:5000`
- Teste status: `http://IP_DO_SERVIDOR:5000/status`

### 3. Monitoramento
- **Logs**: Portainer → Containers → blacklist-api → Logs
- **Stats**: CPU, Memória, Rede em tempo real
- **Health**: Verificação automática a cada 30s

## Configuração de Proxy Reverso (Opcional)

### Nginx via Docker
```yaml
nginx-proxy:
  image: nginx:alpine
  ports:
    - "80:80"
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf
  depends_on:
    - blacklist-api
```

### Traefik (Alternativa)
```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.blacklist.rule=Host(`blacklist.seudominio.com`)"
  - "traefik.http.services.blacklist.loadbalancer.server.port=5000"
```

## Comandos Úteis para Verificar MAC Address

```bash
# Via SSH no servidor
ip link show

# Ou
cat /sys/class/net/*/address

# Para interface específica
ip link show eth0
```

## Troubleshooting

### Container não inicia
1. Verificar logs no Portainer
2. Verificar se porta 5000 está livre
3. Verificar variáveis de ambiente

### Erro de conexão Supabase
1. Verificar SUPABASE_URL e SUPABASE_KEY
2. Testar conectividade: `curl https://fawgofnpdzyxvgupplwb.supabase.co`

### Problemas de permissão
1. Verificar se volume `/app/logs` tem permissões corretas
2. Container roda como usuário `appuser` (não-root)

## Backup e Restore

### Backup
```bash
# Backup do volume de logs
docker run --rm -v blacklist-logs:/data -v $(pwd):/backup alpine tar czf /backup/blacklist-logs.tar.gz -C /data .
```

### Restore
```bash
# Restore do volume de logs
docker run --rm -v blacklist-logs:/data -v $(pwd):/backup alpine tar xzf /backup/blacklist-logs.tar.gz -C /data
``` 