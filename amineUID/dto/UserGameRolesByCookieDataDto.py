from typing import List


class UserService:
    game_biz: str
    game_uid: str
    is_chosen: bool
    is_official: bool
    level: int
    nickname: str
    region: str
    region_name: str

class UserGameRolesByCookieData:
    list: List[UserService]

class UserGameRolesByCookieDataDto:
    data: UserGameRolesByCookieData
    message: str
    retcode: int
