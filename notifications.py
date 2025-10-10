from kavenegar import APIException, HTTPException, KavenegarAPI

from config import settings

# class Email:
#     @staticmethod
#     def send_email(title, body, email):
#         EmailMessage(
#             subject=title,
#             body=body,
#             from_email=settings.DEFAULT_EMAIL,
#             to=[email, ],
#         ).send()
#
#     @staticmethod
#     def send_active_search_result(subject, url, to):
#         html_content = render_to_string(
#             'active_search_result_template.html', {'url': url}
#         )  # render with dynamic value
#         text_content = strip_tags(
#             html_content
#         )  # Strip the html tag. So people can see the pure text at least.
#         # create the email, and attach the HTML version as well.
#         msg = EmailMultiAlternatives(
#             subject,
#             text_content,
#             settings.DEFAULT_EMAIL,
#             [to, ]
#         )
#         msg.attach_alternative(html_content, "text/html")
#         msg.send()


# class PushNotification:
#
#     def __init__(self):
#         self.cred = credentials.Certificate("canso-5273b-firebase-adminsdk-7b93h-e34a03ce91.json")
#         firebase_admin.initialize_app(self.cred)
#
#     def send_notification(self, token: str, title: str, body: str, data: dict):
#         message = messaging.Message(
#             notification=messaging.Notification(
#                 title=title,
#                 body=body
#             ),
#             token=token,
#             android=messaging.AndroidConfig(
#                 notification=messaging.AndroidNotification(sound='True'),
#                 data=data
#             )
#         )
#         messaging.send(message)


class KavenegarSMS:
    def __init__(self):
        self.api = KavenegarAPI(settings.KAVENEGAR_API_KEY)

    def register(self, receptor=None, code=None):
        self.params = {
            "receptor": receptor,
            "template": "otp",
            "token": code,
            "type": "sms",
        }

    def confirm(self, receptor=None, code=None):
        self.params = {
            "receptor": receptor,
            "template": "veterinarian-confirm",
            "token": code,
            "type": "sms",
        }

    def reject(self, receptor=None, code=None):
        self.params = {
            "receptor": receptor,
            "template": "veterinarian-reject",
            "token": code,
            "type": "sms",
        }

    def vet_new_req(self, receptor=None, code=None):
        self.params = {
            "receptor": receptor,
            "template": "vet-new-req",
            "token": code,
            "type": "sms",
        }

    def rancher_new_req(self, receptor=None, code=None):
        self.params = {
            "receptor": receptor,
            "template": "request-new",
            "token": code,
            "type": "sms",
        }

    def confirm_rancher_req(self, receptor=None, code=None):
        self.params = {
            "receptor": receptor,
            "template": "request-accepted",
            "token": code,
            "type": "sms",
        }

    def reject_rancher_req(self, receptor=None, code=None):
        self.params = {
            "receptor": receptor,
            "template": "request-rejected",
            "token": code,
            "type": "sms",
        }

    def visit_done(self, receptor=None, code=None):
        # اتمام کار دامپزشک و نظردهی دامدار
        self.params = {
            "receptor": receptor,
            "template": "visit-done",
            "token": code,
            "type": "sms",
        }

    def check_wallet(self, receptor=None, code=None):
        self.params = {
            "receptor": receptor,
            "template": "inform-wallet-balance",
            "token": code,
            "type": "sms",
        }

    def recharge_wallet(self, receptor=None, message=None):
        self.params = {
            "receptor": receptor,
            "template": "starbot-recharge-wallet",
            "token": message,
            "type": "sms",
        }

    def recharge_warning(self, receptor=None, message=None):
        # هشدار اتمام شارژ کیف پول
        self.params = {
            "receptor": receptor,
            "template": "starbot-recharge-warning",
            "token": message,
            "type": "sms",
        }

    def notify_NewUser_for_admins(self, receptor=None, token=None):
        self.params = {
            "receptor": receptor,
            "template": "starbot-alertNewUser",
            "token": token,
            "type": "sms",
        }

    def notify_welcomeNewUser(self, receptor=None, token=None, token2=None):
        self.params = {
            "receptor": receptor,
            "template": "starbot-sendWelcomeMessage",
            "token": token,
            "token2": token2,
            "type": "sms",
        }

    def send(self):
        flag = True
        for i, j in self.params.items():
            if j is None:
                flag = False
        if flag:
            try:
                return self.api.verify_lookup(self.params)
            except APIException as e:
                return e
            except HTTPException as e:
                return e
        else:
            raise APIException
