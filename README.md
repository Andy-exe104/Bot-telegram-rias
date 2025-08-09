# 🎭 Rias Gremory Telegram Bot

Un bot de Telegram inspirado en Rias Gremory con sistema de rangos, llaves premium y gestión de usuarios.

## 🌟 Características

- **Sistema de Rangos**: Issei (Owner), Admin, Seller, Premium, Free User
- **Gestión de Llaves**: Generación y canje de llaves premium
- **Base de Datos PostgreSQL**: Almacenamiento persistente de usuarios y llaves
- **Hora Colombiana**: Saludos dinámicos según la hora del día
- **Interfaz Temática**: Diseño inspirado en Rias Gremory con emojis
- **Comandos Organizados**: Estructura modular y escalable

## 🚀 Instalación

### 1. Clonar el repositorio
```bash
git clone <repository-url>
cd rias-gremory-bot
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno
Copia `.env.example` a `.env` y configura las variables:

```env
BOT_TOKEN=your_telegram_bot_token_here
DB_HOST=your_database_host
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
ERROR_CHAT_ID=your_chat_id_for_error_notifications
```

### 4. Ejecutar el bot
```bash
python main.py
```

## 🎯 Comandos Disponibles

### Comandos Generales
- `/start` o `*start` - Iniciar el bot con imagen de Rias y botón de @Kenny_kx
- `/info` o `*info` - Ver información del usuario, rango y tiempo restante
- `/logs` o `*logs` - Ver errores recientes (solo Issei)

### Comandos de Administración (Solo Issei)
- `/addadmin <user_id> [días]` o `*addadmin <user_id> [días]` - Agregar administrador
- `/addseller <user_id> [días]` o `*addseller <user_id> [días]` - Agregar vendedor
- `/addpremium <user_id> [días]` o `*addpremium <user_id> [días]` - Agregar usuario premium

### Comandos de Llaves (Issei, Admin, Seller)
- `/generatekey <rango> <días>` o `*generatekey <rango> <días>` - Generar llave premium
- `/keys` o `*keys` - Ver llaves disponibles

### Comandos de Usuario
- `/redeemkey <código>` o `*redeemkey <código>` - Canjear llave premium

### Prefijos Soportados
El bot acepta comandos con los siguientes prefijos: `*`, `:`, `#`, `$`, `&`, `-`, `=`, `%`, `@`

**Ejemplos:**
- `*start` - Iniciar bot
- `:info` - Ver información
- `#generatekey premium 30` - Generar llave premium

## 🎭 Sistema de Rangos

| Rango | Emoji | Descripción | Permisos |
|-------|-------|-------------|----------|
| Issei | 👑 | Dueño del bot | Todos los comandos |
| Admin | ⚡ | Administrador | Gestión de usuarios y llaves |
| Seller | 💎 | Vendedor | Generar llaves y agregar premium |
| Premium | 🌟 | Usuario Premium | Comandos básicos + canje de llaves |
| Free User | 👤 | Usuario Gratuito | Comandos básicos |

## 🗄️ Base de Datos

El bot crea automáticamente las siguientes tablas:

### Tabla `users`
- `id`: ID único del usuario
- `telegram_id`: ID de Telegram
- `username`: Nombre de usuario
- `first_name`: Nombre
- `last_name`: Apellido
- `rank`: Rango del usuario
- `created_at`: Fecha de registro
- `expires_at`: Fecha de expiración
- `is_active`: Estado activo



## 🚀 Despliegue en Railway

1. **Conectar repositorio** a Railway
2. **Configurar variables de entorno**:
   - `BOT_TOKEN`
   - `DB_HOST`
   - `DB_NAME`
   - `DB_USER`
   - `DB_PASSWORD`
   - `ERROR_CHAT_ID` (opcional - para notificaciones de errores)
3. **Desplegar** - Railway detectará automáticamente el Procfile

## 🎨 Características Especiales

- **Saludos Dinámicos**: Buenos días, buenas tardes, buenas noches según hora colombiana
- **Imagen de Rias**: Imagen personalizada en el comando /start
- **Botón @Kenny_kx**: Enlace directo al creador
- **Emojis Temáticos**: Diseño visual inspirado en Rias Gremory
- **Gestión de Expiración**: Control automático de fechas de vencimiento
- **Sistema de Logging**: Registro de errores en archivo y notificaciones Telegram

## 🔧 Estructura del Proyecto

```
rias-gremory-bot/
├── main.py              # Archivo principal del bot
├── requirements.txt     # Dependencias
├── Procfile            # Configuración para Railway
├── runtime.txt         # Versión de Python para Railway
├── .env.example        # Variables de entorno de ejemplo
├── database/
│   ├── __init__.py
│   └── database.py     # Gestión de base de datos
├── logs/               # Directorio de logs (se crea automáticamente)
├── commands/
│   ├── __init__.py
│   ├── start.py        # Comando /start
│   ├── info.py         # Comando /info
│   ├── admin.py        # Comandos de administración
│   └── logs.py         # Comando para ver logs
├── utils/
│   ├── __init__.py
│   └── logger.py       # Sistema de logging
└── config/
    ├── __init__.py
    └── prefixes.py     # Configuración de prefijos
```

## 🎭 Créditos

- **Creador**: @Kenny_kx
- **Inspiración**: Rias Gremory (High School DxD)
- **Desarrollo**: Python + python-telegram-bot

## 📝 Licencia

Este proyecto está bajo la licencia MIT.

---

💖 *¡Disfruta de tu experiencia con Rias Gremory!* 💖
