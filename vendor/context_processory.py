
from .models import Vendor
from decouple import config 

from django.conf import settings
def getVendor(request):
    user=request.user
    try:
        vendor=Vendor.objects.get(user=user)
    except:
        vendor=None

    return {'vendor':vendor}

def getGoogleApi(request):
    return {'GOOGLE_API_KEY':settings.GOOGLE_API_KEY}

def paypal_client_id(request):
    PAYPAL_CLIENT_ID=config('PAYPAL_CLIENT_ID')
    return {'PAYPAL_CLIENT_ID':PAYPAL_CLIENT_ID}
