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
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, f'"{__file__}"', None, 1
    )


def block_driver_updates():
    # 1. Bloqueo general de drivers en actualizaciones de calidad de Windows Update
    wu_policy_path = r"SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate"
    try:
        with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, wu_policy_path) as key:
            winreg.SetValueEx(
                key,
                "ExcludeWUDriversInQualityUpdate",
                0,
                winreg.REG_DWORD,
                1,
            )
        print("[+] Directiva aplicada: Excluir drivers de Windows Update.")
    except Exception as e:
        print(f"[-] Error bloqueando actualizaciones generales de drivers: {e}")

    # 2. Bloqueo estricto por Hardware ID (PCI\VEN_10EC&DEV_C822) para la RTL8822CE
    dev_policy_path = (
        r"SOFTWARE\Policies\Microsoft\Windows\DeviceInstall\Restrictions"
    )
    deny_list_path = rf"{dev_policy_path}\DenyDeviceIDs"
    try:
        with winreg.CreateKey(
            winreg.HKEY_LOCAL_MACHINE, dev_policy_path
        ) as key:
            winreg.SetValueEx(key, "DenyDeviceIDs", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(
                key, "DenyDeviceIDsRetroactive", 0, winreg.REG_DWORD, 0
            )

        with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, deny_list_path) as key:
            winreg.SetValueEx(
                key, "1", 0, winreg.REG_SZ, r"PCI\VEN_10EC&DEV_C822"
            )

        print(
            "[+] Blindaje aplicado: Bloqueo de instalación por Hardware ID (RTL8822CE)."
        )
    except Exception as e:
        print(f"[-] Error aplicando restricción de DeviceInstall: {e}")


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

                            # Limpiar valores manuales que limitan velocidad
                            for param in ["WirelessMode", "BW_20_40_80M"]:
                                try:
                                    winreg.DeleteValue(key, param)
                                except FileNotFoundError:
                                    pass

                            # Desbloquear canales altos (canal 149), 802.11d y apagar ahorro de energía
                            winreg.SetValueEx(
                                key, "bSupport80211d", 0, winreg.REG_SZ, "1"
                            )
                            winreg.SetValueEx(
                                key, "CountryRegion5G", 0, winreg.REG_SZ, "7"
                            )
                            winreg.SetValueEx(
                                key,
                                "RoamingSensitivityType",
                                0,
                                winreg.REG_SZ,
                                "0",
                            )
                            winreg.SetValueEx(
                                key, "PnPCapabilities", 0, winreg.REG_DWORD, 24
                            )

                            found = True
                            print(
                                "[+] Parámetros de 5 GHz configurados en el Registro."
                            )
                            break
                except (FileNotFoundError, OSError):
                    continue
    except Exception as e:
        print(f"[-] Error accediendo al Registro: {e}")

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
    print("[+] Controlador recargado.")


def clear_wifi_profile(profile_name="Remi 5G"):
    subprocess.run(
        ["netsh", "wlan", "delete", "profile", f"name={profile_name}"],
        capture_output=True,
    )


def main():
    if not is_admin():
        run_as_admin()
        sys.exit(0)

    print("=" * 60)
    print(" Optimizador y Blindaje Realtek RTL8822CE - 5 GHz ")
    print("=" * 60)

    block_driver_updates()

    if configure_realtek_5ghz():
        restart_adapter_hardware()
        clear_wifi_profile("Remi 5G")
        print("\n[✓] Configuración y blindaje completados exitosamente.")
        print(
            "[*] Puedes instalar las actualizaciones de Windows sin riesgo a sobreescritura."
        )
    else:
        print("\n[X] No se encontró el adaptador Realtek RTL8822CE.")

    input("\nPresiona Enter para cerrar...")


if __name__ == "__main__":
    main()
