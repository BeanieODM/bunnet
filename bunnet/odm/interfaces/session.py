
from pymongo.client_session import ClientSession


class SessionMethods:
    """
    Session methods
    """

    def set_session(self, session: ClientSession | None = None):
        """
        Set pymongo session
        :param session: Optional[ClientSession] - pymongo session
        :return:
        """
        if session is not None:
            self.session: ClientSession | None = session
        return self
