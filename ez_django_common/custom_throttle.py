from rest_framework.throttling import UserRateThrottle


class SendOtpThrottle(UserRateThrottle):
    scope = "send_otp"
    rate = "100/min"
