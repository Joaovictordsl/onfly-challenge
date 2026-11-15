"""Confere um relatório sem importar onfly_report ou reutilizar suas funções.

Usa frações racionais para dinheiro, ordinais para datas e arredondamento
half-up por divisão inteira. Não modifica os CSVs nem o relatório observado.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timedelta
from fractions import Fraction
from itertools import groupby
from pathlib import Path


def money(value: Fraction) -> str:
    sign = "-" if value < 0 else ""
    scaled = abs(value) * 100
    cents, remainder = divmod(scaled.numerator, scaled.denominator)
    cents += 2 * remainder >= scaled.denominator
    return f"{sign}{cents // 100}.{cents % 100:02d}"


def reference(input_path: Path, rates_path: Path, top: int) -> dict:
    with rates_path.open(encoding="utf-8", newline="") as handle:
        rates = {row["currency"]: Fraction(row["rate_to_brl"]) for row in csv.DictReader(handle)}
    with input_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    statuses = Counter(row["status"] for row in rows)
    billable = []
    for row in rows:
        if row["status"] == "CONFIRMED":
            checkin = datetime.strptime(row["checkin_date"], "%Y-%m-%d").toordinal()
            checkout = datetime.strptime(row["checkout_date"], "%Y-%m-%d").toordinal()
            billable.append({
                "month": row["checkin_date"][:7],
                "hotel_id": row["hotel_id"],
                "hotel_name": row["hotel_name"],
                "nights": (checkout - checkin) * int(row["rooms"]),
                "brl": Fraction(row["amount"]) * rates[row["currency"]],
            })

    months = []
    for month, group in groupby(sorted(billable, key=lambda row: row["month"]), key=lambda row: row["month"]):
        reservations = list(group)
        months.append({
            "month": month,
            "reservations": len(reservations),
            "room_nights": sum(row["nights"] for row in reservations),
            "total_brl": money(sum((row["brl"] for row in reservations), Fraction(0))),
        })

    hotels = []
    for hotel_id, group in groupby(sorted(billable, key=lambda row: row["hotel_id"]), key=lambda row: row["hotel_id"]):
        reservations = list(group)
        hotels.append({
            "hotel_id": hotel_id,
            "hotel_name": reservations[-1]["hotel_name"],
            "room_nights": sum(row["nights"] for row in reservations),
            "exact_brl": sum((row["brl"] for row in reservations), Fraction(0)),
        })
    # A ordem anterior por hotel_id é preservada nos empates desta ordenação estável.
    hotels.sort(key=lambda hotel: hotel["exact_brl"], reverse=True)
    ranking = [{"hotel_id": hotel["hotel_id"], "hotel_name": hotel["hotel_name"],
                "room_nights": hotel["room_nights"], "total_brl": money(hotel["exact_brl"])}
               for hotel in hotels[:top]]
    nights = sum(row["nights"] for row in billable)
    amount = sum((row["brl"] for row in billable), Fraction(0))
    return {
        "report_version": "1.0",
        "summary": {
            "total_reservations": len(rows),
            "confirmed_reservations": statuses["CONFIRMED"],
            "cancelled_reservations": statuses["CANCELLED"],
            "no_show_reservations": statuses["NO_SHOW"],
            "total_room_nights": nights,
            "total_amount_brl": money(amount),
            "average_nightly_rate_brl": money(amount / nights if nights else Fraction(0)),
        },
        "by_month": months,
        "top_hotels": ranking,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--rates", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--reference", required=True, type=Path)
    parser.add_argument("--comparison", required=True, type=Path)
    parser.add_argument("--top", type=int, default=5)
    args = parser.parse_args()
    expected = reference(args.input, args.rates, args.top)
    observed = json.loads(args.report.read_text(encoding="utf-8"))
    timestamp = datetime.fromisoformat(observed["generated_at"])
    comparison = {key: observed.get(key) == value for key, value in expected.items()}
    comparison["schema_raiz"] = set(observed) == set(expected) | {"generated_at"}
    comparison["offset_minus_03"] = timestamp.utcoffset() == timedelta(hours=-3)
    args.reference.write_text(json.dumps(expected, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.comparison.write_text(json.dumps(comparison, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"summary": expected["summary"], "comparacao": comparison}, indent=2))
    return 0 if all(comparison.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
