@echo off
REM filepath: c:\Users\alifa\Documents\Fasilkom\PPL\new\pantautular-be\run_stress_test.bat
echo ===== PANTAU TULAR API STATISTICS STRESS TEST =====
echo.

set SECRET_API_KEY=test-api-key

echo 1. Running k6 stress test with 150 users...
echo.
k6 run --env SECRET_API_KEY=%SECRET_API_KEY% --summary-export=results.json statistics_test.js

if %errorlevel% neq 0 (
    echo.
    echo ERROR: k6 test failed with error code %errorlevel%.
    echo Please check the statistics_test.js file for syntax errors.
    goto :end
)

echo.
echo 2. Test completed. Analyzing results...
echo.

REM Check if results.json exists
if not exist results.json (
    echo ERROR: No results file generated. The test may have failed.
    goto :end
)

REM Check if Python is installed
where python >nul 2>&1
if %errorlevel% equ 0 (
    echo Running Python analysis script...
    python analyze_results.py results.json
    if %errorlevel% neq 0 (
        echo Error running analysis script. Examining raw JSON...
        echo.
        echo Raw JSON preview:
        powershell -Command "if(Test-Path results.json){Get-Content results.json -Head 20}else{Write-Host 'results.json not found'}"
        echo.
        echo [Full results saved to results.json]
    )
) else (
    echo Python not found. Raw results:
    powershell -Command "if(Test-Path results.json){Get-Content results.json -Head 20}else{Write-Host 'results.json not found'}"
)

:end
echo.
echo ===== STRESS TEST COMPLETED =====