# Reparador Wi-Fi 5 GHz para Realtek RTL8822CE en Windows

Script en Python diseñado para solucionar de forma permanente el problema en Windows donde la tarjeta de red interna **Realtek RTL8822CE** no detecta redes Wi-Fi de **5 GHz** (especialmente zonas con cobertura móvil o puntos de acceso en canales altos como el 149), o negocia a velocidades muy bajas (modo legacy 802.11a a 54 Mbps).

---

## ⚙️ ¿Qué hace este script?

1. **Solicitud automática de permisos de Administrador:** Se eleva mediante el control de cuentas de usuario (UAC) de Windows al hacer doble clic, sin requerir abrir consolas manualmente.
2. **Purga de controladores conflictivos:** Utiliza `pnputil` para detectar y desinstalar del Driver Store paquetes defectuosos (como la versión 2024.0.8.141) que Windows Update instala y que rompen la negociación a 5 GHz.
3. **Blindaje contra Windows Update:** Habilita la directiva `ExcludeWUDriversInQualityUpdate` en el Registro para evitar que Microsoft Update vuelva a sobrescribir el controlador funcional con versiones genéricas inestables.
4. **Persistencia tras reinicios (Arranque limpio):** Desactiva el Inicio Rápido de Windows (`HiberbootEnabled = 0` y `powercfg /h off`), evitando que el bus PCIe cargue estados congelados en memoria que bloquean las frecuencias altas al reiniciar o apagar el equipo.
5. **Desbloqueo total de la banda de 5 GHz:**
   - Activa el estándar de regulación internacional (`bSupport80211d = 1`).
   - Configura el dominio `CountryRegion5G = 7` para desbloquear los canales altos (149 al 165).
   - Apaga la suspensión selectiva por ahorro de energía en el bus PCIe (`PnPCapabilities = 24`).
6. **Reconexión automática sin pérdida de credenciales:**
   - Reinicia la interfaz a nivel de hardware mediante `Restart-NetAdapter`.
   - Mantiene los perfiles existentes con `connectionmode=auto`, asegurando que la conexión se restablezca de inmediato conservando la contraseña guardada.

---

## 📋 Requisitos

- **Sistema Operativo:** Windows 10 / Windows 11.
- **Hardware:** Tarjeta de red interna Realtek RTL8822CE 802.11ac PCIe.
- **Python:** Python 3 instalado en Windows (utiliza únicamente módulos nativos: `winreg`, `subprocess`, `ctypes`, `re`, `sys`, `time`).

---

## 🚀 Uso rápido (incluso en equipos recién formateados)

1. Descarga el archivo `wifi-reparar.py` (o clona el repositorio).
2. Haz doble clic sobre `wifi-reparar.py`.
3. Acepta la ventana de confirmación de permisos de Administrador (UAC).
4. El script limpiará versiones rotas, aplicará la configuración en el Registro y recargará la tarjeta.
5. El sistema detectará las redes 5 GHz de inmediato y se conectará automáticamente a tu red sin tener que reescribir tu contraseña en cada reinicio.
