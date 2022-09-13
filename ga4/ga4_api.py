from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import Dimension
from google.analytics.data_v1beta.types import Metric
from google.analytics.data_v1beta.types import RunRealtimeReportRequest
import os
from django.conf import settings



def get_active_user_num():
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = settings.BASE_DIR + '/ga4/client_secrets.json'
    property_id = "331574379"
    client = BetaAnalyticsDataClient()

    request = RunRealtimeReportRequest(
        property=f"properties/{property_id}",
        metrics=[Metric(name="activeUsers")],
    )
    response = client.run_realtime_report(request)

    return response.rows[0].metric_values[0].value



