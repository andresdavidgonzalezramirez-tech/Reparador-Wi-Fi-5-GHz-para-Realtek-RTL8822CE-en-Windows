import ctypes
import subprocess
import sys
import time
import winreg


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def run_as_admin():
    # Solicita permisos de Administrador automáticamente si se ejecuta con doble clic
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, f'"{__file__}"', None, 1
    )


def block_driver_updates():
    # Crea la directiva para que Windows Update no sobreescriba ni degrade el controlador
    policy_path = r"SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate"
    try:
        with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, policy_path) as key:
            winreg.SetValueEx(
                key,
                "ExcludeWUDriversInQualityUpdate",
                0,
                winreg.REG_DWORD,
                1,
            )
        print("[+] Directiva aplicada: Actualizaciones de controladores desactivadas en Windows Update.")
        return True
    except Exception as e:
        print(f"[-] Error bloqueando actualizaciones de controladores: {e}")
        return False


def configure_realtek_5ghz():
    base_class = r"SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}"
    found = False

    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, base_class) as base_key:
            subkeys_count = winreg.QueryInfoKey(base_key)[0]
            for i in range(subkeys_count):
                subkey_name = winreg.EnumKey(base_key, i)
                target_path = f"{base_class}\\{subkey_name}"

                try:
                    with winreg.OpenKey(
                        winreg.HKEY_LOCAL_MACHINE,
                        target_path,
                        0,
                        winreg.KEY_READ | winreg.KEY_WRITE,
                    ) as key:
                        driver_desc, _ = winreg.QueryValueEx(key, "DriverDesc")
                        if "8822CE" in driver_desc.upper():
                            print(f"[+] Tarjeta detectada: {driver_desc}")

                            # Limpiar valores manuales que limitan la velocidad
                            for param in ["WirelessMode", "BW_20_40_80M"]:
                                try:
                                    winreg.DeleteValue(key, param)
                                except FileNotFoundError:
                                    pass

                            # Activar canales extendidos de 5 GHz (canal 149), 802.11d y apagar ahorro de energía
                            winreg.SetValueEx(key, "bSupport80211d", 0, winreg.REG_SZ, "1")
                            winreg.SetValueEx(key, "CountryRegion5G", 0, winreg.REG_SZ, "7")
                            winreg.SetValueEx(key, "RoamingSensitivityType", 0, winreg.REG_SZ, "0")
                            winreg.SetValueEx(key, "PnPCapabilities", 0, winreg.REG_DWORD, 24)

                            found = True
                            print("[+] Parámetros de 5 GHz configurados correctamente en el Registro.")
                            break
                except (FileNotFoundError, OSError):
                    continue
    except Exception as e:
        print(f"[-] Error accediendo al Registro de Windows: {e}")

    return found


def restart_adapter_hardware():
    print("[*] Reiniciando adaptador a nivel de hardware (Restart-NetAdapter)...")
    ps_cmd = (
        'Get-NetAdapter | Where-Object { $_.InterfaceDescription -match "8822CE" } '
        "| Restart-NetAdapter"
    )
    subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_cmd],
        capture_output=True,
    )
    time.sleep(2)
    print("[+] Interfaz recargada.")


def clear_wifi_profile(profile_name="Remi 5G"):
    # Elimina el perfil antiguo con handshake roto para evitar bucle de 'Conectando'
    subprocess.run(
        ["netsh", "wlan", "delete", "profile", f"name={profile_name}"],
        capture_output=True,
    )


def main():
    if not is_admin():
        run_as_admin()
        sys.exit(0)

    print("=" * 55)
    print(" Optimizador y Protector Realtek RTL8822CE - 5 GHz ")
    print("=" * 55)

    block_driver_updates()

    if configure_realtek_5ghz():
        restart_adapter_hardware()
        clear_wifi_profile("Remi 5G")
        print("\n[✓] Proceso completado exitosamente.")
        print("[*] Haz clic en 'Remi 5G' en la barra de tareas e ingresa la contraseña.")
    else:
        print("\n[X] No se encontró el adaptador Realtek RTL8822CE.")

    input("\nPresiona Enter para cerrar...")


if __name__ == "__main__":
    main()
