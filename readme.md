## Setup
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install requests pandas
```

## Usage
- Using Powershell, run `bootstrap.ps1`.
- Alternatively, run `runner.py` directly.

## Automation (Windows)
1. Task Scheduler
2. Trigger: At log on
3. Actions: Start a program `powershell.exe -ExecutionPolicy Bypass -File "X:\path\bootstrap.ps1"`
