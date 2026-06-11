from nomad.datamodel.context import ServerContext
from nomad.datamodel.datamodel import EntryArchive
from nomad.parsing.parser import MatchingParser
from nomad_measurements.utils import create_archive

from nomad_measurements_magnetometry.schema_packages.schema_package import (
    ELNAlternatingGradientMagnetometry,
    ELNVibratingSampleMagnetometry,
    RawFileMagnetometryData,
)


class LakeShoreVSMParser(MatchingParser):
    def is_mainfile(
        self,
        filename: str,
        mime: str,
        buffer: bytes,
        decoded_buffer: str,
        compression: str = None,
    ) -> bool:
        """Gatekeeper for Lake Shore VSM .csv files."""
        if not super().is_mainfile(filename, mime, buffer, decoded_buffer, compression):
            return False

        # string check
        if decoded_buffer and '#RUN ON SOFTWARE VERSION' in decoded_buffer:
            return True

        return False

    def parse(
        self,
        mainfile: str,
        archive: EntryArchive,
        logger=None,
        child_archives=None,
    ) -> None:
        logger = logger or archive.m_context.logger

        # Extract the filename, handling server context paths correctly
        data_file = mainfile.rsplit('/', maxsplit=1)[-1]
        if isinstance(archive.m_context, ServerContext):
            data_file = mainfile.split('/raw/', 1)[1]

        # Instantiate the VSM schema
        entry = ELNVibratingSampleMagnetometry()
        entry.data_file = data_file

        # Create the separate editable .archive.json file to preserve ELN edits
        archive_name = f'{"".join(data_file.split(".")[:-1])}.archive.json'

        # Link the raw file to the generated ELN using the placeholder
        archive.data = RawFileMagnetometryData(
            measurement=create_archive(entry, archive, archive_name)
        )

        # Clean up the display name in the GUI
        archive.metadata.entry_name = f'{data_file} data file'


class MicroMagAGMParser(MatchingParser):
    def is_mainfile(
        self,
        filename: str,
        mime: str,
        buffer: bytes,
        decoded_buffer: str,
        compression: str = None,
    ) -> bool:
        """Gatekeeper for MicroMag AGM .txt files."""
        if not super().is_mainfile(filename, mime, buffer, decoded_buffer, compression):
            return False

        # string check
        if decoded_buffer and 'MicroMag 2900/3900 Data File' in decoded_buffer:
            return True

        return False

    def parse(
        self,
        mainfile: str,
        archive: EntryArchive,
        logger=None,
        child_archives=None,
    ) -> None:
        logger = logger or archive.m_context.logger

        # Extract the filename, handling server context paths correctly
        data_file = mainfile.rsplit('/', maxsplit=1)[-1]
        if isinstance(archive.m_context, ServerContext):
            data_file = mainfile.split('/raw/', 1)[1]

        # Instantiate the AGM schema
        entry = ELNAlternatingGradientMagnetometry()
        entry.data_file = data_file

        # Create the separate editable .archive.json file to preserve ELN edits
        archive_name = f'{"".join(data_file.split(".")[:-1])}.archive.json'

        # Link the raw file to the generated ELN using the placeholder
        archive.data = RawFileMagnetometryData(
            measurement=create_archive(entry, archive, archive_name)
        )

        # Clean up the display name in the GUI
        archive.metadata.entry_name = f'{data_file} data file'
