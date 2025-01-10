class NoticeInfo:
    def __init__(self):
        pass

class AccountInfo:
    account_id: int
    create_time: int
    email: str
    identity_code: str
    is_adult: int
    is_email_verify: int
    real_name: str
    safe_area_code: str
    safe_level: int
    safe_mobile: str
    weblogin_token: str

class Data:
    account_info: AccountInfo
    game_ctrl_info: any
    msg: str
    notice_info: NoticeInfo
    status: int

class LoginCookieDataDto:
    code: int
    data: Data
