"""
SQLiteデータベース管理モジュール

テーブル構成:
  shops - ラーメン店情報
"""

import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "ramen.db")


def get_connection():
    """DB接続を取得する"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """テーブルを作成する"""
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS shops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT,
            prefecture TEXT,
            rating TEXT,
            genre TEXT,
            url TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    print("データベースを初期化しました。")


def insert_shops(shops, prefecture=""):
    """店舗データを一括挿入する（重複URLはスキップ）"""
    conn = get_connection()
    inserted = 0
    skipped = 0

    for shop in shops:
        try:
            conn.execute(
                """
                INSERT INTO shops (name, address, prefecture, rating, genre, url)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    shop["name"],
                    shop["address"],
                    prefecture,
                    shop["rating"],
                    shop["genre"],
                    shop["url"],
                ),
            )
            inserted += 1
        except sqlite3.IntegrityError:
            skipped += 1

    conn.commit()
    conn.close()
    print(f"DB保存: {inserted}件追加, {skipped}件スキップ（重複）")
    return inserted


def search_shops(prefecture=None, genre=None, keyword=None):
    """店舗を検索する"""
    conn = get_connection()
    query = "SELECT * FROM shops WHERE 1=1"
    params = []

    if prefecture:
        query += " AND prefecture = ?"
        params.append(prefecture)

    if genre:
        query += " AND genre LIKE ?"
        params.append(f"%{genre}%")

    if keyword:
        query += " AND (name LIKE ? OR address LIKE ? OR genre LIKE ?)"
        params.extend([f"%{keyword}%"] * 3)

    query += " ORDER BY rating DESC"

    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_shop_count():
    """登録件数を取得する"""
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM shops").fetchone()[0]
    conn.close()
    return count


if __name__ == "__main__":
    init_db()
    print(f"現在の登録件数: {get_shop_count()}件")
