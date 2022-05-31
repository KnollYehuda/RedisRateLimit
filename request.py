from enum import Enum


class ARequest:
    class RequestMethod(Enum):
        USER_ID = 1
        IP = 2

    def __init__(self, method: RequestMethod):
        self.__method = method
        self.__value = None

    def __str__(self):
        return f"limit${'ip' if self.__method == ARequest.RequestMethod.IP else 'user_id'}${self.__value.replace('.', '-')}"

    def set_value(self, value):
        self.__value = str(value)

    def get_value(self):
        return self.__value

    def get_method(self):
        return self.__method
