!include MUI2.nsh
!include FileFunc.nsh
!define MUI_ICON "..\${app_name}\Icon.ico"
!define MUI_UNICON "..\${app_name}\Icon.ico"

!getdllversion "..\${app_name}\${app_name}.exe" ver
!define VERSION "${ver1}.${ver2}.${ver3}.${ver4}"

VIProductVersion "${VERSION}"
VIAddVersionKey "ProductName" "${app_name}"
VIAddVersionKey "FileVersion" "${VERSION}"
VIAddVersionKey "ProductVersion" "${VERSION}"
VIAddVersionKey "LegalCopyright" "(C) ${author}"
VIAddVersionKey "FileDescription" "${app_name}"

;--------------------------------
;Perform Machine-level install, if possible

!define MULTIUSER_EXECUTIONLEVEL Highest
;Add support for command-line args that let uninstaller know whether to
;uninstall machine- or user installation:
!define MULTIUSER_INSTALLMODE_COMMANDLINE
!include MultiUser.nsh
!include LogicLib.nsh

Function .onInit
  !insertmacro MULTIUSER_INIT
  ;Do not use InstallDir at all so we can detect empty $InstDir!
  ${If} $InstDir == "" ; /D not used
      ${If} $MultiUser.InstallMode == "AllUsers"
          StrCpy $InstDir "$PROGRAMFILES\${app_name}"
      ${Else}
          StrCpy $InstDir "$LOCALAPPDATA\${app_name}"
      ${EndIf}
  ${EndIf}
FunctionEnd

Function un.onInit
  !insertmacro MULTIUSER_UNINIT
FunctionEnd

;--------------------------------
;General

  Name "${app_name}"
  OutFile "..\${installer}"

;--------------------------------
;Interface Settings

  !define MUI_ABORTWARNING

;--------------------------------
;Pages

  !define MUI_WELCOMEPAGE_TEXT "This wizard will guide you through the installation of ${app_name}.$\r$\n$\r$\n$\r$\nClick Next to continue."
  !insertmacro MUI_PAGE_WELCOME
  !insertmacro MUI_PAGE_DIRECTORY
  !insertmacro MUI_PAGE_INSTFILES
    !define MUI_FINISHPAGE_NOAUTOCLOSE
    !define MUI_FINISHPAGE_RUN
    !define MUI_FINISHPAGE_RUN_CHECKED
    !define MUI_FINISHPAGE_RUN_TEXT "Run ${app_name}"
    !define MUI_FINISHPAGE_RUN_FUNCTION "LaunchAsNonAdmin"
  !insertmacro MUI_PAGE_FINISH

  !insertmacro MUI_UNPAGE_CONFIRM
  !insertmacro MUI_UNPAGE_INSTFILES

;--------------------------------
;Languages

  !insertmacro MUI_LANGUAGE "English"

;--------------------------------
;Installer Sections

!define UNINST_KEY \
  "Software\Microsoft\Windows\CurrentVersion\Uninstall\${app_name}"
Section
  SetOutPath "$InstDir"
  File /r "..\${app_name}\*"
  WriteRegStr SHCTX "Software\${app_name}" "" $InstDir
  WriteUninstaller "$InstDir\uninstall.exe"
  CreateShortCut "$SMPROGRAMS\${app_name}.lnk" "$InstDir\${app_name}.exe"
  WriteRegStr SHCTX "${UNINST_KEY}" "DisplayName" "${app_name}"
  WriteRegStr SHCTX "${UNINST_KEY}" "UninstallString" \
    "$\"$InstDir\uninstall.exe$\" /$MultiUser.InstallMode"
  WriteRegStr SHCTX "${UNINST_KEY}" "QuietUninstallString" \
    "$\"$InstDir\uninstall.exe$\" /$MultiUser.InstallMode /S"
  WriteRegStr SHCTX "${UNINST_KEY}" "Publisher" "${author}"
  WriteRegStr SHCTX "${UNINST_KEY}" "DisplayIcon" "$InstDir\uninstall.exe"
  ${GetSize} "$InstDir" "/S=0K" $0 $1 $2
  IntFmt $0 "0x%08X" $0
  WriteRegDWORD SHCTX "${UNINST_KEY}" "EstimatedSize" "$0"

SectionEnd

;--------------------------------
;Uninstaller Section

Section "Uninstall"

  RMDir /r "$InstDir"
  Delete "$SMPROGRAMS\${app_name}.lnk"
  DeleteRegKey /ifempty SHCTX "Software\${app_name}"
  DeleteRegKey SHCTX "${UNINST_KEY}"

SectionEnd

Function LaunchAsNonAdmin
  Exec '"$WINDIR\explorer.exe" "$InstDir\${app_name}.exe"'
FunctionEnd