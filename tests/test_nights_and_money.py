"""Regressões para datas completas e precisão financeira até a serialização."""

from decimal import Decimal

import pytest
from helpers import run_cli

from onfly_report.services.currency_converter import convert_to_brl


@pytest.mark.parametrize(
    ("checkin", "checkout", "rooms", "expected_nights"),
    [
        ("2025-01-30", "2025-02-02", "3", 9),
        ("2024-12-30", "2025-01-02", "2", 6),
        ("2024-02-28", "2024-03-01", "2", 4),
    ],
)
def test_room_nights_use_full_dates_and_rooms(tmp_path, checkin, checkout, rooms, expected_nights):
    report = run_cli(
        tmp_path,
        [{"checkin_date": checkin, "checkout_date": checkout, "rooms": rooms}],
    )

    assert report["summary"]["total_room_nights"] == expected_nights
    assert report["by_month"] == [
        {"month": checkin[:7], "reservations": 1, "room_nights": expected_nights, "total_brl": "100.00"}
    ]
    assert report["top_hotels"][0]["room_nights"] == expected_nights


@pytest.mark.parametrize(
    ("amount", "rate", "expected"),
    [
        ("0.01", "5.42", "0.0542"),
        ("9007199254740993.01", "1.000000", "9007199254740993.01"),
    ],
)
def test_conversion_preserves_decimal_precision(amount, rate, expected):
    result = convert_to_brl(Decimal(amount), "USD", {"USD": Decimal(rate)})

    assert isinstance(result, Decimal)
    assert result == Decimal(expected)


@pytest.mark.parametrize(
    ("currency", "amount", "expected_total", "expected_average"),
    [
        ("BRL", "1.005", "2.01", "1.01"),
        ("USD", "0.01", "0.11", "0.05"),
    ],
)
def test_money_rounds_half_up_only_after_aggregation(tmp_path, currency, amount, expected_total, expected_average):
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "currency": currency, "amount": amount},
            {"reservation_id": "R-2", "currency": currency, "amount": amount},
        ],
    )

    assert report["summary"]["total_amount_brl"] == expected_total
    assert report["summary"]["average_nightly_rate_brl"] == expected_average
    assert report["by_month"][0]["total_brl"] == expected_total
    assert report["top_hotels"][0]["total_brl"] == expected_total
