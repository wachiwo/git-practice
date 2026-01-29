"""
ラーメン店検索Webアプリ

使い方:
    python app.py
    ブラウザで http://localhost:5000 にアクセス
"""

from flask import Flask, render_template, request

from scraper.database import init_db, search_shops, get_shop_count

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


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
