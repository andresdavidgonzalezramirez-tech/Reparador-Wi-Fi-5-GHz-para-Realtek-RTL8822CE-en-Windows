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


def deploy_wifi_fix():
    print("=" * 70)
    print(" REPARADOR Y BLINDAJE WI-FI 5 GHz REALTEK RTL8822CE")
    print("=" * 70)

    # El bloque PowerShell definitivo y probado
    ps_deployment_script = r'''
# 1. Habilitar ejecucion de scripts en el sistema
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope LocalMachine -Force

# 2. Desactivar inicio rapido (Fast Startup) para asegurar un apagado completo
powercfg /h off
Write-Host "[+] Inicio rapido desactivado." -ForegroundColor Green

# 3. Crear directorio y guardar el script base corregido
$fixDir = "C:\ProgramData\FixWifi"
if (-not (Test-Path $fixDir)) { New-Item -ItemType Directory -Path $fixDir -Force | Out-Null }

$psCode = @'
Start-Sleep -Seconds 5
$path = "HKLM:\SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}"
$target = Get-ChildItem -Path $path -ErrorAction SilentlyContinue | Where-Object { (Get-ItemProperty $_.PsPath).DriverDesc -match "8822CE" } | Select-Object -First 1

if ($target) {
    Set-ItemProperty -Path $target.PsPath -Name "bSupport80211d" -Value "1" -Type String
    Set-ItemProperty -Path $target.PsPath -Name "CountryRegion5G" -Value "7" -Type String
}

Get-NetAdapter | Where-Object { $_.InterfaceDescription -match "8822CE" } | Restart-NetAdapter
'@

Set-Content -Path "$fixDir\fix.ps1" -Value $psCode -Encoding UTF8
Write-Host "[+] Script guardado en $fixDir\fix.ps1" -ForegroundColor Green

# 4. Limpiar tareas anteriores y crear las tareas de persistencia dual
schtasks /delete /tn "FixRealtek5G_Boot" /f 2>$null
schtasks /delete /tn "FixRealtek5G_Logon" /f 2>$null
schtasks /delete /tn "FixRealtek5G" /f 2>$null

schtasks /create /tn "FixRealtek5G_Boot" /tr "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File C:\ProgramData\FixWifi\fix.ps1" /sc onstart /delay 0000:10 /ru SYSTEM /rl highest /f
schtasks /create /tn "FixRealtek5G_Logon" /tr "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File C:\ProgramData\FixWifi\fix.ps1" /sc onlogon /delay 0000:05 /rl highest /f

Write-Host "[+] Tareas programadas de arranque y sesion creadas exitosamente." -ForegroundColor Green

# 5. Ejecutar la solucion en vivo ahora mismo
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$fixDir\fix.ps1"

Write-Host "[+] Proceso completado: adaptador configurado y blindaje permanente activo." -ForegroundColor Green
'''

    # Ejecutar en vivo mostrando toda la salida en consola sin crear archivos .txt
    proc = subprocess.Popen(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_deployment_script],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    for line in proc.stdout:
        print(line, end="")

    proc.wait()
    print("\n" + "=" * 70)
    print(" Finalizado con exito. El equipo esta blindado contra reinicio y apagado.")
    print("=" * 70)


def main():
    if not is_admin():
        print("[*] Solicitando privilegios de Administrador...")
        run_as_admin()
        sys.exit(0)

    deploy_wifi_fix()
    input("\nPresiona ENTER para salir...")


if __name__ == "__main__":
    main()
