@echo off
echo 🚀 STARTING CONTINUOUS NEWS MONITORING
echo ======================================
echo 📡 Will check Cameroon news sources every 30 minutes
echo 📰 Sources: Cameroon Tribune, Journal du Cameroun, Business in Cameroon
echo 🔄 Press Ctrl+C to stop
echo ======================================
echo.

cd /d "%~dp0"
python continuous_news_monitor.py

pause
