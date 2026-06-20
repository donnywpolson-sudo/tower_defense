Set shell = CreateObject("WScript.Shell")
Set files = CreateObject("Scripting.FileSystemObject")

folder = files.GetParentFolderName(WScript.ScriptFullName)
pythonw = folder & "\.venv\Scripts\pythonw.exe"
python = folder & "\.venv\Scripts\python.exe"
game = folder & "\tower_defense.py"

If Not files.FileExists(game) Then
    MsgBox "Could not find tower_defense.py in:" & vbCrLf & folder, vbExclamation, "Tower Defense"
    WScript.Quit 1
End If

If files.FileExists(pythonw) Then
    command = """" & pythonw & """ """ & game & """"
ElseIf files.FileExists(python) Then
    command = """" & python & """ """ & game & """"
Else
    MsgBox "Could not find .venv\Scripts\pythonw.exe or python.exe.", vbExclamation, "Tower Defense"
    WScript.Quit 1
End If

shell.CurrentDirectory = folder
shell.Run command, 0, False
