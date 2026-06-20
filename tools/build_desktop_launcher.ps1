[CmdletBinding()]
param(
    [string]$OutputPath = (Join-Path ([Environment]::GetFolderPath("DesktopDirectory")) "Play Tower Defense.exe")
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$pythonwPath = Join-Path $repoRoot ".venv\Scripts\pythonw.exe"
$entryPoint = Join-Path $repoRoot "tower_defense.py"
$iconPngPath = Join-Path $repoRoot "assets\sprites\towers\tesla_idle.png"
$compilerPath = "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"

function Assert-PathExists {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Description
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        throw "$Description not found: $Path"
    }
}

Assert-PathExists -Path $repoRoot -Description "Repository root"
Assert-PathExists -Path $pythonwPath -Description "Python windowed executable"
Assert-PathExists -Path $entryPoint -Description "Game entry point"
Assert-PathExists -Path $iconPngPath -Description "Launcher icon source"
Assert-PathExists -Path $compilerPath -Description "C# compiler"

$outputDirectory = Split-Path -Parent $OutputPath
if ([string]::IsNullOrWhiteSpace($outputDirectory)) {
    $outputDirectory = (Get-Location).Path
}
if (-not (Test-Path -LiteralPath $outputDirectory)) {
    New-Item -ItemType Directory -Path $outputDirectory | Out-Null
}

$tempDirectory = Join-Path ([IO.Path]::GetTempPath()) ("tower-defense-launcher-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $tempDirectory | Out-Null

try {
    $sourcePath = Join-Path $tempDirectory "TowerDefenseLauncher.cs"
    $iconPath = Join-Path $tempDirectory "TowerDefenseLauncher.ico"

    Add-Type -AssemblyName System.Drawing
    $nativeMethodsSource = @"
using System;
using System.Runtime.InteropServices;

public static class NativeIconMethods
{
    [DllImport("user32.dll", SetLastError = true)]
    public static extern bool DestroyIcon(IntPtr hIcon);
}
"@
    if (-not ("NativeIconMethods" -as [type])) {
        Add-Type -TypeDefinition $nativeMethodsSource
    }

    $bitmap = New-Object System.Drawing.Bitmap($iconPngPath)
    $iconHandle = [IntPtr]::Zero
    $icon = $null
    $stream = $null
    try {
        $iconHandle = $bitmap.GetHicon()
        $icon = [System.Drawing.Icon]::FromHandle($iconHandle)
        $stream = [System.IO.File]::Create($iconPath)
        $icon.Save($stream)
    }
    finally {
        if ($null -ne $stream) {
            $stream.Dispose()
        }
        if ($null -ne $icon) {
            $icon.Dispose()
        }
        if ($iconHandle -ne [IntPtr]::Zero) {
            [NativeIconMethods]::DestroyIcon($iconHandle) | Out-Null
        }
        $bitmap.Dispose()
    }

    $launcherSource = @'
using System;
using System.Diagnostics;
using System.IO;
using System.Windows.Forms;

internal static class TowerDefenseLauncher
{
    private const string GameFolderName = "tower_defense";
    private const string RelativePythonwPath = @".venv\Scripts\pythonw.exe";
    private const string EntryPointFileName = "tower_defense.py";

    [STAThread]
    private static int Main(string[] args)
    {
        string desktopPath = Environment.GetFolderPath(Environment.SpecialFolder.DesktopDirectory);
        string repoRoot = Path.Combine(desktopPath, GameFolderName);
        string pythonwPath = Path.Combine(repoRoot, RelativePythonwPath);
        string entryPointPath = Path.Combine(repoRoot, EntryPointFileName);

        string validationError = Validate(repoRoot, pythonwPath, entryPointPath);
        bool checkOnly = args.Length == 1 && String.Equals(args[0], "--check", StringComparison.OrdinalIgnoreCase);

        if (validationError != null)
        {
            ShowError(validationError);
            return 1;
        }

        if (checkOnly)
        {
            return 0;
        }

        try
        {
            ProcessStartInfo startInfo = new ProcessStartInfo
            {
                FileName = pythonwPath,
                Arguments = QuoteArgument(entryPointPath),
                WorkingDirectory = repoRoot,
                UseShellExecute = false,
                CreateNoWindow = true
            };
            Process.Start(startInfo);
            return 0;
        }
        catch (Exception ex)
        {
            ShowError("Tower Defense could not be started.\n\n" + ex.Message);
            return 1;
        }
    }

    private static string Validate(string repoRoot, string pythonwPath, string entryPointPath)
    {
        if (!Directory.Exists(repoRoot))
        {
            return "Tower Defense folder was not found.\n\nExpected: " + repoRoot;
        }

        if (!File.Exists(pythonwPath))
        {
            return "Python runtime was not found.\n\nExpected: " + pythonwPath;
        }

        if (!File.Exists(entryPointPath))
        {
            return "Tower Defense entry point was not found.\n\nExpected: " + entryPointPath;
        }

        return null;
    }

    private static string QuoteArgument(string value)
    {
        return "\"" + value.Replace("\"", "\\\"") + "\"";
    }

    private static void ShowError(string message)
    {
        MessageBox.Show(
            message,
            "Tower Defense Launcher",
            MessageBoxButtons.OK,
            MessageBoxIcon.Error);
    }
}
'@

    Set-Content -LiteralPath $sourcePath -Value $launcherSource -Encoding ASCII

    & $compilerPath `
        /nologo `
        /target:winexe `
        /optimize+ `
        /platform:anycpu `
        /win32icon:$iconPath `
        /reference:System.Windows.Forms.dll `
        /out:$OutputPath `
        $sourcePath

    if ($LASTEXITCODE -ne 0) {
        throw "C# compiler failed with exit code $LASTEXITCODE."
    }

    Write-Host "Built launcher: $OutputPath"
}
finally {
    if (Test-Path -LiteralPath $tempDirectory) {
        Remove-Item -LiteralPath $tempDirectory -Recurse -Force
    }
}
