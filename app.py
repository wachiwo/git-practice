"""
ラーメン店検索Webアプリ

使い方:
    python app.py
    ブラウザで http://localhost:5000 にアクセス
"""

import threading

from flask import Flask, render_template, request, jsonify, redirect, url_for

from scraper.database import init_db, search_shops, get_shop_count, insert_shops
from scraper.tabelog_scraper import PREFECTURES, build_url, fetch_page, parse_shops

app = Flask(__name__)

PREFECTURE_NAMES = {
    "": "すべて",
    "hokkaido": "北海道",
    "aomori": "青森", "iwate": "岩手", "miyagi": "宮城",
    "akita": "秋田", "yamagata": "山形", "fukushima": "福島",
    "ibaraki": "茨城", "tochigi": "栃木", "gunma": "群馬",
    "saitama": "埼玉", "chiba": "千葉", "tokyo": "東京",
    "kanagawa": "神奈川",
    "niigata": "新潟", "toyama": "富山", "ishikawa": "石川",
    "fukui": "福井", "yamanashi": "山梨", "nagano": "長野",
    "gifu": "岐阜", "shizuoka": "静岡", "aichi": "愛知", "mie": "三重",
    "shiga": "滋賀", "kyoto": "京都", "osaka": "大阪",
    "hyogo": "兵庫", "nara": "奈良", "wakayama": "和歌山",
    "tottori": "鳥取", "shimane": "島根", "okayama": "岡山",
    "hiroshima": "広島", "yamaguchi": "山口",
    "tokushima": "徳島", "kagawa": "香川", "ehime": "愛媛", "kochi": "高知",
    "fukuoka": "福岡", "saga": "佐賀", "nagasaki": "長崎",
    "kumamoto": "熊本", "oita": "大分", "miyazaki": "宮崎",
    "kagoshima": "鹿児島", "okinawa": "沖縄",
}

GENRES = ["", "ラーメン", "つけ麺", "味噌", "豚骨", "醤油", "塩", "太麺", "細麺"]


@app.route("/")
def index():
    prefecture = request.args.get("prefecture", "")
    genre = request.args.get("genre", "")
    keyword = request.args.get("keyword", "")

    results = search_shops(
        prefecture=prefecture or None,
        genre=genre or None,
        keyword=keyword or None,
    )

    return render_template(
        "index.html",
        results=results,
        prefectures=PREFECTURE_NAMES,
        genres=GENRES,
        selected_prefecture=prefecture,
        selected_genre=genre,
        keyword=keyword,
        total_count=get_shop_count(),
    )


scrape_status = {"running": False, "message": "", "count": 0}


@app.route("/scrape", methods=["POST"])
def scrape():
    pref = request.form.get("scrape_prefecture", "")
    pages = int(request.form.get("scrape_pages", 1))

    if not pref or pref not in PREFECTURES:
        return redirect(url_for("index"))

    if scrape_status["running"]:
        return redirect(url_for("index"))

    def run_scrape():
        import time
        scrape_status["running"] = True
        scrape_status["message"] = "取得中..."
        scrape_status["count"] = 0

        all_shops = []
        for page in range(1, pages + 1):
            try:
                url = build_url(PREFECTURES[pref], page)
                html = fetch_page(url)
                shops = parse_shops(html)
                all_shops.extend(shops)
                scrape_status["message"] = f"ページ {page}/{pages} 完了（{len(all_shops)}件取得）"
            except Exception as e:
                scrape_status["message"] = f"エラー: {e}"
                break
            if page < pages:
                time.sleep(3)

        if all_shops:
            inserted = insert_shops(all_shops, prefecture=pref)
            scrape_status["count"] = inserted
            scrape_status["message"] = f"完了: {inserted}件追加（合計 {get_shop_count()}件）"
        elif "エラー" not in scrape_status["message"]:
            scrape_status["message"] = "データが取得できませんでした。"

        scrape_status["running"] = False

    thread = threading.Thread(target=run_scrape)
    thread.start()

    return redirect(url_for("index"))


@app.route("/scrape/status")
def scrape_status_api():
    return jsonify(scrape_status)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
