# SSH Tunnel Manager - Nuevas Funcionalidades

## Soporte para Nombres e Iconos Personalizados

El SSH Tunnel Manager ahora soporta configurar nombres (labels) personalizados e iconos para cada túnel en el archivo de configuración YAML.

### Nuevos Campos en la Configuración

#### `name` (Opcional)
Define un nombre personalizado que se mostrará en la interfaz en lugar de la clave del diccionario.

#### `icon` (Opcional)  
Define un icono personalizado para el túnel. Puede ser:
- Nombre del archivo sin extensión (busca en `./icons/`)
- Nombre del archivo con extensión `.png`
- Ruta completa al archivo de icono

### Ejemplo de Configuración

```yaml
gitlab:
  name: "GitLab Server"
  icon: "gitlab"
  browser_open: https://gitlab.example.com
  local_port: 443
  proxy_host: demo-bastion
  remote_address: 10.10.10.10:443

postgresql:
  name: "PostgreSQL Database"
  icon: "database"
  local_port: 5432
  proxy_host: demo-bastion
  remote_address: 10.10.10.20:9999

rabbitmq:
  name: "RabbitMQ Management"
  icon: "rabbitmq"
  browser_open: http://127.0.0.1
  local_port: 15672
  proxy_host: demo-bastion
  remote_address: 10.10.10.30:15672

kubernetes:
  name: "K8s Dashboard"
  icon: "kubernetes"
  browser_open: https://127.0.0.1:8443
  local_port: 8443
  proxy_host: demo-bastion
  remote_address: 10.10.10.40:8443
```

### Comportamiento de Iconos

1. **Con campo `icon` especificado:**
   - Busca el archivo en `./icons/{icon}`
   - Si no existe, busca `./icons/{icon}.png`
   - Si no existe, usa el icono por defecto

2. **Sin campo `icon`:**
   - Busca `./icons/{clave_del_diccionario}.png`
   - Si no existe, usa el icono por defecto

### Retrocompatibilidad

Las configuraciones existentes seguirán funcionando sin cambios. Los campos `name` e `icon` son completamente opcionales.

### Iconos Disponibles

Los siguientes iconos están disponibles en la carpeta `icons/`:
- `acunetix.png`
- `browser.png`
- `gitlab.png`
- `harbor.png`
- `kill.png`
- `kubernetes.png`
- `nessus.png`
- `rabbitmq.png`
- `settings.png`
- `start.png`
- `stop.png`
- `tenable.png`
- `tunnel.png`
