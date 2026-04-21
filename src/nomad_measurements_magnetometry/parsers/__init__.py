from nomad.config.models.plugins import ParserEntryPoint

class MagnetometryParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_measurements_magnetometry.parsers.parser import MagnetometryParser
        return MagnetometryParser(**self.model_dump())

parser_entry_point = MagnetometryParserEntryPoint(
    name='Magnetometry Parser',
    description='Parser for Magnetometry raw files (VSM, AGM, etc.).',
    mainfile_name_re=r'^.*\.(csv|txt)$',
    mainfile_mime_re='text/.*',
)