from sqlmodel import Field
from typing import Optional

from gsuid_core.utils.database.base_models import BaseIDModel


class WikiBind(BaseIDModel, table=True):
    __table_args__ = {'extend_existing': True}
    # wiki对象映射关系
    name: Optional[str] = Field(default="", title="名称")
    value: Optional[str] = Field(default="", title="值")
    type: Optional[str] = Field(default="", title="类型")
    avatar: Optional[str] = Field(default="", title="头像")
    version: Optional[str] = Field(default="", title="版本")
