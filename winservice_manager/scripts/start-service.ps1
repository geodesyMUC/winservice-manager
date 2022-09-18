$servicenames = $args
$date = Get-Date -Format "MM/dd/yyyy HH:mm:ss"

Write-Output "$date : Starting script, service(s) $servicenames ..."

# Run the commands
Write-Output "$date : Running Start-Service, then printing Get-Service ..."
# Add the * wildcard so that we can get multiple services, then pipe
Get-Service $servicenames | Start-Service
Get-Service $servicenames

Write-Output "$date : Script finished!"
exit 0
