# server/constants/error_messages.py

DUPLICATE_ERROR_MESSAGES = {
    "users": "No se puede registrar el usuario: el correo o nombre de usuario ya existe.",
    "roles": "No se puede crear el rol: ya existe un rol con este nombre.",
    "actions": "No se puede crear la acción: ya existe una acción con este identificador.",
    "modules": "No se puede crear el módulo: ya existe un módulo con este nombre o clave.",
    "permissions": "No se puede crear el permiso: ya existe un permiso con esta combinación de módulo y acción.",
}

DEFAULT_DUPLICATE_MESSAGE = "Este recurso ya ha sido registrado anteriormente."
