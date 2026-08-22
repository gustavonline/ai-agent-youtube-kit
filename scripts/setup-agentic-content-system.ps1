$ErrorActionPreference = "Stop"

$pythonCommand = Get-Command py -ErrorAction SilentlyContinue
if ($null -eq $pythonCommand) {
  $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
}
if ($null -eq $pythonCommand) {
  throw "Python 3 is required. Install Python 3.10 or newer."
}

& $pythonCommand.Source -m venv .venv
& .venv\Scripts\python.exe -m pip install -e .
& .venv\Scripts\python.exe -m agentic_content_system --help
Write-Output "Agentic Content System setup is ready."
