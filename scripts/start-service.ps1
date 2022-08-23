$servicename = $args[0]
$date = Get-Date -Format "MM/dd/yyyy HH:mm:ss"

Write-Output "$date : Starting script, service(s) $servicename* ..."
if ($servicename.length -lt 3) {
    # Just for security reasons
    # So that we don't start too many at the same time
    Write-Output "$servicename name too short"
    exit 1
}

# Run the commands
Write-Output "$date : Running Start-Service, printing Get-Service:"
# Add the * wildcard so that we can get multiple services, then pipe
Get-Service "$servicename*" | Start-Service
Get-Service "$servicename*"

Write-Output "$date : Script finished!"
exit 0