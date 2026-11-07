<#
.SYNOPSIS
  Live demo: starts Gitea, runs selected Selenium tests in a visible browser and
  evaluates one view with LLM-as-a-Judge.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File scripts\demo.ps1
  powershell -ExecutionPolicy Bypass -File scripts\demo.ps1 -SkipJudge
#>
param(
    [switch]$SkipJudge,
    [string]$Distro = "Debian",
    [string]$View = "issues_list"
)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$python = Join-Path $root ".venv\Scripts\python.exe"

function Step($text) { Write-Host "`n=== $text ===" -ForegroundColor Cyan }

Step "1/4 Starting Gitea 28.3.0 (Docker in WSL: $Distro)"
$wslRoot = (wsl -d $Distro -- wslpath -a ($root -replace '\\', '/')).Trim()
wsl -d $Distro -- bash -lc "cd '$wslRoot' && bash scripts/bootstrap.sh"
if ($LASTEXITCODE -ne 0) { throw "bootstrap failed" }

Step "2/4 Selenium UI tests in a visible browser"
$env:HEADLESS = "0"
$env:SCREENSHOTS = "all"
& $python -m pytest tests/ui -v `
    -k "wrong_password or issue_with_label or comment_close_and_reopen or merge_pull_request" `
    --html=reports/demo.html --self-contained-html
$testsExit = $LASTEXITCODE
Remove-Item Env:HEADLESS, Env:SCREENSHOTS

Step "3/4 Test report: reports\demo.html"
Start-Process (Join-Path $root "reports\demo.html")

if (-not $SkipJudge) {
    Step "4/4 LLM-as-a-Judge: view '$View' (1 run)"
    & $python -m llm_judge.capture
    & $python -m llm_judge.judge --view $View --runs 1 --results-dir reports/demo_judge
    Get-Content -Encoding utf8 reports\demo_judge\summary.md
}
exit $testsExit
