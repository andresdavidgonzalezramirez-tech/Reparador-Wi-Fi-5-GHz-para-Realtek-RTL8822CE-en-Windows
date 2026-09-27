import ctypes
import re
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


def purge_bad_drivers():
    print("[*] 1. Purgando drivers conflictivos de Realtek...")
    try:
        output = subprocess.check_output(
            ["pnputil", "/enum-drivers"], text=True, errors="ignore"
        )
        entries = output.split("\n\n")
        for entry in entries:
            if "Realtek" in entry and (
                "Net" in entry or "2024.0.8" in entry or "8822CE" in entry
            ):
                match = re.search(r"oem\d+\.inf", entry, re.IGNORECASE)
                if match:
                    inf_name = match.group(0)
                    print(f"[-] Eliminando paquete: {inf_name}...")
                    subprocess.run(
                        ["pnputil", "/delete-driver", inf_name, "/uninstall", "/force"],
                        capture_output=True,
                    )
    except Exception as e:
        print(f"[-] Error purgando drivers: {e}")


def prevent_driver_updates():
    print("[*] 2. Desactivando actualizacion de controladores en Windows Update...")
    try:
        wu_path = r"SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate"
        with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, wu_path) as key:
            winreg.SetValueEx(
                key, "ExcludeWUDriversInQualityUpdate", 0, winreg.REG_DWORD, 1
            )
        print("[+] Windows Update protegido contra reemplazo de drivers.")
    except Exception as e:
        print(f"[-] Error en directiva de Windows Update: {e}")


def disable_fast_startup():
    print("[*] 3. Desactivando Inicio Rapido (Fast Startup)...")
    try:
        power_path = r"SYSTEM\CurrentControlSet\Control\Session Manager\Power"
        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, power_path, 0, winreg.KEY_SET_VALUE
        ) as key:
            winreg.SetValueEx(key, "HiberbootEnabled", 0, winreg.REG_DWORD, 0)
        # Desactivar hibernacion para garantizar encendido limpio de la tarjeta PCIe
        subprocess.run(["powercfg", "/h", "off"], capture_output=True)
        print("[+] Arranque limpio asegurado para cada reinicio.")
    except Exception as e:
        print(f"[-] Error configurando energia: {e}")


def apply_5ghz_settings():
    print("[*] 4. Configurando registros 5 GHz (canal 149 y 802.11d)...")
    base = r"SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}"
    found = False

    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, base) as base_key:
            count = winreg.QueryInfoKey(base_key)[0]
            for i in range(count):
                subkey = winreg.EnumKey(base_key, i)
                target_path = f"{base}\\{subkey}"
                try:
                    with winreg.OpenKey(
                        winreg.HKEY_LOCAL_MACHINE,
                        target_path,
                        0,
                        winreg.KEY_READ | winreg.KEY_WRITE,
                    ) as key:
                        driver_desc, _ = winreg.QueryValueEx(key, "DriverDesc")
                        if "8822CE" in driver_desc.upper():
                            winreg.SetValueEx(
                                key, "bSupport80211d", 0, winreg.REG_SZ, "1"
                            )
                            winreg.SetValueEx(
                                key, "CountryRegion5G", 0, winreg.REG_SZ, "7"
                            )
                            winreg.SetValueEx(
                                key, "PnPCapabilities", 0, winreg.REG_DWORD, 24
                            )
                            found = True
                            print(f"[+] Registros aplicados a: {driver_desc}")
                            break
                except (FileNotFoundError, OSError):
                    continue
    except Exception as e:
        print(f"[-] Error en el Registro: {e}")

    return found


def restart_adapter():
    print("[*] 5. Reiniciando tarjeta por hardware...")
    ps_cmd = 'Get-NetAdapter | Where-Object { $_.InterfaceDescription -match "8822CE" } | Restart-NetAdapter'
    subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_cmd],
        capture_output=True,
    )
    time.sleep(2)


def ensure_auto_connect(profile_name="Remi 5G"):
    # Mantiene la clave existente y fuerza la autoconexion inmediata
    subprocess.run(
        [
            "netsh",
            "wlan",
            "set",
            "profileparameter",
            f"name={profile_name}",
            "connectionmode=auto",
            "nonBroadcast=no",
        ],
        capture_output=True,
    )


def main():
    if not is_admin():
        run_as_admin()
        sys.exit(0)

    print("=" * 60)
    print(" Optimizacion Permanente Realtek RTL8822CE - 5 GHz ")
    print("=" * 60)

    purge_bad_drivers()
    prevent_driver_updates()
    disable_fast_startup()

    if apply_5ghz_settings():
        restart_adapter()
        ensure_auto_connect("Remi 5G")
        print("\n[✓] Sistema configurado de forma permanente.")
        print("[*] Puedes apagar o reiniciar el PC; se conectara solo y sin pedir clave.")
    else:
        print("\n[!] Reescaneando dispositivos...")
        subprocess.run(["pnputil", "/scan-devices"], capture_output=True)
        time.sleep(3)
        if apply_5ghz_settings():
            restart_adapter()
            ensure_auto_connect("Remi 5G")
            print("\n[✓] Listo tras reescaneo.")
        else:
            print("\n[X] No se encontro la tarjeta.")

    input("\nPresiona Enter para cerrar...")


if __name__ == "__main__":
    main()
