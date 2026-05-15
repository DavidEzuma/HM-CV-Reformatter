"""FastAPI web app for HM CV reformatter — batch capable."""

import io
import os
import uuid
import zipfile
import concurrent.futures
from pathlib import Path
from typing import List

from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse

import config
from extract import extract_cv_data
from populate import populate_template

app = FastAPI(title="HM CV Reformatter")

BASE = Path(os.environ.get("APPDATA", ".")) / "HMCVReformatter"
UPLOAD_DIR = BASE / "uploads"
OUTPUT_DIR = BASE / "outputs"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f0f4ff;
     display:flex;justify-content:center;align-items:flex-start;min-height:100vh;padding:2rem}
.card{background:white;border-radius:14px;padding:2.5rem;box-shadow:0 4px 32px rgba(0,48,135,.1);
      max-width:600px;width:100%;margin-top:2rem}
.top{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:.3rem}
h1{font-size:1.4rem;color:#003087}
.nav a{font-size:.82rem;color:#003087;text-decoration:none;opacity:.7}
.nav a:hover{opacity:1}
.sub{color:#666;font-size:.88rem;margin-bottom:1.8rem}
.drop{border:2px dashed #003087;border-radius:10px;padding:2.2rem;text-align:center;
      cursor:pointer;color:#555;transition:background .2s}
.drop:hover,.drop.over{background:#f0f4ff}
.drop input{display:none}
.drop .icon{font-size:2.4rem;margin-bottom:.4rem}
.drop .hint{font-size:.8rem;color:#999;margin-top:.3rem}
#flist{margin-top:1rem;font-size:.85rem;color:#003087;min-height:1rem}
#flist div{padding:2px 0}
button{margin-top:1.4rem;width:100%;padding:.85rem;background:#003087;color:white;
       border:none;border-radius:8px;font-size:1rem;font-weight:600;cursor:pointer;transition:background .2s}
button:hover{background:#00419e}
button:disabled{background:#aaa;cursor:not-allowed}
#status{margin-top:1rem;text-align:center;font-size:.9rem;color:#555;min-height:1.4rem}
#status.err{color:#c0392b}
#status.ok{color:#27ae60}
.spin{display:inline-block;width:14px;height:14px;border:2px solid #ddd;
      border-top-color:#003087;border-radius:50%;animation:sp .8s linear infinite;vertical-align:middle;margin-right:5px}
@keyframes sp{to{transform:rotate(360deg)}}
label.field{display:block;font-size:.85rem;color:#444;margin-bottom:.4rem;font-weight:500}
input.text{width:100%;padding:.6rem .8rem;border:1px solid #ccc;border-radius:6px;font-size:.9rem;
           font-family:monospace;margin-bottom:1rem}
input.text:focus{outline:none;border-color:#003087}
.msg{margin-top:.8rem;font-size:.88rem;text-align:center}
.msg.ok{color:#27ae60}.msg.err{color:#c0392b}
"""

HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Houston Methodist CV Reformatter</title>
<style>{_CSS}</style>
</head>
<body>
<div class="card">
  <div class="top">
    <h1>HM CV Reformatter</h1>
    <span class="nav"><a href="/settings">⚙ Settings</a></span>
  </div>
  <p class="sub">Upload one or more resumes — download them formatted to Houston Methodist's WCM CV template.</p>
  <div class="drop" id="drop">
    <div class="icon">📄</div>
    <label for="files">Click to select files or drag &amp; drop</label>
    <input type="file" id="files" multiple accept=".docx,.pdf,.txt"/>
    <div class="hint">Supports .docx · .pdf · .txt &nbsp;|&nbsp; Multiple files OK</div>
  </div>
  <div id="flist"></div>
  <button id="btn" onclick="convert()" disabled>Convert to HM Format</button>
  <div id="status"></div>
</div>
<script>
const inp=document.getElementById('files'),btn=document.getElementById('btn'),
      st=document.getElementById('status'),fl=document.getElementById('flist'),
      drop=document.getElementById('drop');

function showFiles(files){
  fl.innerHTML=[...files].map(f=>`<div>✓ ${f.name}</div>`).join('');
  btn.disabled=false; st.textContent='';
}
inp.addEventListener('change',()=>inp.files.length&&showFiles(inp.files));
drop.addEventListener('dragover',e=>{e.preventDefault();drop.classList.add('over')});
drop.addEventListener('dragleave',()=>drop.classList.remove('over'));
drop.addEventListener('drop',e=>{
  e.preventDefault();drop.classList.remove('over');
  if(e.dataTransfer.files.length){inp.files=e.dataTransfer.files;showFiles(inp.files)}
});

async function convert(){
  if(!inp.files.length)return;
  btn.disabled=true; st.className='';
  st.innerHTML='<span class="spin"></span>Processing '+inp.files.length+' file(s) — please wait…';
  const form=new FormData();
  [...inp.files].forEach(f=>form.append('files',f));
  try{
    const res=await fetch('/convert',{method:'POST',body:form});
    if(!res.ok){const e=await res.json();throw new Error(e.detail||'Conversion failed')}
    const blob=await res.blob();
    const url=URL.createObjectURL(blob);
    const a=document.createElement('a');
    a.href=url;
    const cd=res.headers.get('content-disposition')||'';
    a.download=cd.match(/filename="([^"]+)"/)?.[1]||'HM_CVs.zip';
    a.click();
    st.className='ok'; st.textContent='✓ Download ready!';
  }catch(e){st.className='err';st.textContent='✗ '+e.message;}
  finally{btn.disabled=false}
}
</script>
</body>
</html>"""


def _settings_html(msg: str = "", ok: bool = True) -> str:
    key = config.get_api_key()
    masked = (key[:6] + "..." + key[-4:]) if len(key) > 10 else ("(not set)" if not key else key)
    msg_html = f'<p class="msg {"ok" if ok else "err"}">{msg}</p>' if msg else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Settings — HM CV Reformatter</title>
<style>{_CSS}</style>
</head>
<body>
<div class="card">
  <div class="top">
    <h1>Settings</h1>
    <span class="nav"><a href="/">← Back</a></span>
  </div>
  <p class="sub">Configure your DeepSeek API key. Get one at <a href="https://platform.deepseek.com" target="_blank">platform.deepseek.com</a>.</p>
  <form method="POST" action="/settings">
    <label class="field">Current key: <code>{masked}</code></label>
    <label class="field">New API key</label>
    <input class="text" type="password" name="api_key" placeholder="sk-..." autocomplete="off" />
    <button type="submit">Save Key</button>
  </form>
  {msg_html}
</div>
</body>
</html>"""


def _process_one(file_bytes: bytes, filename: str) -> tuple[str, bytes]:
    """Extract + populate for a single resume. Returns (output_filename, docx_bytes)."""
    suffix = Path(filename).suffix.lower()
    uid = uuid.uuid4().hex
    upload_path = UPLOAD_DIR / f"{uid}{suffix}"
    output_path = OUTPUT_DIR / f"{uid}_HM_CV.docx"
    try:
        upload_path.write_bytes(file_bytes)
        cv_data = extract_cv_data(str(upload_path))
        populate_template(cv_data, str(output_path))
        result_bytes = output_path.read_bytes()
        stem = Path(filename).stem
        return f"HM_CV_{stem}.docx", result_bytes
    finally:
        upload_path.unlink(missing_ok=True)
        output_path.unlink(missing_ok=True)


@app.get("/", response_class=HTMLResponse)
def index():
    return HTML


@app.get("/settings", response_class=HTMLResponse)
def settings_get():
    return _settings_html()


@app.post("/settings", response_class=HTMLResponse)
def settings_post(api_key: str = Form(...)):
    key = api_key.strip()
    if not key.startswith("sk-") or len(key) < 10:
        return _settings_html("Invalid key format — must start with sk-", ok=False)
    config.set_api_key(key)
    return _settings_html("API key saved.", ok=True)


@app.post("/convert")
async def convert(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(400, "No files uploaded.")

    for f in files:
        if Path(f.filename).suffix.lower() not in (".docx", ".pdf", ".txt"):
            raise HTTPException(400, f"Unsupported file type: {f.filename}")

    # Read all bytes upfront (async), then process in thread pool
    file_data = [(await f.read(), f.filename) for f in files]

    results: list[tuple[str, bytes]] = []
    errors: list[str] = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(_process_one, data, name): name for data, name in file_data}
        for future in concurrent.futures.as_completed(futures):
            name = futures[future]
            try:
                results.append(future.result())
            except Exception as e:
                errors.append(f"{name}: {e}")

    if errors and not results:
        raise HTTPException(500, "All conversions failed:\n" + "\n".join(errors))

    # Single file → direct download; multiple → zip
    if len(results) == 1 and not errors:
        out_name, out_bytes = results[0]
        return StreamingResponse(
            io.BytesIO(out_bytes),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f'attachment; filename="{out_name}"'},
        )

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for out_name, out_bytes in results:
            zf.writestr(out_name, out_bytes)
        if errors:
            zf.writestr("ERRORS.txt", "\n".join(errors))
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": 'attachment; filename="HM_CVs.zip"'},
    )
