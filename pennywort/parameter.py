from dataclasses import dataclass
from typing import Generic, Type, TypeVar

from dataclasses_json import DataClassJsonMixin
from dataclasses_json.core import Json


@dataclass(frozen=True)
class BaseConfig(DataClassJsonMixin):
    ascent: int
    descent: int


C = TypeVar("C", bound=BaseConfig)


@dataclass(frozen=True)
class HackConfig(BaseConfig):
    width: int
    skew: float
    m_cutoff: int


@dataclass(frozen=True)
class MgenplusConfig(BaseConfig):
    half_width: int
    full_width: int
    skew: float


@dataclass(frozen=True)
class NerdConfig(BaseConfig):
    width: int


@dataclass(frozen=True)
class FontData(DataClassJsonMixin, Generic[C]):
    source: str
    config: C

    @classmethod
    def from_dict_with_type(cls, data: dict, config_type: Type[C]) -> "FontData[C]":
        return cls(
            source=data["source"],
            config=config_type.from_dict(data["config"]),
        )


@dataclass(frozen=True)
class Parameter(DataClassJsonMixin):
    family_name: str
    style_name: str
    weight_name: str
    ascent: int
    descent: int
    upos: int
    os2_table: dict
    hack: FontData[HackConfig]
    mgenplus: FontData[MgenplusConfig]
    nerd: FontData[NerdConfig]

    @classmethod
    def from_dict(
        cls,
        kvs: Json,
        *,
        infer_missing: bool = False,
    ) -> "Parameter":
        if not isinstance(kvs, dict):
            raise ValueError

        hack = FontData.from_dict_with_type(kvs.pop("hack"), HackConfig)
        mgenplus = FontData.from_dict_with_type(kvs.pop("mgenplus"), MgenplusConfig)
        nerd = FontData.from_dict_with_type(kvs.pop("nerd"), NerdConfig)

        return cls(
            **{k: kvs[k] for k in kvs.keys() & cls.__dataclass_fields__.keys()},
            hack=hack,
            mgenplus=mgenplus,
            nerd=nerd,
        )
