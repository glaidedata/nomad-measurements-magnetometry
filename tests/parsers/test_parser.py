import logging
from unittest.mock import MagicMock, patch

from nomad.datamodel import EntryArchive, EntryMetadata

from nomad_measurements_magnetometry.parsers.parser import (
    LakeShoreVSMParser,
    MicroMagAGMParser,
)
from nomad_measurements_magnetometry.schema_packages.schema_package import (
    ELNAlternatingGradientMagnetometry,
    ELNVibratingSampleMagnetometry,
    RawFileMagnetometryData,
)


@patch('nomad_measurements_magnetometry.parsers.parser.create_archive')
def test_lakeshore_vsm_parser(mock_create_archive):
    """Verify routing to the VSM schema via the Two-Archive pattern."""
    # 1. Setup Mock
    mock_create_archive.return_value = 'mocked_archive_reference'
    parser = LakeShoreVSMParser()

    archive = EntryArchive()
    archive.metadata = EntryMetadata()
    archive.m_context = MagicMock()

    # 2. Parse
    parser.parse('path/to/dummy_vsm.csv', archive, logging.getLogger())

    # 3. Assertions for the Two-Archive Placeholder
    assert isinstance(archive.data, RawFileMagnetometryData)
    assert archive.data.measurement.m_proxy_value == 'mocked_archive_reference'

    # Check that the correct ELN was created and linked
    mock_create_archive.assert_called_once()
    entry, _, archive_name = mock_create_archive.call_args[0]

    assert isinstance(entry, ELNVibratingSampleMagnetometry)
    assert entry.data_file == 'dummy_vsm.csv'
    assert archive_name == 'dummy_vsm.archive.json'


@patch('nomad_measurements_magnetometry.parsers.parser.create_archive')
def test_micromag_agm_parser(mock_create_archive):
    """Verify routing to the AGM schema via the Two-Archive pattern."""
    # 1. Setup Mock
    mock_create_archive.return_value = 'mocked_archive_reference'
    parser = MicroMagAGMParser()

    archive = EntryArchive()
    archive.metadata = EntryMetadata()
    archive.m_context = MagicMock()

    # 2. Parse
    parser.parse('path/to/dummy_agm.txt', archive, logging.getLogger())

    # 3. Assertions for the Two-Archive Placeholder
    assert isinstance(archive.data, RawFileMagnetometryData)
    assert archive.data.measurement.m_proxy_value == 'mocked_archive_reference'

    # Check that the correct ELN was created and linked
    mock_create_archive.assert_called_once()
    entry, _, archive_name = mock_create_archive.call_args[0]

    assert isinstance(entry, ELNAlternatingGradientMagnetometry)
    assert entry.data_file == 'dummy_agm.txt'
    assert archive_name == 'dummy_agm.archive.json'
