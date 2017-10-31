# Register the HNetCfg library (once)
regsvr32 hnetcfg.dll

$MainAdapter = Get-NetAdapter | Where-Object {$_.MediaConnectionState -eq 'Connected' -and $_.PhysicalMediaType -ne 'Unspecified'} | Sort-Object LinkSpeed -Descending

function EnableICS([string]$ID)
{
    # Create a NetSharingManager object
    $m = New-Object -ComObject HNetCfg.HNetShare

    # List connections
    $m.EnumEveryConnection |% { $m.NetConnectionProps.Invoke($_).Guid }

    # Find connection
    $c = $m.EnumEveryConnection |? { $m.NetConnectionProps.Invoke($_).Guid -eq $ID }

    # Get sharing configuration
    $config = $m.INetSharingConfigurationForINetConnection.Invoke($c)

    # See if sharing is enabled
    Write-Output $config.SharingEnabled

    # See the role of connection in sharing
    # 0 - public, 1 - private
    # Only meaningful if SharingEnabled is True
    Write-Output $config.SharingType

    # Enable sharing (0 - public, 1 - private)
    $config.EnableSharing(0)

    # Disable sharing
    #$config.DisableSharing()
}

EnableICS($MainAdapter.InterfaceGuid)