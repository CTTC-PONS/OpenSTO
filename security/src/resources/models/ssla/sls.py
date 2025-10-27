from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


class SLO(SQLModel):
    id: str = Field(primary_key=True)
    name: str
    href: str
    conformanceComparator: str
    conformanceTarget: str
    conformancePeriod: dict
    graceTimes: str
    thresholdTarget: str
    toleranceTarget: str
    tolerancePeriod: dict
    serviceLevelObjectiveParameter: dict
    serviceLevelObjectiveConsequence: list
    relatedEntity: list


class SLSBase(SQLModel):
    id: str | None = Field(primary_key=True, default=None)
    name: str
    href: str | None = None
    description: str
    validFor: dict = Field(default_factory=dict, sa_column=Column(JSON))
    relatedServiceLevelObjective: list = Field(default_factory=list, sa_column=Column(JSON))

    @property
    def slos(self) -> list[SLO]:
        return [SLO.model_validate(slo) for slo in self.relatedServiceLevelObjective]


class SLSGet(SLSBase): ...


class SLSCreate(SLSBase): ...


class SLS(SLSBase): ...
