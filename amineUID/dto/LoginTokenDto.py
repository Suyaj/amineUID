from typing import List


class DataObj:
    name: str
    token: str

class LoginTokenData:
    list: List[DataObj]

class LoginTokenDto:
    data: LoginTokenData
    message: str
    retcode: int
