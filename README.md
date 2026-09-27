# Reparador y Persistencia Wi-Fi 5 GHz para Realtek RTL8822CE en Windows

Solución integral y automatizada diseñada para resolver el fallo de la tarjeta de red interna **Realtek RTL8822CE** en Windows, la cual no detecta o falla al conectarse a redes Wi-Fi de **5 GHz** (especialmente en canales altos como el 149), garantizando conexión inmediata y persistencia total frente a **reinicios** y **apagados completos** sin intervención manual.

---

## ⚙️ ¿Qué hace la solución?

1. **Elevación automática de privilegios (UAC):**
   - El script detecta el nivel de permisos y solicita automáticamente elevación de Administrador mediante Windows ShellExecute al ejecutarse.

2. **Habilitación de Directivas de Ejecución:**
   - Configura la directiva `RemoteSigned` en la máquina local para permitir la inicialización sin bloqueos de seguridad (`PSSecurityException`).

3. **Desactivación del Inicio Rápido (`powercfg /h off`):**
   - Deshabilita la hibernación del núcleo de Windows (Fast Startup), forzando a que cada encendido desde apagado sea un arranque en frío limpio, evitando estados de energía PCIe corruptos o suspensión de canales.

4. **Desbloqueo de frecuencias en el Registro de Windows:**
   - Localiza dinámicamente la clave exacta de la controladora en:
     `HKLM:\SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}`
   - Habilita el estándar regulatorio internacional: `bSupport80211d = 1`.
   - Modifica la región de radiofrecuencia a: `CountryRegion5G = 7` (desbloquea canales 149 al 165).

5. **Reinicio por hardware de la interfaz de red:**
   - Ejecuta `Restart-NetAdapter` con una pausa previa de estabilización (5 segundos) para recargar el firmware del chip en caliente y levantar la radiofrecuencia.

6. **Blindaje Dual de Persistencia (Tareas Programadas de Windows):**
   - Almacena el script de soporte en `C:\ProgramData\FixWifi\fix.ps1`.
   - **Tarea 1 (`FixRealtek5G_Boot`):** Se dispara en el arranque del sistema (`/sc onstart`) con un retardo de 10 segundos bajo la cuenta de más alto privilegio (`/ru SYSTEM /rl highest`), blindando el encendido tras apagados.
   - **Tarea 2 (`FixRealtek5G_Logon`):** Se dispara al iniciar sesión en el escritorio (`/sc onlogon`) con un retardo de 5 segundos, garantizando la estabilidad del enlace interactivo.

---

## 📋 Requisitos

- **Sistema Operativo:** Windows 10 / Windows 11 (64-bit).
- **Adaptador:** Realtek RTL8822CE 802.11ac PCIe Adapter.
- **Entorno:** Python 3 (usa únicamente librerías estándar nativas: `ctypes`, `os`, `subprocess`, `sys`).
- **PowerShell:** PowerShell 5.1 o superior (nativo en Windows).

---

## 🚀 Uso Rápido

1. Guarda el código en un archivo llamado `wifi-reparar.py`.
2. Haz clic derecho y selecciona **Ejecutar con Python** (o doble clic).
3. Acepta el cuadro de diálogo de permisos de Administrador (UAC).
4. El script mostrará en la misma ventana de consola el progreso en tiempo real: desactivación de Fast Startup, creación del archivo `.ps1`, registro de las tareas duales y reinicio de la tarjeta.
5. El Wi-Fi quedará conectado al instante y no requerirá volver a ejecutar ningún script tras apagar o reiniciar el equipo.
