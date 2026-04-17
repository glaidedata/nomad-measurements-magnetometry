import os

from nomad.client import normalize_all
from nomad.datamodel import EntryArchive, EntryMetadata
from nomad.datamodel.context import ClientContext

from nomad_measurements_magnetometry.parsers.parser import VSMParser


def test_vsm_parsing_and_normalization():
    # 1. Locate the dummy file and its folder
    test_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'dummy_vsm.csv')
    test_dir = os.path.dirname(test_file)

    # 2. Initialize an empty archive WITH metadata
    archive = EntryArchive(metadata=EntryMetadata())

    # 3. Attach a testing context so archive.m_context.raw_file() can find the file!
    archive.m_context = ClientContext(local_dir=test_dir)

    # 4. Initialize and run the parser directly
    parser = VSMParser()
    parser.parse(test_file, archive, None)

    # 5. Run NOMAD's normalizer
    normalize_all(archive)

    # 6. Check that the correct schema was applied
    assert archive.data.m_def.name == 'ELNVibratingSampleMagnetometry'
    assert archive.data.data_file == 'dummy_vsm.csv'

    # 7. Check that the schema's normalize function successfully mapped the metadata
    assert archive.data.software_version == 'Version 1.4.2'
    assert archive.data.measurement_method == 'FORC'
    assert archive.data.sample_settings.mass.magnitude == 0.123  # noqa: PLR2004

    # 8. Check that the data arrays were successfully mapped into the Results section
    assert len(archive.data.results[0].magnetic_field) == 3  # noqa: PLR2004
    assert archive.data.results[0].magnetic_field[0] == 100.5  # noqa: PLR2004
    assert archive.data.results[0].moment_status[0] == 'OK'
