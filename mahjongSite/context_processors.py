from django.conf import settings
from ga4 import ga4_api

def google_analytics(request):
    """
    DEBUG=Falseの場合に、GoogleアナリティクスのトラッキングIDを返す
    """
    # GoogleアナリティクスのトラッキングIDをsettings.pyから取得する
    ga_tracking_id = getattr(settings, 'GOOGLE_ANALYTICS_TRACKING_ID', False)

    # DEBUG=FalseかつGoogleアナリティクスのトラッキングIDを取得できたら、
    # テンプレート内で'GOOGLE_ANALYTICS_TRACKING_ID'という変数を利用できるようにする
    if not settings.DEBUG and ga_tracking_id:
        return {
            'GOOGLE_ANALYTICS_TRACKING_ID': ga_tracking_id,
        }
    return {}

def user_num(request):
    return {'active_user_num': ga4_api.get_active_user_num(),
            'today_user_num': ga4_api.get_today_user_num(),
            'yesterday_user_num': ga4_api.get_yesterday_user_num(),}

