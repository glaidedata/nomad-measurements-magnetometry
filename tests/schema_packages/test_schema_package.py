from nomad.datamodel import EntryArchive

from nomad_measurements_magnetometry.schema_packages.schema_package import (
    ELNAlternatingGradientMagnetometry,
    ELNVibratingSampleMagnetometry,
    MagnetometryResult,
    MagnetometrySample,
)


def test_vsm_schema_instantiation():
    """Test that the VSM schema correctly inherits BaseMagnetometry properties."""
    archive = EntryArchive()
    entry = ELNVibratingSampleMagnetometry()

    # Test Base properties
    entry.measurement_type = 'Hysteresis'
    entry.software_version = '1.0.0'

    # Test Base Subsections
    sample = MagnetometrySample(mass=0.5, volume=1.2)
    entry.sample_setup = sample

    res = MagnetometryResult(magnetic_field=[1.0, 2.0], magnetic_moment=[0.1, 0.2])
    entry.results = [res]

    archive.data = entry

    # Assertions
    assert archive.data.measurement_type == 'Hysteresis'
    MASS_MAGNITUDE = 0.5
    assert archive.data.sample_setup.mass.magnitude == MASS_MAGNITUDE
    MAGNETIC_FIELD_LENGTH = 2
    assert len(archive.data.results[0].magnetic_field) == MAGNETIC_FIELD_LENGTH


def test_agm_schema_instantiation():
    """Test that the AGM schema correctly inherits BaseMagnetometry properties."""
    archive = EntryArchive()
    entry = ELNAlternatingGradientMagnetometry()

    # Test Base properties
    entry.instrument_model = 'MicroMag 2900'

    # Test AGM Specific properties
    entry.data_format_version = '2.0'
    entry.measurement_mode = 'Continuous'

    archive.data = entry

    # Assertions
    assert archive.data.instrument_model == 'MicroMag 2900'
    assert archive.data.data_format_version == '2.0'
    assert archive.data.measurement_mode == 'Continuous'
