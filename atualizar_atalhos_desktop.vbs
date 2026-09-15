Set oWS = WScript.CreateObject("WScript.Shell")

sLinkFile1 = "C:\Users\Henrique\OneDrive\Desktop\Painel de Estudos - Concursos (IA).lnk"
sLinkFile2 = "C:\Users\Henrique\Desktop\Painel de Estudos - Concursos (IA).lnk"

Sub CreateShortcut(sPath)
    On Error Resume Next
    Set oLink = oWS.CreateShortcut(sPath)
    oLink.TargetPath = "C:\PROJETOS IA\Concursos\iniciar_app_desktop.bat"
    oLink.WorkingDirectory = "C:\PROJETOS IA\Concursos"
    oLink.Description = "Central de Concursos Publicos com IA - Metodo 4 Pilares"
    oLink.IconLocation = "C:\Windows\System32\shell32.dll,43"
    oLink.WindowStyle = 1
    oLink.Save
End Sub

CreateShortcut(sLinkFile1)
CreateShortcut(sLinkFile2)
