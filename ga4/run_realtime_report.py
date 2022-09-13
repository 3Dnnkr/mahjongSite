from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import Dimension
from google.analytics.data_v1beta.types import Metric
from google.analytics.data_v1beta.types import RunRealtimeReportRequest
from run_report import print_run_report_response
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'client_secrets.json'



def run_sample():
    """Runs the sample."""
    # TODO(developer): Replace this variable with your Google Analytics 4
    #  property ID before running the sample.
    property_id = "331574379"
    run_realtime_report(property_id)


def run_realtime_report(property_id="YOUR-GA4-PROPERTY-ID"):
    """Runs a realtime report on a Google Analytics 4 property."""
    client = BetaAnalyticsDataClient()

    request = RunRealtimeReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name="city")],
        metrics=[Metric(name="activeUsers")],
    )
    response = client.run_realtime_report(request)
    print_run_report_response(response)
    


if __name__ == '__main__':
    run_sample()