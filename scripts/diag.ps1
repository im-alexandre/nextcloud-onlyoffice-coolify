Write-Host "=== TCP 5432 ==="
Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object { $PSItem.LocalPort -eq 5432 } | ForEach-Object {
    $proc = Get-Process -Id $PSItem.OwningProcess -ErrorAction SilentlyContinue
    "{0}:{1} pid={2} proc={3}" -f $PSItem.LocalAddress, $PSItem.LocalPort, $PSItem.OwningProcess, $proc.Name
}
Write-Host "=== netstat 5432 ==="
netstat -ano -p tcp | Select-String ":5432"
Write-Host "=== docker volumes ==="
docker volume ls --format "{{.Name}}" | Select-String "coolify"
