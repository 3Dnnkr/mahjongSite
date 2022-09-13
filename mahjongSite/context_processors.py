from django.conf import settings
from ga4.ga4_api import get_active_user_num

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

def active_user_num(request):
    active_user_num = get_active_user_num()
    return {'active_user_num': active_user_num}