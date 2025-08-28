!define APPNAME "Antonio Rabelo"
!define EXENAME "AntonioRabelo.exe"

OutFile "LuaJoalheriaSetup.exe"
InstallDir "$PROGRAMFILES\AntonioRabelo"

RequestExecutionLevel admin
SetCompress auto
SetCompressor /SOLID lzma

Page directory
Page instfiles

Section "Install"
  SetOutPath "$INSTDIR"

  ; Binário PyInstaller (onedir)
  File /r "dist\AntonioRabelo\*"

  ; Atalhos
  CreateShortCut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\${EXENAME}" "" "$INSTDIR\${EXENAME}" 0
  CreateDirectory "$SMPROGRAMS\${APPNAME}"
  CreateShortCut "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk" "$INSTDIR\${EXENAME}" "" "$INSTDIR\${EXENAME}" 0
SectionEnd

Section "Uninstall"
  Delete "$DESKTOP\${APPNAME}.lnk"
  Delete "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk"
  RMDir "$SMPROGRAMS\${APPNAME}"
  RMDir /r "$INSTDIR"
SectionEnd


