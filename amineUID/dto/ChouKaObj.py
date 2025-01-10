from typing import List

class ListUrl:
    uid: str
    url: str

class ChouKaObj:
    code: int
    msg: str
    urlListObj: List[ListUrl]
