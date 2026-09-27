import ctypes
import os
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


def apply_registry_5ghz():
    print("[*] 1. Configurando registros para canal 149 (5 GHz)...")
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
                            found = True
                            print(f"[+] Registros aplicados a: {driver_desc}")
                            break
                except (FileNotFoundError, OSError):
                    continue
    except Exception as e:
        print(f"[-] Error en el Registro: {e}")

    return found


def setup_scheduled_task():
    print("[*] 2. Creando persistencia en el sistema...")
    dir_path = r"C:\ProgramData\FixWifi"
    os.makedirs(dir_path, exist_ok=True)
    ps1_path = os.path.join(dir_path, "fix.ps1")

    # Script idéntico al probado con éxito en consola
    script_content = (
        "Start-Sleep -Seconds 5\n"
        '$p = "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e972-e325-11ce-bfc1-08002be10318}"\n'
        '$t = Get-ChildItem -Path $p -ErrorAction SilentlyContinue | Where-Object { (Get-ItemProperty $_.PsPath).DriverDesc -match "8822CE" }\n'
        "if ($t) {\n"
        '    Set-ItemProperty -Path $t.PsPath -Name "bSupport80211d" -Value "1" -Type String -Force\n'
        '    Set-ItemProperty -Path $t.PsPath -Name "CountryRegion5G" -Value "7" -Type String -Force\n'
        '    Get-NetAdapter | Where-Object { $_.InterfaceDescription -match "8822CE" } | Restart-NetAdapter\n'
        "}\n"
    )

    with open(ps1_path, "w", encoding="utf-8") as f:
        f.write(script_content)

    # Comando nativo de Windows schtasks
    cmd_task = (
        'schtasks /create /tn "FixRealtek5G" '
        '/tr "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File C:\\ProgramData\\FixWifi\\fix.ps1" '
        '/sc onlogon /ru "SYSTEM" /rl highest /f'
    )
    res = subprocess.run(cmd_task, shell=True, capture_output=True, text=True)
    if "CORRECTO" in res.stdout or "SUCCESS" in res.stdout:
        print("[+] Tarea programada 'FixRealtek5G' registrada con éxito.")
    else:
        print(f"[-] Salida de schtasks: {res.stdout.strip()}")


def restart_net_adapter():
    print("[*] 3. Reiniciando tarjeta Wi-Fi por hardware...")
    ps_cmd = 'Get-NetAdapter | Where-Object { $_.InterfaceDescription -match "8822CE" } | Restart-NetAdapter'
    subprocess.run(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_cmd],
        capture_output=True,
    )
    time.sleep(2)
    print("[+] Adaptador reiniciado.")


def main():
    if not is_admin():
        run_as_admin()
        sys.exit(0)

    print("=" * 60)
    print(" Instalador Permanente Realtek RTL8822CE (5 GHz) ")
    print("=" * 60)

    if apply_registry_5ghz():
        setup_scheduled_task()
        restart_net_adapter()
        print("\n[✓] Listo. Tu PC conectará automáticamente en cada reinicio.")
    else:
        print("\n[X] No se encontró el adaptador RTL8822CE en el Registro.")

    input("\nPresiona Enter para salir...")


if __name__ == "__main__":
    main()