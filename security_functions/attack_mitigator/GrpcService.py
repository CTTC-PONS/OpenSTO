from typing import TYPE_CHECKING
from _common.GenericGrpcService import GenericGrpcService

if TYPE_CHECKING:
    from .Manager import Manager

class GrpcService(GenericGrpcService):
    def __init__(self, manager : 'Manager', cls_name : str = __name__) -> None:
        super().__init__(cls_name=cls_name)

    def install_servicers(self):
        pass
