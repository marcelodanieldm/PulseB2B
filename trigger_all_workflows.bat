@echo off
REM Trigger all GitHub Actions workflows
echo ========================================
echo  GitHub Actions Workflow Trigger
echo ========================================
echo.

REM Check if GITHUB_TOKEN is set
if "%GITHUB_TOKEN%"=="" (
    echo [ERROR] GITHUB_TOKEN environment variable not set
    echo.
    echo Please set your GitHub Personal Access Token:
    echo   $env:GITHUB_TOKEN = "your_token_here"
    echo.
    echo Create a token at: https://github.com/settings/tokens
    echo Required scopes: repo, workflow
    echo.
    pause
    exit /b 1
)

echo [INFO] Triggering all workflows...
echo.

python trigger_all_workflows.py

echo.
echo Press any key to exit...
pause > nul
