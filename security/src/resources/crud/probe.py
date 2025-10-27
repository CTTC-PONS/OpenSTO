from sqlmodel import Session, select
from src.exceptions import ProbeNotFoundError
from src.resources.models.probe import Probe, ProbeCreate, ProbeGet


def create_probe(probe: ProbeCreate, session: Session) -> ProbeGet:
    probe = Probe.model_validate(probe)
    session.add(probe)
    session.commit()
    session.refresh(probe)
    return ProbeGet.model_validate(probe)


def delete_probe(probe_id: str, session: Session) -> ProbeGet:
    statement = select(Probe).where(Probe.id == probe_id)
    probes = session.exec(statement)
    probe = probes.first()
    if not probe:
        raise ProbeNotFoundError
    session.delete(probe)
    session.commit()
    return ProbeGet.model_validate(probe)


def get_probe(session: Session) -> ProbeGet:
    statement = select(Probe)
    probes = session.exec(statement)
    probe = probes.first()
    if not probe:
        raise ProbeNotFoundError
    return ProbeGet.model_validate(probe)
