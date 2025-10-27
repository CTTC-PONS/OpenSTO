from sqlmodel import Session
from src.control.controller import MirroringRequest
from src.decision_engine.topology import TopologyManager


class DecisionEngine:
    topology_manager = TopologyManager

    @classmethod
    def get_mirroring_info(cls, session: Session) -> MirroringRequest:
        return cls.topology_manager.get_mirroring_device_endpoints(session)
