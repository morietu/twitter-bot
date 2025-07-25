# 可視化 or 統計出力
# analysis/analyzer.py

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# フォント設定（Windows）
plt.rcParams['font.family'] = 'Meiryo'

def analyze_labeled_csv(path):
    df = pd.read_csv(path)

    os.makedirs("output", exist_ok=True)

    # ① カテゴリ別 投稿数
    plt.figure(figsize=(8, 5))
    ax = sns.countplot(
        data=df,
        x="category",
        order=df["category"].value_counts().index,
        palette="Set2"
    )
    plt.title("カテゴリ別 投稿数", fontsize=14)
    plt.xlabel("投稿カテゴリ", fontsize=12)
    plt.ylabel("投稿件数", fontsize=12)
    for p in ax.patches:
        ax.annotate(f'{p.get_height()}', (p.get_x() + 0.3, p.get_height()), fontsize=10)
    plt.tight_layout()
    plt.savefig("output/category_count.png")
    plt.close()
    print("[📊] カテゴリ別投稿数 → output/category_count.png")

    # ② カテゴリ別 平均いいね数
    plt.figure(figsize=(8, 5))
    like_avg = df.groupby("category")["likes"].mean().sort_values(ascending=False)
    ax = sns.barplot(x=like_avg.index, y=like_avg.values, palette="Set1")
    plt.title("カテゴリ別 平均いいね数", fontsize=14)
    plt.xlabel("投稿カテゴリ", fontsize=12)
    plt.ylabel("平均いいね数", fontsize=12)
    for i, v in enumerate(like_avg.values):
        ax.text(i, v + 0.1, f"{v:.1f}", ha='center', fontsize=10)
    plt.tight_layout()
    plt.savefig("output/likes_by_category.png")
    plt.close()
    print("[📊] カテゴリ別平均いいね → output/likes_by_category.png")

    # ③ 時間帯別 投稿数
    plt.figure(figsize=(8, 5))
    ax = sns.countplot(data=df, x="time_zone", order=["朝", "昼", "夜", "深夜"], palette="pastel")
    plt.title("時間帯別 投稿数", fontsize=14)
    plt.xlabel("時間帯", fontsize=12)
    plt.ylabel("投稿件数", fontsize=12)
    for p in ax.patches:
        ax.annotate(f'{p.get_height()}', (p.get_x() + 0.2, p.get_height()), fontsize=10)
    plt.tight_layout()
    plt.savefig("output/timezone_count.png")
    plt.close()
    print("[📊] 時間帯別投稿数 → output/timezone_count.png")

    # ④ 時間帯別 平均いいね数
    plt.figure(figsize=(8, 5))
    like_avg_tz = df.groupby("time_zone")["likes"].mean().reindex(["朝", "昼", "夜", "深夜"])
    ax = sns.barplot(x=like_avg_tz.index, y=like_avg_tz.values, palette="muted")
    plt.title("時間帯別 平均いいね数", fontsize=14)
    plt.xlabel("時間帯", fontsize=12)
    plt.ylabel("平均いいね数", fontsize=12)
    for i, v in enumerate(like_avg_tz.values):
        ax.text(i, v + 0.1, f"{v:.1f}", ha='center', fontsize=10)
    plt.tight_layout()
    plt.savefig("output/likes_by_timezone.png")
    plt.close()
    print("[📊] 時間帯別平均いいね → output/likes_by_timezone.png")

    # ⑤ カテゴリ × 時間帯 のクロス集計（平均いいね数）＋ヒートマップ
    plt.figure(figsize=(10, 6))
    pivot_table = pd.pivot_table(
        df,
        values="likes",
        index="category",
        columns="time_zone",
        aggfunc="mean"
    ).reindex(columns=["朝", "昼", "夜", "深夜"])
    
    sns.heatmap(pivot_table, annot=True, fmt=".1f", cmap="YlGnBu")
    plt.title("カテゴリ × 時間帯 × 平均いいね数（ヒートマップ）", fontsize=14)
    plt.xlabel("時間帯", fontsize=12)
    plt.ylabel("投稿カテゴリ", fontsize=12)
    plt.tight_layout()
    plt.savefig("output/heatmap_category_timezone.png")
    plt.close()
    print("[📊] ヒートマップ出力 → output/heatmap_category_timezone.png")

if __name__ == "__main__":
    input_file = "data/tweets_20250725-0735_labeled.csv"  # ← 適宜変更
    analyze_labeled_csv(input_file)
