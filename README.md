# Reparador y Persistencia Wi-Fi 5 GHz para Realtek RTL8822CE en Windows

Script en Python diseñado para solucionar de forma definitiva el problema en Windows donde la tarjeta de red interna **Realtek RTL8822CE** no detecta o falla al conectarse a redes Wi-Fi de **5 GHz** (especialmente puntos de acceso en canales altos como el 149), garantizando conexión inmediata y persistencia total tanto en **reinicios** como en **apagados y encendidos completos** sin intervención manual.

---

## ⚙️ ¿Qué hace este script?

1. **Elevación automática de privilegios:** Detecta el nivel de permisos y solicita automáticamente elevación de Administrador mediante el Control de Cuentas de Usuario (UAC) de Windows al ejecutarse.
2. **Desactivación del Inicio Rápido (`powercfg /h off`):**
   - Deshabilita la hibernación del núcleo de Windows (Fast Startup), evitando que el bus PCIe despierte en estados de energía erráticos o revierta la configuración tras apagar el equipo.
3. **Persistencia mediante Tarea Programada de Sistema:**
   - Genera el script de persistencia en `C:\ProgramData\FixWifi\fix_wifi.ps1`.
   - Limpia cualquier tarea previa conflictiva y registra una nueva tarea nativa (`FixRealtek5G`) configurada para ejecutarse en el arranque del sistema (`/sc onstart`) bajo la cuenta con mayores privilegios (`/ru SYSTEM /rl highest`), operando en segundo plano antes de que el usuario inicie sesión.
4. **Espera activa y sincronización de hardware:**
   - Implementa un bucle dinámico que espera activamente la inicialización del adaptador Realtek en el sistema antes de intentar aplicar cambios, evitando fallos por carreras de arranque.
5. **Desbloqueo de frecuencias en el Registro:**
   - Localiza dinámicamente la clave exacta de la controladora en:
     `HKLM:\SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}`
   - Habilita el soporte de dominio regulatorio internacional: `bSupport80211d = "1"`.
   - Configura la región de radiofrecuencia para desbloquear todos los canales altos: `CountryRegion5G = "7"`.
6. **Reinicio limpio de la interfaz de red:**
   - Ejecuta un reinicio forzado del adaptador (`Restart-NetAdapter`) para recargar los parámetros en caliente, permitiendo la conexión inmediata a la red Wi-Fi de 5 GHz sin perder contraseñas ni perfiles guardados.

---

## 📋 Requisitos

- **Sistema Operativo:** Windows 10 / Windows 11.
- **Hardware:** Adaptador de red Realtek RTL8822CE 802.11ac PCIe.
- **Entorno:** Python 3 instalado en Windows (emplea únicamente módulos nativos estándar: `ctypes`, `os`, `subprocess`, `sys`).
- **PowerShell:** PowerShell 5.1 o superior (incluido por defecto en Windows).

---

## 🚀 Uso rápido

1. Guarda el código en un archivo llamado `wifi-reparar.py`.
2. Haz clic derecho sobre el archivo y selecciona **Ejecutar con Python** (o ábrelo con doble clic).
3. Acepta el aviso de permisos de Administrador (UAC).
4. El script desactivará el inicio rápido, creará la tarea de arranque, aplicará los valores de registro y reiniciará la interfaz de red.
5. La red Wi-Fi se reconectará de inmediato y la persistencia quedará blindada contra reinicios y apagados.
