from nomad.config.models.plugins import ParserEntryPoint


class NewParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_measurements_magnetometry.parsers.parser import VSMParser

        return VSMParser(**self.model_dump())


parser_entry_point = NewParserEntryPoint(
    name='VSM Parser',
    description='Parser for Vibrating Sample Magnetometry (VSM) raw files.',
    mainfile_name_re=r'^.*\.csv$',
    mainfile_mime_re='text/csv|text/plain',
)
