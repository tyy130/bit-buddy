; Inno Setup Script for Bit Buddy Windows Installer
; Requires Inno Setup 6.0 or later: https://jrsoftware.org/isinfo.php

#define MyAppName "Bit Buddy"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Bit Buddy Team"
#define MyAppURL "https://github.com/tyy130/bit-buddy"
#define MyAppExeName "BitBuddy.exe"

[Setup]
; Basic app info
AppId={{A1B2C3D4-E5F6-4A5B-8C9D-0E1F2A3B4C5D}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Installation paths
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes

; Output settings
OutputDir=dist\installer
OutputBaseFilename=BitBuddySetup-{#MyAppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern

; Minimum Windows version
MinVersion=10.0

; Privileges
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; Icons and graphics
SetupIconFile=assets\buddy_icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

; License and info
LicenseFile=LICENSE.txt
InfoBeforeFile=README.md

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Main executable
Source: "dist\BitBuddy.exe"; DestDir: "{app}"; Flags: ignoreversion

; Documentation
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "END_USER_GUIDE.md"; DestDir: "{app}"; Flags: ignoreversion

; Config templates (will be copied to user dir on first run)
Source: "app\config.yaml"; DestDir: "{app}\templates"; Flags: ignoreversion
Source: "custodian\*.yaml"; DestDir: "{app}\templates\custodian"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
var
  DrivePage: TInputDirWizardPage;
  ModelSelectionPage: TInputOptionWizardPage;
  
procedure InitializeWizard;
begin
  // Drive selection page
  DrivePage := CreateInputDirPage(
    wpSelectDir,
    'Select Installation Drive',
    'Choose the drive where Bit Buddy will store its data',
    'Select the drive with enough free space (minimum 2GB recommended):',
    False,
    'New Folder'
  );
  DrivePage.Add('Installation Drive:');
  DrivePage.Values[0] := ExpandConstant('{autopf}\{#MyAppName}');
  
  // Model selection page
  ModelSelectionPage := CreateInputOptionPage(
    DrivePage.ID,
    'Select AI Model',
    'Choose the AI model for your Bit Buddy',
    'Larger models are smarter but require more resources:',
    True,
    False
  );
  ModelSelectionPage.Add('TinyLlama 1.1B (0.7GB) - Fastest, basic capabilities');
  ModelSelectionPage.Add('Qwen2.5 1.5B (0.9GB) - Recommended, balanced performance');
  ModelSelectionPage.Add('Phi-3.5 Mini (2.3GB) - Most capable, slower');
  ModelSelectionPage.SelectedValueIndex := 1; // Default to Qwen
end;

function GetDrivePath(Param: String): String;
begin
  Result := DrivePage.Values[0];
end;

function GetModelSelection(Param: String): String;
begin
  case ModelSelectionPage.SelectedValueIndex of
    0: Result := 'tinyllama-1.1b';
    1: Result := 'qwen2.5-1.5b';
    2: Result := 'phi3.5-mini';
  else
    Result := 'qwen2.5-1.5b';
  end;
end;

function GetSpaceInfo: String;
var
  TotalSpace, FreeSpace: Integer;
  DriveLetter: String;
begin
  DriveLetter := Copy(DrivePage.Values[0], 1, 2);
  if GetSpaceOnDisk64(DriveLetter, FreeSpace, TotalSpace) then
    Result := Format('Free space: %.1f GB', [FreeSpace / 1024.0 / 1024.0 / 1024.0])
  else
    Result := 'Unable to check space';
end;
