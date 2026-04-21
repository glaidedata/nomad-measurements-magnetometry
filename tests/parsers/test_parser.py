import os

from nomad.client import normalize_all
from nomad.datamodel import EntryArchive, EntryMetadata
from nomad.datamodel.context import ClientContext

# CHANGED: Import your new unified parser
from nomad_measurements_magnetometry.parsers.parser import MagnetometryParser


def test_vsm_parsing_and_normalization():
    """Test that the parser correctly routes and processes Lake Shore VSM files."""
    test_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'dummy_vsm.csv')
    test_dir = os.path.dirname(test_file)

    archive = EntryArchive(metadata=EntryMetadata())
    archive.m_context = ClientContext(local_dir=test_dir)

    # CHANGED: Use the unified parser
    parser = MagnetometryParser()
    parser.parse(test_file, archive, None)

    normalize_all(archive)

    # Check that the VSM schema was applied
    assert archive.data.m_def.name == 'ELNVibratingSampleMagnetometry'
    assert archive.data.data_file == 'dummy_vsm.csv'

    assert archive.data.software_version == 'Version 1.4.2'
    assert archive.data.measurement_method == 'FORC'
    assert archive.data.sample_settings.mass.magnitude == 0.123  # noqa: PLR2004

    assert len(archive.data.results[0].magnetic_field) == 3  # noqa: PLR2004
    assert archive.data.results[0].magnetic_field[0] == 100.5  # noqa: PLR2004
    assert archive.data.results[0].moment_status[0] == 'OK'


def test_agm_parsing_and_normalization():
    """Test that the parser correctly routes and processes MicroMag AGM files."""
    test_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'dummy_agm.txt')
    test_dir = os.path.dirname(test_file)

    archive = EntryArchive(metadata=EntryMetadata())
    archive.m_context = ClientContext(local_dir=test_dir)

    # Run the unified parser
    parser = MagnetometryParser()
    parser.parse(test_file, archive, None)

    normalize_all(archive)

    # Check that the correct AGM schema was automatically routed and applied
    assert archive.data.m_def.name == 'ELNAlternatingGradientMagnetometry'
    assert archive.data.data_file == 'dummy_agm.txt'

    # Check metadata mapping from the schema
    assert archive.data.instrument_model == 'MicroMag 2900/3900'
    assert archive.data.data_format_version == '0016.002'
    assert archive.data.measurement_mode == 'Multiple segments'

    # Check nested subsections
    assert archive.data.settings.operating_frequency == 406.5  # noqa: PLR2004
    assert archive.data.script.number_of_segments == 7  # noqa: PLR2004
    assert len(archive.data.script.segments) == 7  # noqa: PLR2004

    # Check physical units/magnitudes
    assert archive.data.script.segments[0].final_field == 5000.0  # noqa: PLR2004

    # Check data arrays mapping
    res = archive.data.results[0]
    assert len(res.magnetic_field) == 3  # noqa: PLR2004
    assert res.magnetic_field[0] == 5005.130  # noqa: PLR2004
    assert res.normalized_moment[0] == 0.9983703  # noqa: PLR2004
