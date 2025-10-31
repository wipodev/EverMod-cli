; ==========================================================
; EverMod CLI — Windows Installer (Inno Setup 6)
; ==========================================================
; Creates a clean CLI installation with PATH registration.
; ==========================================================

[Setup]
AppName=EverMod CLI
AppId={{E1A0ADEF-01D4-4A2F-8B77-5C7A77B8D5E4}}
AppVersion=1.0.0
AppPublisher=WipoDev
AppPublisherURL=https://github.com/wipodev/evermod-cli
AppSupportURL=https://github.com/wipodev/evermod-cli/issues
AppUpdatesURL=https://github.com/wipodev/evermod-templates
DefaultDirName={autopf}\EverMod CLI
OutputBaseFilename=EverMod-Setup
SetupIconFile=assets\installer.ico
UninstallDisplayIcon={app}evermod.exe
Compression=lzma
SolidCompression=yes
WizardStyle=modern
LicenseFile=LICENSE
PrivilegesRequired=lowest
DisableProgramGroupPage=yes
DisableDirPage=no
DisableReadyMemo=no
ArchitecturesInstallIn64BitMode=x64compatible

[Files]
Source: "dist\evermod.exe"; DestDir: "{app}"; Flags: ignoreversion

[Registry]
; ✅ Add EverMod CLI to user PATH (HKCU → no requiere admin)
Root: HKCU; Subkey: "Environment"; ValueType: expandsz; ValueName: "Path"; \
    ValueData: "{olddata};{app}"; Flags: preservestringtype

[Run]
; ✅ Update PATH immediately (optional)
Filename: "powershell.exe"; \
    Parameters: "-Command ""[Environment]::SetEnvironmentVariable('Path', ($env:Path + ';{app}'), 'User')"""; \
    Flags: runhidden

; ✅ Install templates only if ~/.evermod does not exist
Filename: "{app}\evermod.exe"; \
    Parameters: "update --force --silent"; \
    Flags: runhidden; \
    Check: not EvermodTemplatesExist

[Code]
function EvermodTemplatesExist(): Boolean;
var
  TemplatesPath: String;
begin
  TemplatesPath := ExpandConstant('{%USERPROFILE}\.evermod');
  Result := DirExists(TemplatesPath);
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  PathValue, AppDir, TemplatesPath: String;
begin
  if CurUninstallStep = usUninstall then
  begin
    { ✅ 1. Clean PATH }
    AppDir := ExpandConstant('{app}');
    RegQueryStringValue(HKEY_CURRENT_USER, 'Environment', 'Path', PathValue);
    if Pos(AppDir, PathValue) > 0 then
    begin
      StringChangeEx(PathValue, ';' + AppDir, '', True);
      StringChangeEx(PathValue, AppDir, '', True);
      RegWriteStringValue(HKEY_CURRENT_USER, 'Environment', 'Path', PathValue);
    end;

    { ✅ 2. Remove .evermod folder from user directory }
    TemplatesPath := ExpandConstant('{%USERPROFILE}\.evermod');
    if DirExists(TemplatesPath) then
    begin
      DelTree(TemplatesPath, True, True, True);
    end;
  end;
end;