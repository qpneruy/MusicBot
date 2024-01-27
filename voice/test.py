from fbchat import Client
from fbchat.models import *

cookies = {
    "sb": "1xc2ZT4SxHx7owHgpLe0GbpM",
    "fr": "1Rfy0JS9mocm1zJuc.AWUfn09J4OxJhD0cU7bdXjnmJFE.BltMEA.R1.AAA.0.0.BltMEc.AWVC1oKzAu0",
    "c_user": "61555738113140",
    "datr": "1xc2ZSuZuNAA_0n8jO0KbDpn",
    "xs": "12%3A2TeLzXf_k379Tw%3A2%3A1706344729%3A-1%3A15213"
}


class EchoBot(Client):
    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        self.markAsDelivered(thread_id, message_object.uid)
        self.markAsRead(thread_id)

        # Nếu bạn không gửi tin nhắn, hãy in nó ra console
        if author_id != self.uid:
            user = self.fetchUserInfo(author_id)[author_id]
            print("Tin nhắn từ {}: {}".format(user.name, message_object.text))


clienta = EchoBot("chiasefile0912@gmail.com", "01267879gG", session_cookies=cookies)
clienta.listen()

# clienta.send(Message(text="), "6956202157762920", thread_type=ThreadType.GROUP)
