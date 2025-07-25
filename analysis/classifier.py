# GPTでカテゴリ分類
# analysis/classifier.py

import pandas as pd
import os
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
import glob

latest_file = sorted(glob.glob("data/tweets_*.csv"))[-1]


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

CATEGORY_LABELS = [
    "モチベ系", "記録系", "食事・栄養系", "情報系", "雑談系"
]

def classify_tweet(text: str) -> str:
    prompt = f"""
以下のツイートを、次のカテゴリから1つ選んで分類してください：
- モチベ系（やる気・自己肯定・ポジティブな内容）
- 記録系（回数・メニュー・日数など）
- 食事・栄養系（サプリや栄養成分など）
- 情報系（商品紹介・知識・テクニックなど）
- 雑談系（筋トレ以外や混ざった話題）

ツイート本文：
{text}

カテゴリ名のみで回答してください（例：「モチベ系」）
"""

    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "あなたはSNS投稿を分類するアシスタントです。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=10,
            timeout=20
        )
        return res.choices[0].message.content.strip()
    except Exception as e:
        print("[⚠️ GPT ERROR]", e)
        return "分類失敗"
def get_time_zone(hour):
    if 5 <= hour < 11:
        return "朝"
    elif 11 <= hour < 16:
        return "昼"
    elif 16 <= hour < 22:
        return "夜"
    else:
        return "深夜"

def classify_csv(input_path: str, output_path: str):
    df = pd.read_csv(input_path)

    print(f"[INFO] 分類中... {len(df)} 件")

    # ① GPTでカテゴリ分類
    df["category"] = df["text"].apply(classify_tweet)


     # ② created_at → datetime変換 → 時間帯列を追加
    df["created_at"] = pd.to_datetime(df["created_at"])
    df["time_zone"] = df["created_at"].dt.hour.apply(get_time_zone)



    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"[✅] 分類結果を保存 → {output_path}")

if __name__ == "__main__":
    input_file = "data/tweets_20250725-0735.csv"  # ←最新のCSVに書き換えてOK
    output_file = input_file.replace(".csv", "_labeled.csv")
    classify_csv(input_file, output_file)
