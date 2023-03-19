$vm = "NAME OF VM"
$systemPath = "C:\Windows\System32\"
$driverPath = "C:\Windows\System32\DriverStore\FileRepository\"

# check if script is admin
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if( $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator) ) {
    
    # do we need guest vm privs? enable it
    Get-VM -Name $vm | Get-VMIntegrationService | ? {-not($_.Enabled)} | Enable-VMIntegrationService -Verbose
    
    # aggregate and copy files to driverstore
    $localDriverFolder = ""
    Get-ChildItem $driverPath -recurse | Where-Object {$_.PSIsContainer -eq $true -and $_.Name -match "nv_dispi.inf_amd64_*"} | Sort-Object -Descending -Property LastWriteTime | select -First 1 |
    ForEach-Object {
        if ($localDriverFolder -eq "") {
            $localDriverFolder = $_.Name                                  
            }
    }

    Write-Host $localDriverFolder

    Get-ChildItem $driverPath$localDriverFolder -recurse | Where-Object {$_.PSIsContainer -eq $false} |
    Foreach-Object {
        $sourcePath = $_.FullName
        $destinationPath = $sourcePath -replace "^C\:\\Windows\\System32\\DriverStore\\","C:\Temp\System32\HostDriverStore\"
        Copy-VMFile $vm -SourcePath $sourcePath -DestinationPath $destinationPath -Force -CreateFullPath -FileSource Host
    }

    # get all files related to NV*.* in system32
    Get-ChildItem $systemPath  | Where-Object {$_.Name -like "NV*"} |
    ForEach-Object {
        $sourcePath = $_.FullName
        $destinationPath = $sourcePath -replace "^C\:\\Windows\\System32\\","C:\Temp\System32\"
        Copy-VMFile $vm -SourcePath $sourcePath -DestinationPath $destinationPath -Force -CreateFullPath -FileSource Host
    }

    Write-Host "Success! Please go to C:\Temp and copy the files where they are expected within the VM."

} else {
    Write-Host "This PowerShell Script must be run with Administrative Privileges or nothing will work."
}
