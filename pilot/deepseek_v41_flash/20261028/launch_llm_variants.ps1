$ErrorActionPreference = 'Stop'
$taskPython = 'D:\miniconda3\envs\scilead\python.exe'
$variantRoot = 'D:\C++\SCILEAD\pilot\deepseek_v41_flash\20261028\variants'
$env:PYTHONHASHSEED = '0'
$env:PYTHONDONTWRITEBYTECODE = '1'
$prepared = Get-Content -LiteralPath (Join-Path $variantRoot 'experiment_manifest.json') -Raw | ConvertFrom-Json
$csStatus = Get-Content -LiteralPath (Join-Path $variantRoot 'fully_cs\execution_status.json') -Raw | ConvertFrom-Json
if ($csStatus.status -ne 'COMPLETE') { throw 'Wait for the isolated CS process to finish before launching API branches.' }
$launchPath = Join-Path $variantRoot 'live_processes.json'
if (Test-Path -LiteralPath $launchPath) {
    $previous = Get-Content -LiteralPath $launchPath -Raw | ConvertFrom-Json
    foreach ($item in $previous) {
        if (Get-Process -Id $item.pid -ErrorAction SilentlyContinue) { throw 'Previous branch process still exists; inspect before relaunch.' }
    }
    throw 'Launch manifest already exists; use explicit individual checkpoint resume after inspection.'
}
$launched = @()
foreach ($branch in @('partially', 'cold_default', 'cold_0', 'cold_42')) {
    $branchDirectory = Join-Path $variantRoot $branch
    $branchScript = Join-Path $variantRoot 'variant_runtime.py'
    $arguments = @('-B','-X','utf8',('"' + $branchScript + '"'),'--branch',$branch)
    $process = Start-Process -FilePath $taskPython -ArgumentList $arguments -WorkingDirectory $variantRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $branchDirectory 'runtime.stdout.log') -RedirectStandardError (Join-Path $branchDirectory 'runtime.stderr.log')
    $launched += [pscustomobject]@{branch=$branch;pid=$process.Id;started_utc=[DateTime]::UtcNow.ToString('o');stdout=(Join-Path $branchDirectory 'runtime.stdout.log');stderr=(Join-Path $branchDirectory 'runtime.stderr.log')}
    $launched | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $launchPath -Encoding UTF8
}
$launched | ConvertTo-Json -Depth 4
