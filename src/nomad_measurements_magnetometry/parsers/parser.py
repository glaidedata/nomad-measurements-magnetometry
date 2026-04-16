from pathlib import Path
from typing import TYPE_CHECKING

from nomad.datamodel.context import ServerContext
from nomad.parsing import MatchingParser

from nomad_measurements_magnetometry.schema_packages.schema_package import (
    ELNVibratingSampleMagnetometry,
)

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import EntryArchive
    from structlog.stdlib import BoundLogger


class VSMParser(MatchingParser):
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

        entry = ELNVibratingSampleMagnetometry()
        entry.data_file = data_file
        archive.data = entry
        archive.metadata.entry_name = f'{data_file} data file'
