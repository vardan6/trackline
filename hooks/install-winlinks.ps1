# Internal creation backend; the caller owns preflight, JSON, and recovery.
param([Parameter(Mandatory=$true)][string]$Path,
      [Parameter(Mandatory=$true)][string]$Target, [switch]$Directory)
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class TracklineNativeLinks {
    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, ExactSpelling = true, SetLastError = true)]
    [return: MarshalAs(UnmanagedType.U1)]
    public static extern bool CreateSymbolicLinkW(string path, string target, uint flags);
}
'@
[uint32]$flags = 2
if ($Directory) { $flags = $flags -bor 1 }
if (-not [TracklineNativeLinks]::CreateSymbolicLinkW($Path, $Target, $flags)) {
    throw [ComponentModel.Win32Exception]::new([Runtime.InteropServices.Marshal]::GetLastWin32Error())
}
if (-not (Test-Path -LiteralPath $Path)) {
    throw "Windows cannot follow the created link: $Path"
}
