from nomad.datamodel.datamodel import EntryArchive
from nomad.parsing.parser import MatchingParser

from nomad_measurements_magnetometry.schema_packages.schema_package import (
    ELNAlternatingGradientMagnetometry,
    ELNVibratingSampleMagnetometry,
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

        # Instantiate the VSM schema
        entry = ELNVibratingSampleMagnetometry()
        entry.data_file = mainfile.rsplit('/', maxsplit=1)[-1]

        archive.data = entry
        entry.normalize(archive, logger)


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

        # Instantiate the AGM schema
        entry = ELNAlternatingGradientMagnetometry()
        entry.data_file = mainfile.rsplit('/', maxsplit=1)[-1]

        archive.data = entry
        entry.normalize(archive, logger)
