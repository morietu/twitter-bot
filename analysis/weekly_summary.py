import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
import os

# ✅ 日本語フォント設定
plt.rcParams['font.family'] = 'Meiryo'

# 環境変数読み込み
load_dotenv()
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ディレクトリ設定
csv_dir = Path("data")
output_dir = Path("output")
output_dir.mkdir(exist_ok=True)

# CSVの統合
all_files = list(csv_dir.glob("tweets_*_labeled.csv"))
if not all_files:
    print("⚠️ CSVファイルが見つかりません。collector.py → classifier.py を実行してください。")
    exit()

df_list = [pd.read_csv(f) for f in all_files]
df = pd.concat(df_list, ignore_index=True)

# 日時変換と時間帯分類
df["created_at"] = pd.to_datetime(df["created_at"])
df["hour"] = df["created_at"].dt.hour

def classify_time(hour):
    if 5 <= hour < 11:
        return "朝"
    elif 11 <= hour < 17:
        return "昼"
    elif 17 <= hour < 22:
        return "夕方"
    else:
        return "夜"

df["時間帯"] = df["hour"].apply(classify_time)

# カテゴリ×時間帯のクロス集計
pivot = pd.pivot_table(df, index="category", columns="時間帯", values="text", aggfunc="count", fill_value=0)

# ヒートマップ描画
plt.figure(figsize=(10, 6))
sns.heatmap(pivot, annot=True, fmt="d", cmap="YlGnBu")
plt.title("カテゴリ×時間帯 出現数（週次）", fontsize=14)
plt.xlabel("時間帯")
plt.ylabel("カテゴリ")
plt.tight_layout()
heatmap_path = output_dir / "heatmap_weekly.png"
plt.savefig(heatmap_path)
plt.close()

# 時間帯ごとの平均いいね数（bar plot）
likes_mean = df.groupby("時間帯")["likes"].mean().reindex(["朝", "昼", "夕方", "夜"])
plt.figure(figsize=(6, 4))
likes_mean.plot(kind="bar", color="skyblue")
plt.title("時間帯別の平均いいね数")
plt.ylabel("平均いいね数")
plt.xlabel("時間帯")
plt.tight_layout()
likes_plot_path = output_dir / "likes_by_time.png"
plt.savefig(likes_plot_path)
plt.close()

# HTMLレポートとして保存（簡易）
today_str = datetime.now().strftime("%Y%m%d")
report_path = output_dir / f"weekly_report_{today_str}.html"
with open(report_path, "w", encoding="utf-8") as f:
    f.write(f"""
    <html>
    <head><meta charset="utf-8"><title>週次Twitter分析レポート</title></head>
    <body>
    <h1>週次Twitter分析レポート（{today_str}）</h1>
    <h2>1. カテゴリ×時間帯 出現ヒートマップ</h2>
    <img src="{heatmap_path.name}" width="600"><br>
    <h2>2. 時間帯別 平均いいね数</h2>
    <img src="{likes_plot_path.name}" width="400"><br>
    <p>対象ツイート数：{len(df)} 件</p>
    </body>
    </html>
    """)

print(f"✅ レポート出力完了 → {report_path}")


# 投稿文プロンプト
def generate_summary_text(df, pivot, likes_mean, date_str):
    prompt = f"""
あなたはTwitter分析アシスタントです。以下の条件で週次レポートの文章を日本語で生成してください。

# 条件:
- 日付: {date_str}
- 分析対象のカテゴリとその投稿数: {dict(df['category'].value_counts())}
- 各時間帯ごとの投稿件数と平均いいね数: {likes_mean.to_dict()}
- カテゴリ×時間帯のクロス集計結果: {pivot.to_dict()}

# 指示:
- note用の読みやすい週次レポートの本文として
- 口調は丁寧でわかりやすく
- 箇条書きや見出しを交えて
- SNS運用者が参考にできる具体的な分析を含めてください
- 800文字以内で出力してください
    """
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "あなたはSNSマーケティングの分析アシスタントです。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ OpenAI API エラー: {e}"

# 要約文の生成
summary_text = generate_summary_text(df, pivot, likes_mean, today_str)
summary_path = output_dir / f"weekly_summary_{today_str}.txt"
with open(summary_path, "w", encoding="utf-8") as f:
    f.write(summary_text)

print(f"📝 投稿文生成 → {summary_path}")

import tweepy

def post_to_twitter(text_path):
    with open(text_path, encoding="utf-8") as f:
        content = f.read()

    # 読み込んだ要約文をトリムして280文字以内に収める（note誘導も可能）
    max_length = 260  # noteリンク付きにしたい場合は260にする
    tweet_text = content[:max_length] + " #週次レポート"

    # Twitter認証
    auth = tweepy.OAuth1UserHandler(
        os.getenv("API_KEY"),
        os.getenv("API_SECRET"),
        os.getenv("ACCESS_TOKEN"),
        os.getenv("ACCESS_SECRET"),
    )
    api = tweepy.API(auth)

    try:
        api.update_status(status=tweet_text)
        print("✅ X（Twitter）へ自動投稿完了！")
    except Exception as e:
        print(f"⚠️ Twitter投稿エラー: {e}")

# --- Zenn記事ファイルとして保存 ---
zenn_path = Path("../zenn-content/articles")  # GitHubに連携しているZenn用リポジトリ
zenn_path.mkdir(parents=True, exist_ok=True)

md_filename = f"weekly-report-{today_str}.md"
md_path = zenn_path / md_filename

with open(md_path, "w", encoding="utf-8") as f:
    f.write(f"""---
title: "Twitter週次レポート（{today_str}）"
emoji: "📈"
type: "idea"
topics: ["Twitter", "SNS分析"]
published: true
---

{summary_text}
""")

print(f"📝 Zenn投稿用Markdown生成 → {md_path}")
