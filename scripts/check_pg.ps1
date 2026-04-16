Get-Service | Where-Object { $PSItem.Name -like "*postgres*" } | Select-Object Name,Status,DisplayName
