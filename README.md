# HM CV Reformatter

Converts any resume (`.docx`, `.pdf`, `.txt`) into Houston Methodist's WCM CV template format. Runs as a local desktop app — no data leaves the user's machine except for the DeepSeek API call used to extract structured information from the resume.

---

## How It Works

1. User drops one or more resume files into the browser UI
2. DeepSeek AI extracts all candidate data into a validated schema
3. Data is injected deterministically into the HM WCM CV template
4. Formatted `.docx` files are downloaded — single file direct, multiple files as a `.zip`

---

## For HR Staff (End Users)

### Installation
1. Double-click `HMCVReformatter.msi`
2. Click through the installer (no admin password needed)
3. The app opens automatically in your browser

### First-Time Setup
1. Click **⚙ Settings** in the top-right corner
2. Paste your DeepSeek API key (starts with `sk-`)
3. Click **Save Key**

> Get a free API key at [platform.deepseek.com](https://platform.deepseek.com)

### Using the App
1. Drag and drop resumes onto the upload area, or click to browse
2. Click **Convert to HM Format**
3. Your formatted CV(s) download automatically

### System Tray
The app runs silently in the background. Right-click the tray icon (bottom-right of taskbar) to:
- **Open App** — reopen the browser window
- **Quit** — shut down completely

### Updating
Receive a new `HMCVReformatter.msi` from your administrator and run it — it overwrites the previous version automatically.

---

## For Developers

### Project Structure

```
├── src/
│   ├── app.py          # FastAPI web server + HTML UI
│   ├── config.py       # Persistent settings (API key storage)
│   ├── extract.py      # DeepSeek API extraction pipeline
│   ├── launcher.py     # Desktop launcher (uvicorn + system tray)
│   ├── populate.py     # Template injection (python-docx)
│   └── schema.py       # Pydantic HMCVData model (19 CV sections)
├── assets/
│   └── HM WCM CV (sample Assistant Professor).docx  # HM template
├── dist/               # Build output (gitignored)
├── build.spec          # PyInstaller configuration
├── installer.wxs       # WiX v4 MSI installer definition
├── requirements.txt    # Python dependencies
└── BUILD.md            # Build instructions
```

### Prerequisites

```bash
pip install -r requirements.txt
pip install pyinstaller pystray pillow
dotnet tool install --global wix --version 4.0.5
```

### Running in Development

```bash
cd src
uvicorn app:app --reload --port 8000
```

Then open [http://localhost:8000](http://localhost:8000).

Set your API key in Settings, or via environment variable:

```bash
set DEEPSEEK_API_KEY=sk-...
```

### Building the Installer

```bash
# 1. Bundle Python app into single .exe
python -m PyInstaller build.spec

# 2. Build .msi installer
wix build installer.wxs -o dist\HMCVReformatter.msi
```

Output: `dist\HMCVReformatter.msi` — ready to distribute.

See [`BUILD.md`](BUILD.md) for full build instructions.

### Architecture Notes

- **Extraction**: DeepSeek `deepseek-chat` with `response_format: json_object` and `temperature: 0.1` for deterministic output. Schema-validated via Pydantic v2.
- **Template fidelity**: All output clones the HM `.docx` template via `python-docx`. Missing fields fill as `N/A`. Format is always 100% correct regardless of source resume quality.
- **Batch processing**: Up to 4 resumes processed in parallel via `ThreadPoolExecutor`.
- **Config persistence**: API key stored in `%APPDATA%\HMCVReformatter\config.json`.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Web server | FastAPI + uvicorn |
| AI extraction | DeepSeek API (OpenAI-compatible) |
| Data validation | Pydantic v2 |
| Template output | python-docx |
| Desktop packaging | PyInstaller |
| Installer | WiX Toolset v4 |
| System tray | pystray + Pillow |
