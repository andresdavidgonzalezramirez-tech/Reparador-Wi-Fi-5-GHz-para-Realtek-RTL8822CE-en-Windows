# Reparador y Persistencia Wi-Fi 5 GHz para Realtek RTL8822CE en Windows

Script en Python diseñado para solucionar de forma permanente el problema en Windows donde la tarjeta de red interna **Realtek RTL8822CE** no detecta o falla al conectarse a redes Wi-Fi de **5 GHz** (especialmente puntos de acceso en canales altos como el 149), asegurando que la conexión funcione de inmediato y sobreviva a todos los reinicios del sistema sin intervención manual.

---

## ⚙️ ¿Qué hace este script?

1. **Solicitud automática de privilegios de Administrador:** Detecta el nivel de ejecución y se eleva automáticamente mediante el control de cuentas de usuario (UAC) de Windows al ejecutarlo con doble clic.
2. **Desbloqueo de frecuencias en el Registro:**
   - Localiza la clave de configuración de la tarjeta Realtek dentro de `SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}`.
   - Activa el estándar de dominio regulatorio internacional (`bSupport80211d = 1`).
   - Configura la región de radiofrecuencia (`CountryRegion5G = 7`) para habilitar el rango completo de canales altos (149 al 165).
3. **Persistencia mediante Tarea Programada nativa:**
   - Genera el archivo de soporte `C:\ProgramData\FixWifi\fix.ps1`.
   - Registra una tarea programada en Windows (`FixRealtek5G`) que se ejecuta de forma silenciosa al iniciar sesión (`/sc onlogon`) con privilegios máximos del sistema (`SYSTEM`), eliminando la necesidad de volver a ejecutar scripts o comandos tras reiniciar el equipo.
4. **Reinicio de la tarjeta por hardware:**
   - Ejecuta `Restart-NetAdapter` para recargar el firmware del chip PCIe en caliente, destrabando la conexión al instante y asociándose automáticamente a tu red Wi-Fi sin alterar contraseñas ni perfiles guardados.

---

## 📋 Requisitos

- **Sistema Operativo:** Windows 10 / Windows 11.
- **Hardware:** Tarjeta de red Realtek RTL8822CE 802.11ac PCIe.
- **Python:** Python 3 instalado en Windows (utiliza únicamente librerías estándar nativas: `winreg`, `subprocess`, `ctypes`, `os`, `sys`, `time`).

---

## 🚀 Uso rápido

1. Descarga el archivo `wifi-reparar.py`.
2. Haz clic derecho y selecciona **Ejecutar con Python** (o doble clic).
3. Acepta la ventana de permisos de Administrador (UAC).
4. El script configurará los parámetros en el Registro, registrará la tarea de inicio automático en Windows y reiniciará el adaptador de red.
5. La red de 5 GHz conectará de inmediato y la solución quedará fija para todos los arranques futuros.
