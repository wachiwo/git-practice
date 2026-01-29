"""
食べログ ラーメン店スクレイピングスクリプト

使い方:
    python scraper/tabelog_scraper.py --prefecture tokyo
    python scraper/tabelog_scraper.py --prefecture osaka --pages 3
    python scraper/tabelog_scraper.py --prefecture tokyo --save-db
"""

import argparse
import csv
import os
import time

import requests
from bs4 import BeautifulSoup

# 都道府県コード（食べログURL用）
PREFECTURES = {
    "hokkaido": "hokkaido",
    "aomori": "aomori",
    "iwate": "iwate",
    "miyagi": "miyagi",
    "akita": "akita",
    "yamagata": "yamagata",
    "fukushima": "fukushima",
    "ibaraki": "ibaraki",
    "tochigi": "tochigi",
    "gunma": "gunma",
    "saitama": "saitama",
    "chiba": "chiba",
    "tokyo": "tokyo",
    "kanagawa": "kanagawa",
    "niigata": "niigata",
    "toyama": "toyama",
    "ishikawa": "ishikawa",
    "fukui": "fukui",
    "yamanashi": "yamanashi",
    "nagano": "nagano",
    "gifu": "gifu",
    "shizuoka": "shizuoka",
    "aichi": "aichi",
    "mie": "mie",
    "shiga": "shiga",
    "kyoto": "kyoto",
    "osaka": "osaka",
    "hyogo": "hyogo",
    "nara": "nara",
    "wakayama": "wakayama",
    "tottori": "tottori",
    "shimane": "shimane",
    "okayama": "okayama",
    "hiroshima": "hiroshima",
    "yamaguchi": "yamaguchi",
    "tokushima": "tokushima",
    "kagawa": "kagawa",
    "ehime": "ehime",
    "kochi": "kochi",
    "fukuoka": "fukuoka",
    "saga": "saga",
    "nagasaki": "nagasaki",
    "kumamoto": "kumamoto",
    "oita": "oita",
    "miyazaki": "miyazaki",
    "kagoshima": "kagoshima",
    "okinawa": "okinawa",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

BASE_URL = "https://tabelog.com"


def build_url(prefecture, page=1):
    """検索URLを組み立てる"""
    url = f"{BASE_URL}/{prefecture}/rstLst/ramen/{page}/"
    return url


def fetch_page(url):
    """ページのHTMLを取得する"""
    print(f"  取得中: {url}")
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    return response.text


def parse_shops(html):
    """HTMLからラーメン店情報をパースする"""
    soup = BeautifulSoup(html, "html.parser")
    shops = []

    # 店舗リストを取得
    shop_list = soup.select(".list-rst")

    for shop in shop_list:
        # 店名
        name_tag = shop.select_one(".list-rst__rst-name-target")
        name = name_tag.text.strip() if name_tag else ""

        # URL
        shop_url = name_tag.get("href", "") if name_tag else ""

        # 評価
        rating_tag = shop.select_one(".c-rating__val")
        rating = rating_tag.text.strip() if rating_tag else ""

        # 住所
        area_tag = shop.select_one(".list-rst__area-genre")
        address = ""
        genre = ""
        if area_tag:
            area_text = area_tag.text.strip().split("\n")
            # エリア情報とジャンル情報を分離
            parts = [p.strip() for p in area_text if p.strip()]
            if len(parts) >= 1:
                address = parts[0]
            if len(parts) >= 2:
                genre = parts[1]

        if name:
            shops.append({
                "name": name,
                "address": address,
                "rating": rating,
                "genre": genre,
                "url": shop_url,
            })

    return shops


def save_to_csv(shops, output_path):
    """取得データをCSVに保存する"""
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "address", "rating", "genre", "url"])
        writer.writeheader()
        writer.writerows(shops)

    print(f"\n保存完了: {output_path} ({len(shops)}件)")


def main():
    parser = argparse.ArgumentParser(description="食べログ ラーメン店スクレイピング")
    parser.add_argument(
        "--prefecture", "-p",
        required=True,
        choices=list(PREFECTURES.keys()),
        help="都道府県（ローマ字）",
    )
    parser.add_argument(
        "--pages",
        type=int,
        default=1,
        help="取得ページ数（デフォルト: 1）",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="出力ファイルパス（デフォルト: data/<prefecture>_ramen.csv）",
    )
    parser.add_argument(
        "--save-db",
        action="store_true",
        help="SQLiteデータベースにも保存する",
    )
    args = parser.parse_args()

    prefecture = PREFECTURES[args.prefecture]
    output = args.output or f"data/{args.prefecture}_ramen.csv"

    print(f"=== 食べログ ラーメン店スクレイピング ===")
    print(f"都道府県: {args.prefecture}")
    print(f"取得ページ数: {args.pages}")
    print()

    all_shops = []

    for page in range(1, args.pages + 1):
        print(f"--- ページ {page}/{args.pages} ---")
        url = build_url(prefecture, page)

        try:
            html = fetch_page(url)
            shops = parse_shops(html)
            all_shops.extend(shops)
            print(f"  {len(shops)}件 取得")
        except requests.RequestException as e:
            print(f"  エラー: {e}")
            break

        # サーバー負荷軽減のため待機
        if page < args.pages:
            print("  3秒待機中...")
            time.sleep(3)

    if all_shops:
        save_to_csv(all_shops, output)

        if args.save_db:
            from scraper.database import init_db, insert_shops, get_shop_count
            init_db()
            insert_shops(all_shops, prefecture=args.prefecture)
            print(f"DB登録件数: {get_shop_count()}件")
    else:
        print("\nデータが取得できませんでした。")
        print("食べログの構造が変更されている可能性があります。")


if __name__ == "__main__":
    main()
