from aiogram.types import Message
from datetime import datetime


class SendingMessages:
    def __init__(self, message: Message) -> None:
        self.message = message

    def start(self) -> str:
        return "Здравствуйте введите наименование заведения: "

    def registration_success(self, custom_phrase) -> str:
        return (
            f"Привет: {self.message.from_user.full_name}!\n"
            f"Вы успешно зарегистрировали заведение: <b>{custom_phrase}</b>"
        )

    def enter_success(self, custom_phrase) -> str:
        return (
            f"Привет: {self.message.from_user.full_name}!\n"
            f"Ваше заведение: <b>{custom_phrase}</b>"
        )

    def enter_fail(self) -> str:
        return (
            f"Привет: {self.message.from_user.full_name}!\n"
            f"Ваше заведение не зарегистрировано\n"
            f"Введите наименование заведения:"
        )

    def restart(self) -> str:
        return (
            f"Заведение <b>{self.message.text}</b> не зарегистрировано!\n"
            "Чтобы начать сначала нажмите /start"
        )

    def customer(self, custom_phrase) -> str:
        return (
            f"Привет: {self.message.from_user.full_name}!\n"
            f"Ваше заведение {custom_phrase}"
        )

    def customer_not_exist(self, custom_phrase) -> str:
        return (
            f"Привет: {self.message.from_user.full_name}!\n"
            f"Заведение <b>{custom_phrase}</b> не зарегистрировано\n"
            f"Чтобы начать сначала нажмите /start"
        )

    def admin_start(self) -> str:
        return "Здравствуйте, Admin!"

    def choose_action(self) -> str:
        return "Выберите действие:"

    def cancel(self) -> str:
        return "Действие отменено\n Чтобы начать сначала нажмите /start"

    def delivery_for_today(self, custom_phrase) -> str:
        return f"Доставки для {custom_phrase} на сегодня: <b>{datetime.now().strftime('%d.%m.%Y')}</b>"

    def not_delivery_for_today(self, custom_phrase) -> str:
        return f"<b>Нет</b> доставок для {custom_phrase} на сегодня: {datetime.now().strftime('%d.%m.%Y')}"

    def delivery_for_customer_success(self) -> str:
        return f"Заказ доставлен"

    def delivery_allready_delivered(self) -> str:
        return f"Заказ уже доставлен"


def sending_messages(message: Message, custom_phrase: str | None = None):
    messages = {
        "start": SendingMessages(message).start(),
        "registration_success": SendingMessages(message).registration_success(
            custom_phrase
        ),
        "enter_success": SendingMessages(message).enter_success(custom_phrase),
        "enter_fail": SendingMessages(message).enter_fail(),
        "restart": SendingMessages(message).restart(),
        "customer": SendingMessages(message).customer(custom_phrase),
        "customer_not_exist": SendingMessages(message).customer_not_exist(
            custom_phrase
        ),
        "admin_start": SendingMessages(message).admin_start(),
        "choose_action": SendingMessages(message).choose_action(),
        "cancel": SendingMessages(message).cancel(),
        "delivery_for_today": SendingMessages(message).delivery_for_today(
            custom_phrase
        ),
        "not_delivery_for_today": SendingMessages(message).not_delivery_for_today(
            custom_phrase
        ),
        "delivery_for_customer_success": SendingMessages(
            message
        ).delivery_for_customer_success(),
        "delivery_allready_delivered": SendingMessages(
            message
        ).delivery_allready_delivered(),
    }
    return messages
