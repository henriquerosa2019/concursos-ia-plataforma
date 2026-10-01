$WshShell = New-Object -comObject WScript.Shell
$desktop1 = [Environment]::GetFolderPath('Desktop')
$desktop2 = "C:\Users\Henrique\OneDrive\Desktop"
$bat_path = "c:\PROJETOS IA\Concursos\testar_mapa_pdf.bat"
$work_dir = "c:\PROJETOS IA\Concursos"

foreach ($d in @($desktop1, $desktop2)) {
    if (Test-Path $d) {
        $Shortcut = $WshShell.CreateShortcut("$d\Testador de Mapa Mental (PDF).lnk")
        $Shortcut.TargetPath = $bat_path
        $Shortcut.WorkingDirectory = $work_dir
        $Shortcut.Description = "Testador Isolado de Mapas Mentais a partir de qualquer PDF"
        $Shortcut.Save()
        Write-Host "Atalho criado em: $d"
    }
}
