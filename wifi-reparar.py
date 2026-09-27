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


def fix_wifi_registry():
    # 1. Desactivar Inicio Rapido para mantener la configuracion tras reiniciar
    try:
        power_path = r"SYSTEM\CurrentControlSet\Control\Session Manager\Power"
        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, power_path, 0, winreg.KEY_SET_VALUE
        ) as key:
            winreg.SetValueEx(key, "HiberbootEnabled", 0, winreg.REG_DWORD, 0)
    except Exception:
        pass

    # 2. Desactivar drivers en Windows Update de forma general (sin romper DeviceInstall)
    try:
        wu_path = r"SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate"
        with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, wu_path) as key:
            winreg.SetValueEx(
                key, "ExcludeWUDriversInQualityUpdate", 0, winreg.REG_DWORD, 1
            )
    except Exception:
        pass

    # 3. Aplicar CountryRegion5G y bSupport80211d
    base_class = r"SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}"
    found = False

    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, base_class) as base_key:
            count = winreg.QueryInfoKey(base_key)[0]
            for i in range(count):
                subkey = winreg.EnumKey(base_key, i)
                target_path = f"{base_class}\\{subkey}"
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
                            break
                except (FileNotFoundError, OSError):
                    continue
    except Exception as e:
        print(f"Error: {e}")

    return found


def restart_adapter():
    ps_cmd = 'Get-NetAdapter | Where-Object { $_.InterfaceDescription -match "8822CE" } | Restart-NetAdapter'
    subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_cmd],
        capture_output=True,
    )
    time.sleep(2)


def main():
    if not is_admin():
        run_as_admin()
        sys.exit(0)

    print("Configurando Realtek RTL8822CE...")
    if fix_wifi_registry():
        restart_adapter()
        print("\n[OK] Conectate a tu red normalmente.")
    else:
        print("\n[X] Adaptador no encontrado.")

    input("\nPresiona Enter para salir...")


if __name__ == "__main__":
    main()
