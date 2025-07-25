# 1日3回の自動収集スケジューラ

# scheduler.py

import schedule
import time
from analysis.collector import collect_tweets
from analysis.classifier import classify_csv
from analysis.analyzer import analyze_labeled_csv
from datetime import datetime

def collect_and_analyze():
    now = datetime.now().strftime("%Y%m%d-%H%M")
    raw_file = f"data/tweets_{now}.csv"
    labeled_file = raw_file.replace(".csv", "_labeled.csv")

    print(f"[▶] データ収集開始: {now}")
    collect_tweets(query="#筋トレ", max_results=50, out_dir="data")
    classify_csv(raw_file, labeled_file)
    analyze_labeled_csv(labeled_file)

# 毎日 8:00 / 12:00 / 20:00 に実行
schedule.every().day.at("08:00").do(collect_and_analyze)
schedule.every().day.at("12:00").do(collect_and_analyze)
schedule.every().day.at("20:00").do(collect_and_analyze)

print("[📅] スケジューラ稼働中（Ctrl+Cで終了）")
while True:
    schedule.run_pending()
    time.sleep(10)
