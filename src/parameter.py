from dataclasses import dataclass

from dataclasses_json import DataClassJsonMixin


@dataclass(frozen=True)
class GlyphShape(DataClassJsonMixin):
    ascent: int
    descent: int
    half_width: int
    full_width: int


@dataclass(frozen=True)
class BaseConfig(DataClassJsonMixin):
    source: str
    shape_as: GlyphShape


@dataclass(frozen=True)
class HackConfig(BaseConfig):
    m_cutoff: int
    dot_zero: bool
    broken_vline: bool


@dataclass(frozen=True)
class BizudConfig(BaseConfig):
    visualize_zenkaku_space: bool
    baseline_shift: float
    weight: float


@dataclass(frozen=True)
class NerdConfig(BaseConfig):
    pass


@dataclass(frozen=True)
class Parameter(DataClassJsonMixin):
    family_name: str
    style_name: str
    weight_name: str
    shape_to: GlyphShape
    skew: float
    upos: int
    os2_table: dict
    hack: HackConfig
    bizud: BizudConfig
    nerd: NerdConfig
