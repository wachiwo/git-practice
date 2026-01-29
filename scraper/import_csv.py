"""
CSVファイルからSQLiteデータベースにインポートするスクリプト

使い方:
    python scraper/import_csv.py data/sample_ramen.csv --prefecture tokyo
"""

import argparse
import csv
import sys

from scraper.database import init_db, insert_shops, get_shop_count


def load_csv(filepath):
    """CSVファイルを読み込む"""
    shops = []
    with open(filepath, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            shops.append(row)
    return shops


def main():
    parser = argparse.ArgumentParser(description="CSVからDBへインポート")
    parser.add_argument("csv_file", help="インポートするCSVファイルのパス")
    parser.add_argument(
        "--prefecture", "-p",
        default="",
        help="都道府県（ローマ字）",
    )
    args = parser.parse_args()

    init_db()

    print(f"CSVファイル: {args.csv_file}")
    shops = load_csv(args.csv_file)
    print(f"読み込み件数: {len(shops)}件")

    insert_shops(shops, prefecture=args.prefecture)
    print(f"DB総登録件数: {get_shop_count()}件")


if __name__ == "__main__":
    main()
