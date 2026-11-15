"""Regressões para ranking por total exato, desempate e limite do CLI."""

import pytest
from helpers import run_cli


@pytest.mark.parametrize(
    ("top", "expected_ids"),
    [(1, ["H03"]), (2, ["H03", "H01"]), (10, ["H03", "H01", "H02"])],
)
def test_ranking_breaks_equal_brl_totals_by_hotel_id(tmp_path, top, expected_ids):
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "hotel_id": "H02", "currency": "USD", "amount": "100.00"},
            {"reservation_id": "R-2", "hotel_id": "H01", "amount": "500.00"},
            {"reservation_id": "R-3", "hotel_id": "H03", "amount": "600.00"},
            {"reservation_id": "R-4", "hotel_id": "H01", "amount": "42.00"},
        ],
        top=top,
    )

    expected_amounts = {"H01": "542.00", "H02": "542.00", "H03": "600.00"}
    assert [hotel["hotel_id"] for hotel in report["top_hotels"]] == expected_ids
    assert [hotel["total_brl"] for hotel in report["top_hotels"]] == [
        expected_amounts[hotel_id] for hotel_id in expected_ids
    ]


@pytest.mark.parametrize("top", [1, 2])
def test_ranking_uses_exact_totals_before_rounding(tmp_path, top):
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "hotel_id": "H01", "amount": "1.001"},
            {"reservation_id": "R-2", "hotel_id": "H02", "amount": "1.004"},
        ],
        top=top,
    )

    assert [hotel["hotel_id"] for hotel in report["top_hotels"]] == ["H02", "H01"][:top]
    assert [hotel["total_brl"] for hotel in report["top_hotels"]] == ["1.00"] * top
