import pyautogui
import pyperclip
import schedule
import time
import os
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError
import logging
import pygetwindow as gw
import requests
from bs4 import BeautifulSoup
import tweepy

client = tweepy.Client(bearer_token="YOUR_BEARER_TOKEN")
query = "#筋トレ -is:retweet lang:ja"

response = client.search_recent_tweets(
    query=query,
    tweet_fields=["created_at", "public_metrics", "text", "author_id"],
    max_results=50
)

tweets = response.data

def fetch_note_body(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    body = soup.find("div", class_="o-noteContent")  # ← クラス名はnoteの仕様によって変わる
    return body.get_text(strip=True) if body else None

load_dotenv()

# OpenAI設定
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ログ設定
logging.basicConfig(
    filename="logs/success_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    encoding="utf-8")

NOTE_URL = "https://note.com/famous_walrus484"

def generate_tweet(time_of_day: str) -> str:
    # note本文取得
    body_text = fetch_note_body(NOTE_URL)
    if not body_text:
        print("[❌ ERROR] note本文の取得に失敗しました")
        return "note本文の取得に失敗しました"
    

    prompt = f"""
    {time_of_day}の時間帯に投稿する筋トレメニューとストレッチ、一言メッセージを含めて、
    以下のnote記事の内容を元に、日本語で全角260文字以内のツイート文を作ってください。
    文末に note リンクをつける余裕（約20文字分）を残してください。

    【note本文】:
    {body_text}

    """
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"system", "content": "あなたはnote投稿をTwitter向けに要約・整形するアシスタントです。"}
                {"role": "user", "content": prompt}
                ],
                max_tokens=100
            temperature=0.8,
            timeout=30
        )

        tweet = response.choices[0].message.content.strip()

        # 260文字以内に調整（URL余白確保）
        if len(tweet) > 240:
            tweet = tweet[:240] + "..."

        tweet += f"\n{NOTE_URL}"
        return tweet
        
    except OpenAIError as e:
        print(f"[❌ ERROR] OpenAI API呼び出し失敗: {e}")
        return "ツイート文の生成に失敗しました"

def is_target_window_active(window_keywords=["X", "投稿", "Compose", "Tweet"]):
    try:
        active_window = gw.getActiveWindow()
        print(f"[DEBUG] アクティブウィンドウタイトル: {active_window.title}")
        return any(keyword in active_window.title for keyword in window_keywords)
    except Exception as e:
        print(f"[❌ ERROR] アクティブウィンドウ取得に失敗: {e}")
        return False

def tweet_from_gui(tweet_text: str):
    pyperclip.copy(tweet_text)
    time.sleep(1)

    max_attempts = 3
    for i in range(max_attempts):
        if is_target_window_active("X"):
            print(f"[INFO] 投稿画面にフォーカスあり（{i+1}回目）")
            pyautogui.hotkey("ctrl", "a")
            pyautogui.hotkey("backspace")  # 削除
            time.sleep(0.5)
            pyautogui.hotkey("ctrl", "v")  # 再貼り付け
            time.sleep(1)


            pyautogui.click(x=1165, y=513)  # ← 座標クリック（適宜調整）
            print("[✅ SUCCESS] 投稿完了")
            return
        else:
            print(f"[⚠️ WARNING] 投稿画面以外にフォーカスあり（{i+1}回目）")
            time.sleep(2)

    print("[❌ STOP] 投稿画面が見つからないため処理を中断します。")

def run_post(time_of_day: str):
    print(f"[INFO] {time_of_day} のツイートを生成・投稿します。")
    tweet_text = generate_tweet(time_of_day)
    print("[DEBUG] 投稿文:\n", tweet_text)
    tweet_from_gui(tweet_text)

# スケジュール
schedule.every().day.at("08:00").do(run_post, time_of_day="morning")
schedule.every().day.at("12:00").do(run_post, time_of_day="noon")
schedule.every().day.at("20:00").do(run_post, time_of_day="night")

print("[INFO] GPT付き自動投稿Botが待機中です（Ctrl+Cで停止）")

run_post("test")
while True:
    schedule.run_pending()
    time.sleep(10)
