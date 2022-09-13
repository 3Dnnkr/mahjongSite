from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import Dimension
from google.analytics.data_v1beta.types import Metric
from google.analytics.data_v1beta.types import RunRealtimeReportRequest
import os

from mahjongSite.settings import BASE_DIR
from django.conf import settings
from django.templatetags.static import static


def get_active_user_num():
    os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', os.path.join(settings.BASE_DIR, static('json/client_secrets.json')))
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = BASE_DIR + static('json/client_secrets.json')
    #os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = settings.BASE_DIR + static('json/client_secrets.json')
    # property_id = "331574379"
    # client = BetaAnalyticsDataClient()

    # request = RunRealtimeReportRequest(
    #     property=f"properties/{property_id}",
    #     metrics=[Metric(name="activeUsers")],
    # )
    # response = client.run_realtime_report(request)
    # return response
    #return sum([v for row in response.rows for v in row.metric_values])

    return os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')



