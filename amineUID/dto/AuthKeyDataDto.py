class AuthKeyData:
    authkey: str
    authkey_ver: int
    sign_type: int

class AuthKeyDataDto:
    data: AuthKeyData
    message: str
    retcode: int

