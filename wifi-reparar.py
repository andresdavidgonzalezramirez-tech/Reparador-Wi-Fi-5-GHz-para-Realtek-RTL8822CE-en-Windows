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


def main():
    if not is_admin():
        run_as_admin()
        sys.exit(0)

    print("Configurando Realtek RTL8822CE...")

    path = r"SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}"
    encontrado = False

    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path) as base_key:
            total_claves = winreg.QueryInfoKey(base_key)[0]
            for i in range(total_claves):
                subclave = winreg.EnumKey(base_key, i)
                target_path = f"{path}\\{subclave}"
                try:
                    with winreg.OpenKey(
                        winreg.HKEY_LOCAL_MACHINE,
                        target_path,
                        0,
                        winreg.KEY_READ | winreg.KEY_WRITE,
                    ) as key:
                        driver_desc, _ = winreg.QueryValueEx(key, "DriverDesc")
                        if "8822CE" in driver_desc.upper():
                            # Exactamente lo que arreglo el problema:
                            winreg.SetValueEx(
                                key, "bSupport80211d", 0, winreg.REG_SZ, "1"
                            )
                            winreg.SetValueEx(
                                key, "CountryRegion5G", 0, winreg.REG_SZ, "7"
                            )
                            encontrado = True
                            print(f"[+] Valores aplicados en: {driver_desc}")
                            break
                except (FileNotFoundError, OSError):
                    continue
    except Exception as e:
        print(f"[-] Error en el Registro: {e}")

    if encontrado:
        print("[*] Reiniciando tarjeta...")
        ps_cmd = 'Get-NetAdapter | Where-Object { $_.InterfaceDescription -match "8822CE" } | Restart-NetAdapter'
        subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                ps_cmd,
            ],
            capture_output=True,
        )
        time.sleep(2)
        print("\n[✓] Listo. Wi-Fi 5 GHz restaurado.")
    else:
        print("\n[X] No se encontro la tarjeta RTL8822CE.")

    input("\nPresiona Enter para cerrar...")


if __name__ == "__main__":
    main()
