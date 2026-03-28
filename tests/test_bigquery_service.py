from unittest.mock import MagicMock, patch
import pytest
from app.services.bigquery_service import BigQueryService


@pytest.fixture
def bq_service():
    with patch(
        "app.services.bigquery_service.service_account.Credentials.from_service_account_file"
    ):
        with patch("app.services.bigquery_service.bigquery.Client"):
            service = BigQueryService(
                project_id="test-project",
                credentials_path="fake/path.json",
            )
            return service


def test_get_traffic_volume_all_channels(bq_service):
    bq_service.run_query = MagicMock(
        return_value=[
            {"traffic_source": "Search", "total_users": 5000},
            {"traffic_source": "Organic", "total_users": 3000},
            {"traffic_source": "Facebook", "total_users": 1500},
        ]
    )

    results = bq_service.get_traffic_volume(traffic_source=None, days=30)

    assert len(results) == 3
    assert results[0]["traffic_source"] == "Search"
    assert results[0]["total_users"] == 5000


def test_get_traffic_volume_specific_channel(bq_service):
    bq_service.run_query = MagicMock(
        return_value=[
            {"traffic_source": "Search", "total_users": 5000},
        ]
    )

    results = bq_service.get_traffic_volume(traffic_source="Search", days=30)

    assert len(results) == 1
    assert results[0]["traffic_source"] == "Search"


def test_get_revenue_by_channel(bq_service):
    bq_service.run_query = MagicMock(
        return_value=[
            {
                "traffic_source": "Search",
                "total_orders": 800,
                "total_revenue": 200767.50,
                "avg_order_value": 250.96,
            },
        ]
    )

    results = bq_service.get_revenue_by_channel(days=30)

    assert len(results) == 1
    assert results[0]["total_revenue"] == 200767.50
    assert results[0]["avg_order_value"] == 250.96


def test_get_channel_comparison(bq_service):
    bq_service.run_query = MagicMock(
        return_value=[
            {
                "traffic_source": "Display",
                "total_users": 1000,
                "total_orders": 1024,
                "total_revenue": 97750.00,
                "conversion_rate_pct": 4.2,
                "revenue_per_user": 97.75,
            },
        ]
    )

    results = bq_service.get_channel_comparison(days=30)

    assert len(results) == 1
    assert results[0]["traffic_source"] == "Display"
    assert results[0]["conversion_rate_pct"] == 4.2


def test_get_traffic_volume_empty_result(bq_service):
    bq_service.run_query = MagicMock(return_value=[])

    results = bq_service.get_traffic_volume(traffic_source="TikTok", days=30)

    assert results == []
