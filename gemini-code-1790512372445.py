import ctypes
import os
import subprocess
import sys


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def run_as_admin():
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, f'"{os.path.abspath(__file__)}"', None, 1
    )


def setup_permanent_fix():
    print("=" * 65)
    print(" CONFIGURACION PERMANENTE REALTEK 8822CE (5 GHz)")
    print("=" * 65)

    fix_dir = r"C:\ProgramData\FixWifi"
    os.makedirs(fix_dir, exist_ok=True)
    ps_file_path = os.path.join(fix_dir, "fix_wifi.ps1")

    # Script exacto de PowerShell con espera activa hasta que el adaptador exista en el sistema
    ps_content = """# Esperar activamente hasta que el adaptador de red este disponible
$attempts = 0
do {
    $nic = Get-NetAdapter | Where-Object { $_.InterfaceDescription -match "8822CE" }
    if (-not $nic) {
        Start-Sleep -Seconds 2
        $attempts++
    }
} while (-not $nic -and $attempts -lt 15)

# Buscar la ruta exacta en el registro de la tarjeta Realtek 8822CE
$path = "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e972-e325-11ce-bfc1-08002be10318}"
$target = Get-ChildItem -Path $path -ErrorAction SilentlyContinue | Where-Object { 
    (Get-ItemProperty $_.PsPath -ErrorAction SilentlyContinue).DriverDesc -match "8822CE" 
} | Select-Object -First 1

if ($target) {
    # Activar soporte de canales extendidos y 802.11d
    Set-ItemProperty -Path $target.PsPath -Name "bSupport80211d" -Value "1" -Type String -Force
    Set-ItemProperty -Path $target.PsPath -Name "CountryRegion5G" -Value "7" -Type String -Force
    Write-Output "Registros aplicados correctamente en $($target.PsPath)"
} else {
    Write-Output "Error: No se localizo la clave de la tarjeta en el registro."
}

# Reiniciar la tarjeta interna
if ($nic) {
    Restart-NetAdapter -Name $nic.Name -Confirm:$false
    Write-Output "Adaptador reiniciado con exito."
} else {
    Write-Output "Error: No se encontro el adaptador para reiniciar."
}
"""

    # 1. Guardar el archivo .ps1 limpio en el disco
    with open(ps_file_path, "w", encoding="utf-8") as f:
        f.write(ps_content)
    print(f"[*] Script base guardado en: {ps_file_path}")

    # 2. Desactivar el Inicio Rapido (Fast Startup)
    # Evita que el bus PCIe quede en estado de bajo consumo erratico tras apagar el PC
    subprocess.run(["powercfg", "/h", "off"], capture_output=True)
    print("[*] Inicio rapido de Windows desactivado para proteger el bus PCIe.")

    # 3. Eliminar cualquier tarea anterior que haya fallado
    subprocess.run(
        'schtasks /delete /tn "FixRealtek5G" /f', shell=True, capture_output=True
    )

    # 4. Crear la tarea programada que arranca con el sistema (ONSTART) con privilegios maximos (SYSTEM)
    # De esta manera, tan pronto Windows arranca (al reiniciar o encender), se ejecuta en segundo plano
    cmd_task = (
        'schtasks /create /tn "FixRealtek5G" '
        f'/tr "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File \\"{ps_file_path}\\"" '
        "/sc onstart /ru SYSTEM /rl highest /f"
    )
    res_task = subprocess.run(cmd_task, shell=True, capture_output=True, text=True)
    if res_task.returncode == 0:
        print("[+] Tarea permanente en el arranque creada exitosamente.")
    else:
        print(f"[-] Advertencia al crear tarea: {res_task.stderr.strip()}")

    # 5. Ejecutar la solucion AHORA MISMO para que quede conectado de inmediato
    print("\n[*] Aplicando configuracion en este momento...")
    res_run = subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            ps_file_path,
        ],
        capture_output=True,
        text=True,
    )

    if res_run.stdout:
        print(res_run.stdout.strip())
    if res_run.stderr:
        print(f"Detalle: {res_run.stderr.strip()}")

    print("\n[+] Proceso finalizado. El Wi-Fi deberia reconectarse ahora.")


def main():
    if not is_admin():
        print("[!] Solicitando permisos de Administrador...")
        run_as_admin()
        sys.exit(0)

    setup_permanent_fix()
    input("\nPresiona ENTER para cerrar esta ventana...")


if __name__ == "__main__":
    main()