from nomad.config.models.plugins import ParserEntryPoint

class LakeShoreVSMParserEntryPoint(ParserEntryPoint):
    def load(self):
        from .parser import LakeShoreVSMParser

        return LakeShoreVSMParser(**self.dict())


class MicroMagAGMParserEntryPoint(ParserEntryPoint):
    def load(self):
        from .parser import MicroMagAGMParser

        return MicroMagAGMParser(**self.dict())


# VSM Entry Point
lakeshore_vsm_parser_entry_point = LakeShoreVSMParserEntryPoint(
    name='Lake Shore VSM Parser',
    description='Parser for Lake Shore VSM .csv data files.',
    mainfile_name_re=r'^.*\.csv$',
)

# AGM Entry Point
micromag_agm_parser_entry_point = MicroMagAGMParserEntryPoint(
    name='MicroMag AGM Parser',
    description='Parser for MicroMag AGM .txt data files.',
    mainfile_name_re=r'^.*\.txt$',
)