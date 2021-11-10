class EmptyResponse(Exception):
    def __init__(self, message="Empty response at MongoDB"):
        super().__init__(message)
