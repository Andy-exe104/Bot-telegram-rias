# Configuración de prefijos para comandos
# Los prefijos permitidos son: *, :, #, $, &, -, =, %, @

COMMAND_PREFIXES = ['*', ':', '#', '$', '&', '-', '=', '%', '@']

def is_valid_prefix(text: str) -> bool:
    """Verifica si el texto comienza con un prefijo válido"""
    return any(text.startswith(prefix) for prefix in COMMAND_PREFIXES)

def get_command_without_prefix(text: str) -> str:
    """Obtiene el comando sin el prefijo"""
    for prefix in COMMAND_PREFIXES:
        if text.startswith(prefix):
            return text[len(prefix):].strip()
    return text

def add_prefix_to_command(command: str, prefix: str = '*') -> str:
    """Agrega un prefijo a un comando"""
    if prefix not in COMMAND_PREFIXES:
        prefix = '*'
    return f"{prefix}{command}"