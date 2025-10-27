from sqlmodel import SQLModel

from .vertical_ns import NSInfoGet
from .wim import WIMServiceInfoGet


class ManoWimServiceInfo(SQLModel):
    mano_service_info: NSInfoGet | None
    wim_service_info: WIMServiceInfoGet | None
