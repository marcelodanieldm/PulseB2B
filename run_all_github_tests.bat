@echo off
echo.
echo ╔═══════════════════════════════════════════════════════════════════╗
echo ║       Complete GitHub Actions Testing Suite                      ║
echo ╚═══════════════════════════════════════════════════════════════════╝
echo.

echo [1/4] Running validation tests...
echo =====================================
python test_github_actions.py
echo.
echo.

echo [2/4] Checking workflow status...
echo =====================================
python check_workflow_status.py
echo.
echo.

echo [3/4] Setting up secrets helpers...
echo =====================================
python setup_github_secrets.py
echo.
echo.

echo [4/4] Generating final summary...
echo =====================================
echo.
echo ✅ All tests complete!
echo.
echo 📋 Generated files:
echo    • data/output/github_actions_test_report.txt
echo    • data/output/workflow_status_report.txt
echo    • data/output/github_secrets_guide.txt
echo    • configure_secrets.ps1
echo    • .env.template
echo.
echo 📚 Documentation:
echo    • GITHUB_ACTIONS_TESTING.md
echo    • GITHUB_ACTIONS_TEST_SUMMARY.md
echo.
echo 🚀 Next steps:
echo    1. Review: GITHUB_ACTIONS_TEST_SUMMARY.md
echo    2. Configure secrets using: configure_secrets.ps1
echo    3. Push to GitHub
echo    4. Test workflows in GitHub Actions tab
echo.
pause
