class InvalidChsuId(Exception):
    def __init__(self, message="Chsu ID invalid"):
        super().__init__(message)


class InvalidApiKey(Exception):
    def __init__(self, message="Chsu API Key invalid"):
        super().__init__(message)
