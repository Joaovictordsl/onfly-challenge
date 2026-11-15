"""Regressões para leitura completa e agregação somente de confirmadas."""

import pytest
from helpers import run_cli


@pytest.mark.parametrize("reservation_count", [201, 300, 303])
def test_cli_reads_every_reservation(tmp_path, reservation_count):
    statuses = ("CONFIRMED", "CANCELLED", "NO_SHOW")
    rows = [
        {"reservation_id": f"R-{index}", "status": statuses[index % 3]}
        for index in range(reservation_count)
    ]

    report = run_cli(tmp_path, rows)
    per_status = reservation_count // 3

    assert report["summary"] == {
        "total_reservations": reservation_count,
        "confirmed_reservations": per_status,
        "cancelled_reservations": per_status,
        "no_show_reservations": per_status,
        "total_room_nights": per_status,
        "total_amount_brl": f"{per_status * 100}.00",
        "average_nightly_rate_brl": "100.00",
    }


def test_only_confirmed_reservations_feed_all_aggregates(tmp_path):
    report = run_cli(
        tmp_path,
        [
            {
                "reservation_id": "CONFIRMED-1",
                "checkin_date": "2025-01-10",
                "checkout_date": "2025-01-13",
                "rooms": "2",
            },
            {
                "reservation_id": "CANCELLED-1",
                "status": "CANCELLED",
                "hotel_id": "H02",
                "checkin_date": "2025-02-10",
                "checkout_date": "2025-02-13",
                "amount": "900.00",
            },
            {
                "reservation_id": "NO-SHOW-1",
                "status": "NO_SHOW",
                "hotel_id": "H03",
                "checkin_date": "2025-03-10",
                "checkout_date": "2025-03-13",
                "amount": "800.00",
            },
        ],
    )

    assert report["summary"] == {
        "total_reservations": 3,
        "confirmed_reservations": 1,
        "cancelled_reservations": 1,
        "no_show_reservations": 1,
        "total_room_nights": 6,
        "total_amount_brl": "100.00",
        "average_nightly_rate_brl": "16.67",
    }
    assert report["by_month"] == [
        {"month": "2025-01", "reservations": 1, "room_nights": 6, "total_brl": "100.00"}
    ]
    assert report["top_hotels"] == [
        {"hotel_id": "H01", "hotel_name": "Hotel Teste", "room_nights": 6, "total_brl": "100.00"}
    ]
