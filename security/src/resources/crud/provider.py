import re

from sqlmodel import Session, select
from src.exceptions import InvalidNFVONameError, ProviderNotFoundError
from src.resources.models.provider import Provider, ProviderCreate, ProviderGet

DOMAIN_EXTRACTOR = r'^([a-zA-Z]*)\d+$'
DOMAIN_EXTRACTOR_RE = re.compile(DOMAIN_EXTRACTOR)


def get_domain_name_from_nfvo_ref(nfvo_ref: str) -> str:
    domain_match = DOMAIN_EXTRACTOR_RE.search(nfvo_ref)
    if not domain_match:
        raise InvalidNFVONameError(nfvo_ref)
    return domain_match.groups(0)[0].lower()


def create_provider(provider: ProviderCreate, session: Session) -> ProviderGet:
    domain = get_domain_name_from_nfvo_ref(provider.name)
    provider = Provider(**provider.model_dump(), domain=domain)
    session.add(provider)
    session.commit()
    session.refresh(provider)
    return ProviderGet.model_validate(provider)


def delete_provider(provider_name: str, session: Session) -> ProviderGet:
    statement = select(Provider).where(Provider.name == provider_name)
    providers = session.exec(statement)
    provider = providers.first()
    if not provider:
        raise ProviderNotFoundError
    session.delete(provider)
    session.commit()
    return ProviderGet.model_validate(provider)


def get_provider_by_id(provider_id: str, session: Session) -> ProviderGet:
    provider = session.get(Provider, provider_id)
    if not provider:
        raise ProviderNotFoundError
    return ProviderGet.model_validate(provider)


def get_provider(provider_name: str, session: Session) -> Provider:
    statement = select(Provider).where(Provider.name == provider_name)
    providers = session.exec(statement)
    provider = providers.first()
    if not provider:
        raise ProviderNotFoundError
    return provider


def get_all_providers(session: Session) -> list[Provider]:
    statement = select(Provider)
    providers = session.exec(statement)
    providers = providers.all()
    return list(providers)


def get_provider_with_domain_name(domain: str, session: Session) -> ProviderGet:
    statement = select(Provider).where(Provider.domain == domain)
    providers = session.exec(statement)
    provider = providers.first()
    if not provider:
        raise ProviderNotFoundError
    return ProviderGet.model_validate(provider)
