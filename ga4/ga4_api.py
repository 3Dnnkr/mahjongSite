from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import Dimension
from google.analytics.data_v1beta.types import Metric
from google.analytics.data_v1beta.types import RunRealtimeReportRequest
import os


def get_active_user_num(): 
    property_id = os.environ.get('PROPERTY_ID')
    client = BetaAnalyticsDataClient()

    request = RunRealtimeReportRequest(
        property=f"properties/{property_id}",
        metrics=[Metric(name="activeUsers")],
    )
    response = client.run_realtime_report(request)
    return sum([int(mv.value) for row in response.rows for mv in row.metric_values])
    


