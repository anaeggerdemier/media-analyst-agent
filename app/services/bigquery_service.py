import logging
from google.cloud import bigquery
from google.api_core.exceptions import GoogleAPIError
from google.oauth2 import service_account

logger = logging.getLogger(__name__)

DATASET = "bigquery-public-data.thelook_ecommerce"


class BigQueryService:
    def __init__(self, project_id: str, credentials_path: str):
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=["https://www.googleapis.com/auth/bigquery"],
        )
        self.client = bigquery.Client(project=project_id, credentials=credentials)

    def run_query(
        self, query: str, params: list[bigquery.ScalarQueryParameter] | None = None
    ) -> list[dict]:
        try:
            job_config = bigquery.QueryJobConfig(query_parameters=params or [])
            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()
            return [dict(row) for row in results]
        except GoogleAPIError as e:
            logger.error(f"BigQuery error: {e}")
            raise

    def get_traffic_volume(self, traffic_source: str | None, days: int) -> list[dict]:
        query = f"""
            SELECT
                traffic_source,
                COUNT(*) AS total_users
            FROM `{DATASET}.users`
            WHERE DATE(created_at) >= DATE_SUB(CURRENT_DATE(), INTERVAL @days DAY)
            {" AND traffic_source = @traffic_source" if traffic_source else ""}
            GROUP BY traffic_source
            ORDER BY total_users DESC
        """
        params = [bigquery.ScalarQueryParameter("days", "INT64", days)]
        if traffic_source:
            params.append(
                bigquery.ScalarQueryParameter(
                    "traffic_source", "STRING", traffic_source
                )
            )
        return self.run_query(query, params)

    def get_revenue_by_channel(self, days: int) -> list[dict]:
        query = f"""
            SELECT
                u.traffic_source,
                COUNT(DISTINCT o.order_id) AS total_orders,
                ROUND(SUM(oi.sale_price), 2) AS total_revenue,
                ROUND(SUM(oi.sale_price) / COUNT(DISTINCT o.order_id), 2) AS avg_order_value
            FROM `{DATASET}.users` u
            INNER JOIN `{DATASET}.orders` o ON u.id = o.user_id
            INNER JOIN `{DATASET}.order_items` oi ON o.order_id = oi.order_id
            WHERE DATE(o.created_at) >= DATE_SUB(CURRENT_DATE(), INTERVAL @days DAY)
                AND o.status NOT IN ('Cancelled', 'Returned')
            GROUP BY u.traffic_source
            ORDER BY total_revenue DESC
        """
        params = [bigquery.ScalarQueryParameter("days", "INT64", days)]
        return self.run_query(query, params)

    def get_channel_comparison(self, days: int) -> list[dict]:
        query = f"""
            SELECT
                u.traffic_source,
                COUNT(DISTINCT u.id) AS total_users,
                COUNT(DISTINCT o.order_id) AS total_orders,
                ROUND(SUM(oi.sale_price), 2) AS total_revenue,
                ROUND(COUNT(DISTINCT CASE WHEN o.order_id IS NOT NULL THEN u.id END) / COUNT(DISTINCT u.id) * 100, 2) AS conversion_rate_pct,
                ROUND(SUM(oi.sale_price) / COUNT(DISTINCT u.id), 2) AS revenue_per_user
            FROM `{DATASET}.users` u
            LEFT JOIN `{DATASET}.orders` o ON u.id = o.user_id
                AND DATE(o.created_at) >= DATE_SUB(CURRENT_DATE(), INTERVAL @days DAY)
                AND o.status NOT IN ('Cancelled', 'Returned')
            LEFT JOIN `{DATASET}.order_items` oi ON o.order_id = oi.order_id
            GROUP BY u.traffic_source
            ORDER BY revenue_per_user DESC
        """
        params = [bigquery.ScalarQueryParameter("days", "INT64", days)]
        return self.run_query(query, params)
