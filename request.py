from enum import Enum


class ARequest:
    class RequestMethod(Enum):
        USER_ID = 1
        IP = 2

    def __init__(self, method: RequestMethod):
        self.__method = method
        self.__user_id = None
        self.__ip = None

    def __str__(self):
        if self.__method == ARequest.RequestMethod.IP:
            return f"limit$ip${self.__ip.replace('.', '-')}"
        return f"limit$user_id${self.__user_id}"

    def set_value(self, value):
        if self.__method == ARequest.RequestMethod.IP:
            self.__ip = str(value)
        else:
            self.__user_id = str(value)

    def get_value(self):
        if self.__method == ARequest.RequestMethod.IP:
            return self.__ip
        return self.__user_id

    def get_method(self):
        return self.__method
