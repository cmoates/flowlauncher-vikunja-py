@echo off
REM Vendor dependencies locally for testing
REM This mimics what the release workflow does

echo Installing vendored dependencies locally...
if not exist lib mkdir lib

REM Install from requirements.txt, excluding dev/test packages
pip install ^
  requests>=2.28.0 ^
  pyflowlauncher>=0.10.0 ^
  python-dateutil>=2.8.2 ^
  --target ./lib ^
  --upgrade

REM Clean up cache
for /d /r ./lib %%D in (__pycache__) do @if exist "%%D" rmdir /s /q "%%D"
for /r ./lib %%F in (*.pyc) do @if exist "%%F" del "%%F"

echo.
echo OK: Dependencies vendored in .\lib
echo OK: Note: lib\ is ignored by git (see .gitignore)
