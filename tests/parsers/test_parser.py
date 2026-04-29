import contextlib
import logging
import os

from nomad.datamodel import EntryArchive, EntryMetadata

from nomad_measurements_magnetometry.parsers.parser import (
    LakeShoreVSMParser,
    MicroMagAGMParser,
)


# Get the path to the dummy data folder
def get_data_path(filename):
    return os.path.join(os.path.dirname(__file__), '..', 'data', filename)


class MockContext:
    """Mocks the NOMAD processing context to bypass the database lookup in tests."""

    @contextlib.contextmanager
    def raw_file(self, path, *args, **kwargs):
        class MockFile:
            name = get_data_path(path)

        yield MockFile()


def test_lakeshore_vsm_parser():
    # 1. Setup
    parser = LakeShoreVSMParser()
    archive = EntryArchive()

    # Inject mocked metadata and context
    archive.metadata = EntryMetadata(entry_name='dummy_vsm.csv')
    archive.m_context = MockContext()

    filepath = get_data_path('dummy_vsm.csv')

    # 2. Parse
    parser.parse(filepath, archive, logging.getLogger())

    # 3. Assertions
    assert archive.data is not None
    assert archive.data.m_def.name == 'ELNVibratingSampleMagnetometry'

    # Check that base schema inheritance works using a field we know the dummy has
    assert hasattr(archive.data, 'start_time')
    assert archive.data.measurement_type is not None

    # Check that subsections initialized correctly
    assert archive.data.sample_setup is not None
    assert archive.data.acquisition_setup is not None
    assert archive.data.field_configurations is not None

    # Check that results mapped cleanly
    assert len(archive.data.results) == 1
    assert archive.data.results[0].magnetic_field is not None
    assert archive.data.results[0].magnetic_moment is not None


def test_micromag_agm_parser():
    # 1. Setup
    parser = MicroMagAGMParser()
    archive = EntryArchive()

    # Inject mocked metadata and context
    archive.metadata = EntryMetadata(entry_name='dummy_agm.txt')
    archive.m_context = MockContext()

    filepath = get_data_path('dummy_agm.txt')

    # 2. Parse
    parser.parse(filepath, archive, logging.getLogger())

    # 3. Assertions
    assert archive.data is not None
    assert archive.data.m_def.name == 'ELNAlternatingGradientMagnetometry'

    # Check that base schema inheritance works
    assert hasattr(
        archive.data, 'start_time'
    )  # Prove the base property exists, even if None
    assert archive.data.instrument_model is not None

    # Check specific AGM subsections
    assert archive.data.instrument_setup is not None
    assert archive.data.settings is not None
    assert archive.data.processing is not None

    # Check results mapping
    assert len(archive.data.results) == 1
    assert archive.data.results[0].magnetic_field is not None
    assert archive.data.results[0].magnetic_moment is not None
