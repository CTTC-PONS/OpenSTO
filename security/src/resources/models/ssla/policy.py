from sqlmodel import SQLModel


class DomainRuleBase(SQLModel):
    name: str
    description: str
    condition: dict
    action: dict


class DomainPolicyBase(SQLModel):
    name: str
    rules: list[DomainRuleBase]
