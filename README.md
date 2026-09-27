# Reparador Wi-Fi 5 GHz para Realtek RTL8822CE en Windows

Script en Python diseñado para solucionar el problema recurrente en Windows donde la tarjeta de red interna **Realtek RTL8822CE** no detecta redes Wi-Fi de **5 GHz** (especialmente puntos de acceso y hotspots móviles en canales altos como el 149), o negocia a velocidades muy bajas (modo legacy 802.11a a 54 Mbps).

---

## ⚙️ ¿Qué hace este script?

1. **Solicita permisos de Administrador automáticamente:** Al ejecutarse con doble clic, eleva privilegios mediante el UAC de Windows sin requerir comandos adicionales.
2. **Protección contra Windows Update:** Habilita la directiva `ExcludeWUDriversInQualityUpdate` en el Registro para evitar que Microsoft Update sobrescriba o degrade el controlador con versiones genéricas defectuosas.
3. **Desbloqueo de canales de 5 GHz:**
   - Activa el soporte internacional de dominios regulatorios (`bSupport80211d = 1`).
   - Configura `CountryRegion5G = 7` para desbloquear canales altos (149–165).
   - Elimina limitaciones obsoletas (`WirelessMode` y `BW_20_40_80M`) para permitir la negociación nativa a máxima velocidad en **Wi-Fi 5 (802.11ac)**.
   - Desactiva el ahorro de energía agresivo del bus PCIe (`PnPCapabilities = 24`).
4. **Reinicio de hardware:** Utiliza `Restart-NetAdapter` para recargar el driver en el bus PCIe de inmediato, sin necesidad de reiniciar la computadora.
5. **Limpieza de caché:** Elimina perfiles Wi-Fi desfasados para evitar bucles de conexión infinita ("Conectando...").

---

## 📋 Requisitos

- **Sistema Operativo:** Windows 10 / Windows 11.
- **Hardware:** Tarjeta de red interna Realtek RTL8822CE 802.11ac PCIe.
- **Python:** Python 3 instalado en Windows (no requiere dependencias externas ni `pip`).

---

## 🚀 Uso en equipos recién formateados

1. Clona este repositorio o descarga el archivo `wifi-reparar.py`.
2. Haz doble clic sobre `wifi-reparar.py`.
3. Confirma la ventana de permisos de Administrador de Windows (UAC).
4. El script aplicará los registros, blindará el controlador y reiniciará la interfaz.
5. Selecciona tu red Wi-Fi de 5 GHz en la barra de tareas e introduce tu contraseña.
