from nomad.config.models.plugins import SchemaPackageEntryPoint


class NewSchemaPackageEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from nomad_measurements_magnetometry.schema_packages.schema_package import (
            m_package,
        )

        return m_package


schema_package_entry_point = NewSchemaPackageEntryPoint(
    name='Magnetometry Schema',
    description='Schema for Magnetometry (VSM, etc) data.',
)
