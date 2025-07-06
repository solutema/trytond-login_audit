##################
Login Audit Module
##################

# Módulo: Login Audit (Auditoría de Inicio de Sesión)

Este módulo registra los inicios y cierres de sesión de los usuarios del sistema Tryton, incluyendo la IP, fecha y hora de acceso. También muestra la duración de cada sesión y permite visualizar los registros en una interfaz amigable.

---

## 📂 Modelo

El modelo principal que utiliza este módulo es:

- `ir.session.log`: Almacena la auditoría de cada sesión iniciada y finalizada.

Campos incluidos:
- `session_key`
- `user_login`
- `user_name`
- `login_datetime`
- `logout_datetime`
- `duration`
- `ip_address`

Además, se derivan los siguientes campos funciones para facilitar la lectura:
- `login_date`, `login_time` (en formato 12h con zona horaria `America/Santo_Domingo`)
- `logout_date`, `logout_time` (formato similar)

---

## 🧭 Menú en Tryton

Una vez instalado el módulo, el menú para acceder al registro de sesiones estará disponible en:

Administración → Usuarios → Auditoria de Inicio de Sesión
