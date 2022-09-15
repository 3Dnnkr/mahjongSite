from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import Dimension, Metric, DateRange
from google.analytics.data_v1beta.types import RunRealtimeReportRequest, RunReportRequest
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
    
def get_today_user_num():
    property_id = os.environ.get('PROPERTY_ID')
    client = BetaAnalyticsDataClient()
    request = RunReportRequest(
        property=f"properties/{property_id}",
        metrics=[Metric(name="activeUsers")],
        date_ranges=[DateRange(start_date="today", end_date="today")],
    )
    response = client.run_report(request)
    return sum([int(mv.value) for row in response.rows for mv in row.metric_values])

def get_yesterday_user_num():
    property_id = os.environ.get('PROPERTY_ID')
    client = BetaAnalyticsDataClient()
    request = RunReportRequest(
        property=f"properties/{property_id}",
        metrics=[Metric(name="activeUsers")],
        date_ranges=[DateRange(start_date="yesterday", end_date="yesterday")],
    )
    response = client.run_report(request)
    return sum([int(mv.value) for row in response.rows for mv in row.metric_values])

def get_total_user_num():
    return 0