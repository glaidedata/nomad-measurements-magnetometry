from nomad_measurements_magnetometry.schema_packages.agm_schema import (
    ELNAlternatingGradientMagnetometry,
)
from nomad_measurements_magnetometry.schema_packages.vsm_schema import (
    ELNVibratingSampleMagnetometry,
)


def test_schema_instantiation():
    """Verify that both schemas can be instantiated successfully without import/syntax errors."""

    vsm_entry = ELNVibratingSampleMagnetometry()
    assert vsm_entry is not None
    assert vsm_entry.m_def.name == 'ELNVibratingSampleMagnetometry'

    agm_entry = ELNAlternatingGradientMagnetometry()
    assert agm_entry is not None
    assert agm_entry.m_def.name == 'ELNAlternatingGradientMagnetometry'
