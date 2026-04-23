from nomad.config.models.plugins import SchemaPackageEntryPoint

class MagnetometrySchemaEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from .schema_package import m_package
        return m_package

magnetometry_schema_entry_point = MagnetometrySchemaEntryPoint(
    name='Magnetometry Schema',
    description='Unified schema for Magnetometry (VSM and AGM) data.',
)