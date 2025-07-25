@echo off
cd /d C:\Users\user\Desktop\Twitter_bot

:: ログ追記
echo [%DATE% %TIME%] Bot started >> bot_log.txt

:: UTF-8指定でログにprint出力も書き出す
set PYTHONIOENCODING=utf-8

:: 仮想環境の python を直接実行してログ出力も通す
C:\Users\user\Desktop\Twitter_bot\.venv\Scripts\python.exe tweet_bot.py >> bot_log.txt 2>&1

pause
