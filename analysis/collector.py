# 情報収集（search_recent_tweets）
# analysis/collector.py

import tweepy
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv

# .envからBEARER_TOKENを読み込む
load_dotenv()
BEARER_TOKEN = os.getenv("BEARER_TOKEN")

if not BEARER_TOKEN:
    raise ValueError("❌ .env に BEARER_TOKEN が設定されていません")

client = tweepy.Client(bearer_token=BEARER_TOKEN)

def collect_tweets(query="#筋トレ", max_results=50, out_dir="data"):
    response = client.search_recent_tweets(
        query=f"{query} -is:retweet lang:ja",
        tweet_fields=["created_at", "public_metrics", "text", "author_id"],
        max_results=max_results
    )

    tweets = response.data
    if not tweets:
        print("[⚠️] ツイートが取得できませんでした")
        return

    # ツイート情報をリストに格納
    data = []
    for tweet in tweets:
        metrics = tweet.public_metrics
        data.append({
            "text": tweet.text,
            "likes": metrics["like_count"],
            "retweets": metrics["retweet_count"],
            "created_at": tweet.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })

    # 保存先ディレクトリ作成（なければ）
    os.makedirs(out_dir, exist_ok=True)

    # ファイル名に日付を付けて保存
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    out_file = os.path.join(out_dir, f"tweets_{timestamp}.csv")
    pd.DataFrame(data).to_csv(out_file, index=False, encoding="utf-8-sig")

    print(f"[✅] {len(data)}件のツイートを収集・保存しました → {out_file}")

# テスト実行
if __name__ == "__main__":
    collect_tweets()
