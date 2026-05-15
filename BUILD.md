# Build Instructions

## Prerequisites
```
pip install pyinstaller pystray pillow
```

## Step 1 — Build the .exe
```
pyinstaller build.spec
```
Output: `dist/HMCVReformatter.exe`

## Step 2a — Build .exe installer (Inno Setup)
1. Download and install [Inno Setup](https://jrsoftware.org/isdl.php)
2. Run:
```
iscc installer.iss
```
Output: `dist/installer/HMCVReformatter_Setup.exe`

## Step 2b — Build .msi installer (WiX v4) ← preferred
1. Install WiX v4: `dotnet tool install --global wix`
2. Run:
```
wix build installer.wxs -o dist\HMCVReformatter.msi
```
Output: `dist/HMCVReformatter.msi`

## Step 3 — Distribute
Send `HMCVReformatter_Setup.exe` to HR staff.

## What HR staff does
1. Double-click `HMCVReformatter_Setup.exe`
2. Click through installer (no admin password needed)
3. App launches automatically after install
4. A browser window opens with the CV reformatter
5. System tray icon (bottom-right) — right-click → Quit to close

## Updating
Build new `HMCVReformatter_Setup.exe` and send to HR staff.
Running it overwrites the old version automatically.

## Environment variable required
The app reads the DeepSeek API key from `DEEPSEEK_API_KEY`.
Set this in the system environment before building, or hardcode in `extract.py`.
