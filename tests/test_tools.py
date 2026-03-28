from unittest.mock import MagicMock, patch
import pytest


@pytest.fixture(autouse=True)
def mock_bq_service():
    with patch("app.agent.tools.bq_service") as mock:
        yield mock


def test_get_traffic_volume_returns_formatted_string(mock_bq_service):
    mock_bq_service.get_traffic_volume.return_value = [
        {"traffic_source": "Search", "total_users": 5000},
        {"traffic_source": "Organic", "total_users": 3000},
    ]

    from app.agent.tools import get_traffic_volume

    result = get_traffic_volume.invoke({"days": 30})

    assert "Search" in result
    assert "5,000" in result
    assert "Traffic volume" in result


def test_get_traffic_volume_specific_channel(mock_bq_service):
    mock_bq_service.get_traffic_volume.return_value = [
        {"traffic_source": "Facebook", "total_users": 1500},
    ]

    from app.agent.tools import get_traffic_volume

    result = get_traffic_volume.invoke({"traffic_source": "Facebook", "days": 30})

    assert "Facebook" in result
    assert "1,500" in result


def test_get_traffic_volume_empty(mock_bq_service):
    mock_bq_service.get_traffic_volume.return_value = []

    from app.agent.tools import get_traffic_volume

    result = get_traffic_volume.invoke({"days": 30})

    assert "No traffic data found" in result


def test_get_revenue_by_channel_returns_formatted_string(mock_bq_service):
    mock_bq_service.get_revenue_by_channel.return_value = [
        {
            "traffic_source": "Search",
            "total_orders": 800,
            "total_revenue": 200767.50,
            "avg_order_value": 250.96,
        },
    ]

    from app.agent.tools import get_revenue_by_channel

    result = get_revenue_by_channel.invoke({"days": 30})

    assert "Search" in result
    assert "200,767.50" in result
    assert "Revenue by channel" in result


def test_get_channel_comparison_returns_formatted_string(mock_bq_service):
    mock_bq_service.get_channel_comparison.return_value = [
        {
            "traffic_source": "Display",
            "total_users": 1000,
            "total_orders": 1024,
            "total_revenue": 97750.00,
            "conversion_rate_pct": 102.44,
            "revenue_per_user": 97.75,
        },
    ]

    from app.agent.tools import get_channel_comparison

    result = get_channel_comparison.invoke({"days": 30})

    assert "Display" in result
    assert "102.44%" in result
    assert "Channel comparison" in result


def test_get_channel_comparison_empty(mock_bq_service):
    mock_bq_service.get_channel_comparison.return_value = []

    from app.agent.tools import get_channel_comparison

    result = get_channel_comparison.invoke({"days": 30})

    assert "No comparison data found" in result
