#!/usr/bin/env python3
"""
Profitshare CSV → Astro .md importer
--------------------------------------
Usage:
    python3 profitshare-import.py products.csv --out ./src/content/products

Each row in the CSV becomes one .md file with YAML frontmatter + full
description as the body. No third-party dependencies — stdlib only.
"""

import argparse
import csv
import html
import os
import re
import sys
import unicodedata

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

EUR_TO_BGN = 1.95583          # fixed BG conversion rate
DESCRIPTION_META_MAX = 160   # chars for frontmatter (meta tag)

# ---------------------------------------------------------------------------
# Bulgarian transliteration table (BDS 9.4:2012 / common web standard)
# ---------------------------------------------------------------------------

BG_TRANSLIT = {
    "а": "a",  "б": "b",  "в": "v",  "г": "g",  "д": "d",
    "е": "e",  "ж": "zh", "з": "z",  "и": "i",  "й": "y",
    "к": "k",  "л": "l",  "м": "m",  "н": "n",  "о": "o",
    "п": "p",  "р": "r",  "с": "s",  "т": "t",  "у": "u",
    "ф": "f",  "х": "h",  "ц": "ts", "ч": "ch", "ш": "sh",
    "щ": "sht","ъ": "a",  "ь": "",   "ю": "yu", "я": "ya",
    # uppercase
    "А": "a",  "Б": "b",  "В": "v",  "Г": "g",  "Д": "d",
    "Е": "e",  "Ж": "zh", "З": "z",  "И": "i",  "Й": "y",
    "К": "k",  "Л": "l",  "М": "m",  "Н": "n",  "О": "o",
    "П": "p",  "Р": "r",  "С": "s",  "Т": "t",  "У": "u",
    "Ф": "f",  "Х": "h",  "Ц": "ts", "Ч": "ch", "Ш": "sh",
    "Щ": "sht","Ъ": "a",  "Ь": "",   "Ю": "yu", "Я": "ya",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def transliterate_bg(text: str) -> str:
    """Replace Cyrillic characters with their Latin transliterations."""
    result = []
    for ch in text:
        result.append(BG_TRANSLIT.get(ch, ch))
    return "".join(result)


def slugify(text: str) -> str:
    """Convert a Bulgarian (or any) product name to a URL-safe slug."""
    text = str(text).strip().lower()
    text = transliterate_bg(text)
    # Normalize remaining accented Latin characters
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


def clean_html_entities(text: str) -> str:
    """Decode HTML entities like &rsquo; → ' and strip leftover tags."""
    if not text:
        return ""
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", "", text)
    return text.strip()


def format_price(row: dict) -> str:
    """
    Build price string: 'X.XX € / Y.YY лв.'
    Uses 'Price with discount, with VAT' first, then 'Price with VAT'.
    Currency is always EUR from Profitshare.
    """
    raw = (
        row.get("Price with discount, with VAT", "").strip()
        or row.get("Price with VAT", "").strip()
    )

    if not raw:
        return ""

    try:
        eur = float(raw)
    except ValueError:
        return raw  # return as-is if unparseable

    bgn = eur * EUR_TO_BGN
    return f"{eur:.2f} € / {bgn:.2f} лв."


def truncate(text: str, max_chars: int) -> str:
    """Truncate to max_chars at a word boundary, appending '…' if needed."""
    if len(text) <= max_chars:
        return text
    truncated = text[:max_chars].rsplit(" ", 1)[0]
    return truncated.rstrip(".,;:") + "…"


def safe_date(value: str) -> str:
    """Return ISO date string (YYYY-MM-DD). Falls back to today if empty."""
    from datetime import date
    today = date.today().isoformat()

    if not value or value.strip().lower() in ("", "nan", "none"):
        return today
    if re.match(r"^\d{4}-\d{2}-\d{2}$", value.strip()):
        return value.strip()
    m = re.match(r"^(\d{4}-\d{2}-\d{2})", value.strip())
    if m:
        return m.group(1)
    return today


def escape_yaml_string(text: str) -> str:
    """Wrap value in double quotes and escape internal double quotes."""
    text = text.replace('"', '\\"')
    return f'"{text}"'


def is_empty(value: str) -> bool:
    return not value or value.strip().lower() in ("", "nan", "none")


# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------

def row_to_md(row: dict) -> tuple:
    """Convert a CSV row (dict) to (filename, markdown_content)."""
    product_name = clean_html_entities(row.get("Product name", "Untitled"))
    slug = slugify(product_name)
    filename = f"{slug}.md"

    full_description = clean_html_entities(row.get("Product description", ""))
    meta_description = truncate(full_description, DESCRIPTION_META_MAX)

    price = format_price(row)
    date_str = safe_date(row.get("last_updated", ""))

    affiliate_link = row.get("Product affiliate link", "").strip()
    if affiliate_link.startswith("//"):
        affiliate_link = "https:" + affiliate_link
    image = row.get("Product picture", "").strip()
    brand = clean_html_entities(row.get("Manufacturer", ""))
    category = clean_html_entities(row.get("Category", ""))

    # Build frontmatter
    lines = ["---"]
    lines.append(f"title: {escape_yaml_string(product_name)}")
    lines.append(f"description: {escape_yaml_string(meta_description)}")

    if not is_empty(image):
        lines.append(f"image: {escape_yaml_string(image)}")

    if not is_empty(affiliate_link):
        lines.append(f"affiliateLink: {escape_yaml_string(affiliate_link)}")

    if price:
        lines.append(f"price: {escape_yaml_string(price)}")

    if not is_empty(brand):
        lines.append(f"brand: {escape_yaml_string(brand)}")

    if not is_empty(category):
        lines.append(f"category: {escape_yaml_string(category)}")

    lines.append("featured: false")
    lines.append(f"date: {date_str}")
    lines.append("---")

    # Body: full description after frontmatter
    parts = ["\n".join(lines)]
    if full_description:
        parts.append(f"\n{full_description}\n")

    return filename, "\n".join(parts)


def process(csv_path: str, out_dir: str, dry_run: bool = False) -> None:
    print(f"Reading: {csv_path}")

    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    total = len(rows)
    print(f"Found {total} product(s)\n")

    os.makedirs(out_dir, exist_ok=True)

    written = 0

    for row in rows:
        filename, content = row_to_md(row)
        out_path = os.path.join(out_dir, filename)

        if dry_run:
            print(f"[DRY RUN] Would write: {out_path}")
            print(content[:500])
            print("...\n")
            continue

        # Handle slug collisions by appending Product code
        if os.path.exists(out_path):
            product_code = row.get("Product code", "").strip()
            product_code_safe = re.sub(r"[^\w-]", "-", product_code)
            base = filename[:-3]
            filename = f"{base}-{product_code_safe}.md"
            out_path = os.path.join(out_dir, filename)
            print(f"  ⚠ Collision — writing as: {filename}")

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"  ✓ {filename}")
        written += 1

    if not dry_run:
        print(f"\nDone — {written} file(s) written → {out_dir}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert Profitshare product CSV to Astro .md content files."
    )
    parser.add_argument("csv", help="Path to the Profitshare CSV file")
    parser.add_argument(
        "--out",
        default="./src/content/products",
        help="Output directory for .md files (default: ./src/content/products)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview output without writing files",
    )
    args = parser.parse_args()

    if not os.path.isfile(args.csv):
        print(f"Error: file not found — {args.csv}", file=sys.stderr)
        sys.exit(1)

    process(args.csv, args.out, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
