# Dot-source this file in a PowerShell session to use local, offline PDF assets.
# These settings apply only to that session. No API keys or persistent settings are touched.
$scileadRoot = $PSScriptRoot
$env:NLTK_DATA = Join-Path $scileadRoot 'assets\nltk_data'
$env:HF_HOME = Join-Path $scileadRoot 'assets\huggingface'
$env:TESSDATA_PREFIX = Join-Path $scileadRoot 'tools\tesseract\tessdata'
$env:MPLCONFIGDIR = Join-Path $scileadRoot 'assets\matplotlib-cache'
$env:HF_HUB_OFFLINE = '1'
$env:TRANSFORMERS_OFFLINE = '1'
$env:HF_HUB_DISABLE_TELEMETRY = '1'
$env:HF_HUB_DISABLE_IMPLICIT_TOKEN = '1'
$env:ANONYMIZED_TELEMETRY = 'False'
$env:DO_NOT_TRACK = '1'
$env:LANGCHAIN_TRACING = 'false'
$env:LANGCHAIN_TRACING_V2 = 'false'
$env:LANGSMITH_TRACING = 'false'
$scileadToolPaths = @(
    (Join-Path $scileadRoot 'tools\tesseract'),
    (Join-Path $scileadRoot 'tools\pdf-system\Library\bin')
)
$env:PATH = ($scileadToolPaths -join ';') + ';' + $env:PATH
Write-Output 'SCILEAD PDF assets configured for this session; inference is offline.'
Write-Output 'Python: D:\miniconda3\envs\scilead\python.exe'
