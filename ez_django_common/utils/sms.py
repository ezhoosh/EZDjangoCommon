from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from kavenegar import KavenegarAPI, APIException, HTTPException

from .loggers import logger

User = get_user_model()
kavehnegar_api = KavenegarAPI(settings.KAVENEGAR_API_KEY)


def activate_sms_verified(user):
    user.is_sms_verified = True
    user.save()


def send_validation_sms(phone_number, token):
    params = {
        "receptor": f"{phone_number}",
        "template": "verfiy-ezhoosh",
        "token": f"{str(token)}",
        "type": "sms",
    }
    try:
        kavehnegar_api.verify_lookup(params)
    except APIException as e:
        logger.error(e)
    except HTTPException as e:
        logger.error(e)


def send_notif_sms(phone_number, message):
    params = {
        "receptor": f"{phone_number}",
        "message": f"{message}",
    }
    response = kavehnegar_api.sms_send(params)
    logger.info(response)


def set_user_sms_token(phone, token, timeout=120):
    cache.set(phone, token, timeout=timeout)


def get_user_sms_token(phone):
    try:
        return cache.get(phone)
    except Exception:
        return None
