from pathlib import Path
from typing import TYPE_CHECKING

from nomad.datamodel.context import ServerContext
from nomad.parsing import MatchingParser

from nomad_measurements_magnetometry.schema_packages.vsm_schema import ELNVibratingSampleMagnetometry
from nomad_measurements_magnetometry.schema_packages.agm_schema import ELNAlternatingGradientMagnetometry

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import EntryArchive
    from structlog.stdlib import BoundLogger


class MagnetometryParser(MatchingParser):
    def is_mainfile(self, filename: str, mime: str, buffer: bytes, decoded_buffer: str, compression: str = None) -> bool:
        """
        Gatekeeper: Only returns True if the file contains VSM or AGM magic strings.
        """
        # 1. Standard regex check (handles the .csv and .txt extensions)
        is_valid_ext = super().is_mainfile(filename, mime, buffer, decoded_buffer, compression)
        if not is_valid_ext:
            return False

        # 2. Check for the actual headers found in your data files
        if decoded_buffer:
            # Lake Shore VSM signature
            if '#RUN ON SOFTWARE VERSION' in decoded_buffer:
                return True
            # MicroMag AGM signature
            if 'MicroMag 2900/3900 Data File' in decoded_buffer:
                return True

        return False

    def parse(
        self,
        mainfile: str,
        archive: 'EntryArchive',
        logger: 'BoundLogger' = None,
        child_archives=None,
    ) -> None:
        data_file = Path(mainfile).name
        if isinstance(archive.m_context, ServerContext):
            normalized_mainfile = mainfile.replace('\\', '/')
            if '/raw/' in normalized_mainfile:
                data_file = normalized_mainfile.split('/raw/', 1)[1]
            else:
                data_file = normalized_mainfile.rsplit('/', 1)[-1]

        # --- The Router Logic ---
        # Read the first chunk of the file to securely identify the signature
        with open(mainfile, 'r', encoding='utf-8', errors='ignore') as f:
            header_chunk = f.read(1024)

        if 'MicroMag 2900/3900 Data File' in header_chunk:
            entry = ELNAlternatingGradientMagnetometry()
        elif '#RUN ON SOFTWARE VERSION' in header_chunk:
            entry = ELNVibratingSampleMagnetometry()
        else:
            if logger:
                logger.error(f"Unrecognized file signature in {data_file}. No schema assigned.")
            return

        # Attach the file to the chosen schema
        entry.data_file = data_file
        archive.data = entry
        archive.metadata.entry_name = f'{data_file} data file'