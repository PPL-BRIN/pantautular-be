@echo off
REM filepath: c:\Users\alifa\Documents\Fasilkom\PPL\new\pantautular-be\run_stress_test.bat
echo ===== PANTAU TULAR API STATISTICS STRESS TEST =====
echo.

set SECRET_API_KEY=test-api-key

echo 1. Running k6 stress test with 150 users...
echo.
k6 run --env SECRET_API_KEY=%SECRET_API_KEY% statistics_test.js

if %errorlevel% neq 0 (
    echo.
    echo ERROR: k6 test failed with error code %errorlevel%.
    echo Please check the statistics_test.js file for syntax errors.
    goto :end
)

echo.
echo 2. Test completed. Results displayed above.
echo.

echo Summary of key metrics:
echo - http_req_duration: Total request duration (DNS + connection + TLS + processing + waiting)
echo - http_req_failed: Rate of failed requests (non-2xx responses)
echo - checks: Rate of successful checks
echo - iterations: Number of complete iterations of the default function

echo.
echo For detailed analysis, view the test results above.
echo A summary JSON has also been exported to: results.json
echo.

:end
echo.
echo ===== STRESS TEST COMPLETED =====