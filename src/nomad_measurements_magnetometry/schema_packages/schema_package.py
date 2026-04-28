from typing import TYPE_CHECKING

import numpy as np
from nomad.datamodel.data import ArchiveSection, EntryData
from nomad.datamodel.metainfo.annotations import ELNAnnotation, ELNComponentEnum
from nomad.datamodel.metainfo.basesections import Measurement, MeasurementResult
from nomad.metainfo import Quantity, SchemaPackage, Section, SubSection
from readers_ientrance import read_lakeshore_vsm, read_micromag_agm

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import EntryArchive
    from structlog.stdlib import BoundLogger

m_package = SchemaPackage()

# Constants for Unit Conversion (CGS to SI)
OE_TO_AM = 1000.0 / (4.0 * np.pi)  # Oersted to A/m
EMU_TO_AM2 = 1e-3                  # emu to A*m^2
EMU_OE_TO_M3 = EMU_TO_AM2 / OE_TO_AM # emu/Oe to m^3

# ==========================================
# 1. BASE MAGNETOMETRY
# ==========================================
class MagnetometrySample(ArchiveSection):
    sample_id = Quantity(
        type=str, description='Unique identifier or name for the sample.'
    )
    mass = Quantity(type=np.float64, unit='g', description='Mass of the sample.')
    volume = Quantity(
        type=np.float64, unit='cm**3', description='Volume of the sample.'
    )
    area = Quantity(
        type=np.float64, unit='cm**2', description='Cross-sectional area of the sample.'
    )
    density = Quantity(
        type=np.float64, unit='g / cm**3', description='Density of the sample.'
    )
    thickness = Quantity(
        type=np.float64, unit='mm', description='Thickness of the sample.'
    )
    demagnetizing_factor = Quantity(
        type=np.float64,
        description='Generic or SI demagnetizing factor applied to correct the applied field.',
    )
    demagnetizing_factor_cgs = Quantity(
        type=np.float64,
        description='CGS demagnetizing factor applied to correct the applied field.',
    )


class MagnetometryResult(MeasurementResult):
    magnetic_field = Quantity(
        type=np.float64,
        shape=['*'],
        unit='A/m',
        description='Applied magnetic field array.',
    )
    magnetic_moment = Quantity(
        type=np.float64,
        shape=['*'],
        unit='A * m**2',
        description='Measured raw magnetic moment array.',
    )
    normalized_moment = Quantity(
        type=np.float64,
        shape=['*'],
        description='Magnetic moment array normalized by sample mass, volume, or saturation moment (dimensionless).',
    )
    time_stamp = Quantity(
        type=np.float64,
        shape=['*'],
        unit='s',
        description='Time elapsed since the start of the measurement for each data point.',
    )
    step_array = Quantity(
        type=np.int32,
        shape=['*'],
        description='Array representing the sequence steps of the measurement protocol.',
    )
    iteration_array = Quantity(
        type=np.int32,
        shape=['*'],
        description='Array representing iteration indices for repetitive loops in the protocol.',
    )
    segment_array = Quantity(
        type=np.int32,
        shape=['*'],
        description='Array representing the segment number for multi-segment measurements.',
    )
    field_status = Quantity(
        type=str,
        shape=['*'],
        description='Instrument status or error codes associated with the magnetic field output.',
    )
    moment_status = Quantity(
        type=str,
        shape=['*'],
        description='Instrument status or error codes associated with the moment acquisition.',
    )


class BaseMagnetometry(Measurement):
    instrument_model = Quantity(
        type=str, description='Make and model of the magnetometry instrument.'
    )
    software_version = Quantity(
        type=str, description='Software version used to run the measurement and export data.'
    )
    measurement_type = Quantity(
        type=str, description='General classification of the measurement (e.g., Hysteresis, FORC).'
    )
    start_time = Quantity(
        type=str, description='Timestamp when the measurement sequence began.'
    )
    finish_time = Quantity(
        type=str, description='Timestamp when the measurement sequence completed.'
    )

    sample_setup = SubSection(section_def=MagnetometrySample)
    results = SubSection(section_def=MagnetometryResult, repeats=True)


# ==========================================
# 2. AGM SCHEMA
# ==========================================
# --- 1. AGM-Specific Subsections ---

class AGMInstrument(ArchiveSection):
    configuration = Quantity(
        type=str, description='Instrument configuration mode (e.g., AGM, VSM).'
    )
    temperature_control = Quantity(
        type=str, description='Type of temperature controller used during the run.'
    )
    hardware_version = Quantity(
        type=str, description='Hardware version of the MicroMag console.'
    )
    units_of_measure = Quantity(
        type=str, description='Base unit system used by the instrument (e.g., cgs, SI).'
    )
    temperature_in = Quantity(
        type=str, description='Temperature unit scale (e.g., Celsius, Kelvin).'
    )

class AGMSettings(ArchiveSection):
    field_range = Quantity(
        type=np.float64, unit='A/m', description='Maximum magnetic field range set for the measurement.'
    )
    field_command = Quantity(
        type=np.float64, unit='A/m', description='Commanded static field offset.'
    )
    moment_range = Quantity(
        type=np.float64, unit='A * m**2', description='Full-scale moment range setting for the amplifier.'
    )
    averaging_time = Quantity(
        type=np.float64, unit='s', description='Time spent integrating the signal for each data point.'
    )
    temperature_command = Quantity(
        type=np.float64, unit='celsius', description='Commanded setpoint temperature.'
    )
    tmprtr_difference_correction = Quantity(
        type=str, description='Whether a temperature difference correction calibration was applied.'
    )
    orientation = Quantity(
        type=str, description='Sample mounting orientation.'
    )
    gradient = Quantity(
        type=np.float64, description='Alternating gradient field magnitude.'
    )
    probe_factor = Quantity(
        type=np.float64, description='Calibration factor of the piezo probe.'
    )
    probe_q = Quantity(
        type=np.float64, description='Quality factor (Q) of the piezo probe resonance.'
    )
    probe_resonance = Quantity(
        type=np.float64, unit='Hz', description='Measured resonant frequency of the probe.'
    )
    operating_frequency = Quantity(
        type=np.float64, unit='Hz', description='Actual frequency used for the alternating gradient.'
    )
    sweep_mode = Quantity(
        type=str, description='Mode of field sweeping (e.g., Automatic, Continuous).'
    )

class AGMMeasurementDetails(ArchiveSection):
    description = Quantity(
        type=str,
        a_eln=dict(component=ELNComponentEnum.RichTextEditQuantity),
        description='Free-text notes or remarks left by the experimentalist.',
    )
    field_measured = Quantity(
        type=np.float64, unit='A/m', description='Measured static field prior to sequence start.'
    )
    temperature_measured = Quantity(
        type=np.float64, unit='celsius', description='Measured temperature prior to sequence start.'
    )
    averages_completed = Quantity(
        type=np.float64, description='Number of signal averages completed.'
    )
    elapsed_time = Quantity(
        type=np.float64, unit='s', description='Total elapsed time for the measurement.'
    )

class AGMProcessing(ArchiveSection):
    background_subtraction = Quantity(
        type=str, description='Indicates if empty probe background data was subtracted.'
    )
    delta_m_processing = Quantity(
        type=str, description='Indicates if Delta-M signal processing was used.'
    )
    demagnetizing_factor = Quantity(
        type=str, description='Indicates if demagnetizing correction was applied to the field.'
    )
    normalization = Quantity(
        type=str, description='Strategy used for normalizing the moment (e.g., by mass, by volume).'
    )
    normalization_factor = Quantity(
        type=np.float64, description='Scalar multiplier used to normalize the moment data.'
    )
    offset_field = Quantity(
        type=str, description='Indicates if a static field offset was applied.'
    )
    offset_moment = Quantity(
        type=str, description='Indicates if a static moment offset was subtracted.'
    )
    pole_saturation = Quantity(
        type=str, description='Indicates if pole saturation compensation was active.'
    )
    slope_correction = Quantity(
        type=str, description='Indicates if a high-field slope (paramagnetic/diamagnetic) was corrected.'
    )

class AGMViewport(ArchiveSection):
    left = Quantity(
        type=np.float64, unit='A/m', description='Left plot limit.'
    )
    right = Quantity(
        type=np.float64, unit='A/m', description='Right plot limit.'
    )
    bottom = Quantity(
        type=np.float64, unit='A * m**2', description='Bottom plot limit.'
    )
    top = Quantity(
        type=np.float64, unit='A * m**2', description='Top plot limit.'
    )
    show_x_axis = Quantity(
        type=str, description='Visibility state of the X-axis in the instrument software.'
    )
    show_y_axis = Quantity(
        type=str, description='Visibility state of the Y-axis in the instrument software.'
    )

class AGMCharacterization(ArchiveSection):
    initial_slope = Quantity(
        type=np.float64, unit='m**3', description='Initial magnetic susceptibility.'
    )
    saturation = Quantity(
        type=np.float64, unit='A * m**2', description='Saturation magnetization (Ms) extracted from the loop.'
    )
    remanence = Quantity(
        type=np.float64, unit='A * m**2', description='Remanent magnetization (Mr) extracted from the loop.'
    )
    coercivity = Quantity(
        type=np.float64, unit='A/m', description='Coercive field (Hc) extracted from the loop.'
    )
    s_star = Quantity(
        type=np.float64, description='S* parameter indicating loop squareness.'
    )

class AGMScriptSegment(ArchiveSection):
    segment_number = Quantity(
        type=int, description='Sequential ID of the measurement segment.'
    )
    averaging_time = Quantity(
        type=np.float64, unit='s', description='Signal averaging time specific to this segment.'
    )
    initial_field = Quantity(
        type=np.float64, unit='A/m', description='Starting magnetic field of the segment.'
    )
    field_increment = Quantity(
        type=np.float64, unit='A/m', description='Step size between field setpoints.'
    )
    final_field = Quantity(
        type=np.float64, unit='A/m', description='Ending magnetic field of the segment.'
    )
    pause = Quantity(
        type=np.float64, unit='s', description='Wait time before starting data acquisition in this segment.'
    )
    final_index = Quantity(
        type=int, description='The array index corresponding to the end of this segment.'
    )

class AGMScript(ArchiveSection):
    number_of_segments = Quantity(
        type=int, description='Total number of distinct field sweep segments.'
    )
    number_of_data = Quantity(
        type=int, description='Total number of discrete data points collected.'
    )
    segments = SubSection(section_def=AGMScriptSegment, repeats=True)

# --- 2. Main AGM Schema ---

class ELNAlternatingGradientMagnetometry(BaseMagnetometry, EntryData):
    m_def = Section(label='MicroMag AGM', a_eln=dict(lane_width='600px'))

    data_file = Quantity(
        type=str,
        a_eln=dict(component=ELNComponentEnum.FileEditQuantity),
        a_browser=dict(adaptor='RawFileAdaptor'),
        description='The raw .txt data file exported from the MicroMag software.',
    )

    data_format_version = Quantity(
        type=str, description='Version of the file structure generated by the hardware.'
    )
    measurement_mode = Quantity(
        type=str, description='Data acquisition mode (e.g., Multiple Segments).'
    )

    instrument_setup = SubSection(section_def=AGMInstrument)
    settings = SubSection(section_def=AGMSettings)
    measurement_details = SubSection(section_def=AGMMeasurementDetails)
    processing = SubSection(section_def=AGMProcessing)
    viewport = SubSection(section_def=AGMViewport)
    characterization = SubSection(section_def=AGMCharacterization)
    script = SubSection(section_def=AGMScript)

    def _get_cleaners(self):
        def safe_float(val):
            if not val or val == 'N/A': return None
            try: return float(val)
            except ValueError: return None

        def safe_float_oe(val):
            v = safe_float(val)
            return v * OE_TO_AM if v is not None else None

        def safe_float_emu(val):
            v = safe_float(val)
            return v * EMU_TO_AM2 if v is not None else None

        def safe_float_emu_oe(val):
            v = safe_float(val)
            return v * EMU_OE_TO_M3 if v is not None else None

        def safe_int(val):
            if not val or val == 'N/A': return None
            try: return int(val)
            except ValueError: return None

        return {'float': safe_float, 'float_oe': safe_float_oe, 'float_emu': safe_float_emu, 'float_emu_oe': safe_float_emu_oe, 'int': safe_int}

    def _map_hardware_and_settings(self, metadata, cleaners):
        sf, s_oe, s_emu = cleaners['float'], cleaners['float_oe'], cleaners['float_emu']

        if not self.instrument_setup:
            self.instrument_setup = AGMInstrument(
                configuration=metadata.get('Configuration'),
                temperature_control=metadata.get('Temperature control'),
                hardware_version=metadata.get('Hardware version'),
                units_of_measure=metadata.get('Units of measure'),
                temperature_in=metadata.get('Temperature in'),
            )

        if not self.settings:
            self.settings = AGMSettings(
                field_range=s_oe(metadata.get('Field range')),
                field_command=s_oe(metadata.get('Field (command)')),
                moment_range=s_emu(metadata.get('Moment range')),
                averaging_time=sf(metadata.get('Averaging time')),
                temperature_command=sf(metadata.get('Temperature (command)')),
                tmprtr_difference_correction=metadata.get('Tmprtr difference correction'),
                orientation=metadata.get('Orientation'),
                gradient=sf(metadata.get('Gradient')),
                probe_factor=sf(metadata.get('Probe factor')),
                probe_q=sf(metadata.get('Probe Q')),
                probe_resonance=sf(metadata.get('Probe resonance')),
                operating_frequency=sf(metadata.get('Operating frequency')),
                sweep_mode=metadata.get('Sweep mode'),
            )

        if not self.measurement_details:
            self.measurement_details = AGMMeasurementDetails(
                description=metadata.get('Description', '').strip('"'),
                field_measured=s_oe(metadata.get('Field (measured)')),
                temperature_measured=sf(metadata.get('Temperature (measured)')),
                averages_completed=sf(metadata.get('Averages (completed)')),
                elapsed_time=sf(metadata.get('Elapsed time')),
            )

    def _map_processing_and_script(self, metadata, agm_data, cleaners):
        sf, s_oe, s_emu, s_emu_oe, si = cleaners['float'], cleaners['float_oe'], cleaners['float_emu'], cleaners['float_emu_oe'], cleaners['int']

        if not self.processing:
            self.processing = AGMProcessing(
                background_subtraction=metadata.get('Background subtraction'),
                delta_m_processing=metadata.get('Delta-m processing'),
                demagnetizing_factor=metadata.get('Demagnetizing factor'),
                normalization=metadata.get('Normalization'),
                normalization_factor=sf(metadata.get('Normalization factor')),
                offset_field=metadata.get('Offset (field)'),
                offset_moment=metadata.get('Offset (moment)'),
                pole_saturation=metadata.get('Pole saturation'),
                slope_correction=metadata.get('Slope correction'),
            )

        if not self.viewport:
            self.viewport = AGMViewport(
                left=s_oe(metadata.get('Left')),
                right=s_oe(metadata.get('Right')),
                bottom=s_emu(metadata.get('Bottom')),
                top=s_emu(metadata.get('Top')),
                show_x_axis=metadata.get('Show X-axis?'),
                show_y_axis=metadata.get('Show Y-axis?'),
            )

        if not self.characterization:
            self.characterization = AGMCharacterization(
                initial_slope=s_emu_oe(metadata.get('Initial slope')),
                saturation=s_emu(metadata.get('Saturation')),
                remanence=s_emu(metadata.get('Remanence')),
                coercivity=s_oe(metadata.get('Coercivity')),
                s_star=sf(metadata.get('S*')),
            )

        if not self.script:
            self.script = AGMScript(
                number_of_segments=si(metadata.get('Number of segments')),
                number_of_data=si(metadata.get('Number of data')),
            )

        if agm_data.segments is not None and not self.script.segments:
            segments_list = []
            for _, row in agm_data.segments.iterrows():
                seg = AGMScriptSegment(
                    segment_number=int(row['Segment Number']),
                    averaging_time=float(row['Averaging Time (s)']),
                    initial_field=float(row['Initial Field (Oe)']) * OE_TO_AM,
                    field_increment=float(row['Field Increment (Oe)']) * OE_TO_AM,
                    final_field=float(row['Final Field (Oe)']) * OE_TO_AM,
                    pause=float(row['Pause (s)']),
                    final_index=int(row['Final Index']),
                )
                segments_list.append(seg)
            self.script.segments = segments_list

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger'):
        if not self.data_file:
            super().normalize(archive, logger)
            return

        try:
            with archive.m_context.raw_file(self.data_file) as file:
                agm_data = read_micromag_agm(file.name)

            metadata = agm_data.metadata
            cleaners = self._get_cleaners()

            self.instrument_model = metadata.get('Instrument Model')
            self.software_version = metadata.get('Software version')
            self.measurement_type = metadata.get('Measurement Type')

            raw_time = metadata.get('Measured on')
            self.start_time = str(raw_time).strip() if raw_time and raw_time != 'N/A' else None

            self.data_format_version = metadata.get('Data Format Version')
            self.measurement_mode = metadata.get('Measurement Mode')

            if not self.sample_setup:
                self.sample_setup = MagnetometrySample(
                    mass=cleaners['float'](metadata.get('Mass')),
                    volume=cleaners['float'](metadata.get('Volume')),
                    demagnetizing_factor=cleaners['float'](metadata.get('Demagnetizing factor')),
                )

            self._map_hardware_and_settings(metadata, cleaners)
            self._map_processing_and_script(metadata, agm_data, cleaners)

            if not self.results:
                self.results = [MagnetometryResult()]
            res = self.results[0]

            # Apply SI Conversion to data arrays!
            res.magnetic_field = agm_data.magnetic_field * OE_TO_AM if agm_data.magnetic_field is not None else None
            res.magnetic_moment = agm_data.magnetic_moment * EMU_TO_AM2 if agm_data.magnetic_moment is not None else None
            res.normalized_moment = agm_data.normalized_moment

        except Exception as e:
            if logger:
                logger.error(f'Error parsing AGM file: {e}')
            raise e

        super().normalize(archive, logger)

# ==========================================
# 3. VSM SCHEMA
# ==========================================

class FieldConfigurations(ArchiveSection):
    magnet_model = Quantity(type=str, description='Model of the electromagnet used for the applied field.')
    power_supply = Quantity(type=str, description='Power supply model driving the magnet.')
    magnet_mode = Quantity(type=str, description='Operational mode of the electromagnet.')
    head_amplitude = Quantity(type=str, description='Vibrational amplitude of the VSM head.')
    gap_settings = Quantity(type=str, description='Distance configuration between the magnet pole pieces.')
    coil_set_name = Quantity(type=str, description='Identifier for the pickup coil configuration.')
    coil_set_serial_number = Quantity(type=str, description='Serial number of the pickup coils.')
    coil_set_balance_number = Quantity(type=np.float64, description='Hardware balance parameter for the coil set.')
    moment_x_calibration_value = Quantity(
        type=np.float64, unit='A * m**2 / V', description='Calibration multiplier linking lock-in voltage to moment (Converted from emu/V).'
    )
    moment_x_calibration_field = Quantity(
        type=np.float64, unit='A/m', description='Magnetic field applied during moment calibration.'
    )
    moment_x_calibration_expected_moment = Quantity(
        type=np.float64, unit='A * m**2', description='Theoretical reference moment of the calibration standard.'
    )
    moment_x_calibration_standard_id = Quantity(type=str, description='Identifier of the standard sample (e.g., Nickel sphere) used.')
    moment_x_calibration_comments = Quantity(type=str, description='Additional notes recorded during instrument calibration.')

class AdvancedAcquisitionSetup(ArchiveSection):
    acquisition_mode = Quantity(type=str, description='Lock-in acquisition style used.')
    pause_at_plus_minus_max_fields = Quantity(type=np.float64, unit='s', description='Stabilization pause duration at maximum loop field.')
    moment_meter_range_mode = Quantity(type=str, description='Auto-ranging or static behavior of the moment meter.')
    gaussmeter_range_mode = Quantity(type=str, description='Auto-ranging or static behavior of the gaussmeter.')
    gaussmeter_fixed_range = Quantity(type=str, description='Fixed range setting if auto-range is disabled.')

class AcquisitionSetup(ArchiveSection):
    saturation_field = Quantity(type=str, description='Nominal field used to saturate the sample.')
    max_field = Quantity(type=str, description='Maximum absolute field reached during the loop.')
    forc_type = Quantity(type=str, description='First-Order Reversal Curve mapping pattern.')
    max_hc_field = Quantity(type=np.float64, unit='A/m', description='Maximum coercive field limit configured for FORC.')
    max_hu_field = Quantity(type=np.float64, unit='A/m', description='Maximum interaction field limit configured for FORC.')
    min_hu_field = Quantity(type=np.float64, unit='A/m', description='Minimum interaction field limit configured for FORC.')
    calibration_field_tolerance = Quantity(type=str, description='Allowed variance in the approach to the calibration field.')
    pause_at_calibration_field = Quantity(type=np.float64, unit='s', description='Wait time to stabilize at the calibration field.')
    number_of_forcs = Quantity(type=np.int32, description='Total number of reversal curves measured.')
    saturation_field_tolerance = Quantity(type=str, description='Allowed variance in the approach to the saturation field.')
    pause_at_saturation_field = Quantity(type=np.float64, unit='s', description='Wait time to stabilize at saturation before reversing.')
    reversal_field_tolerance = Quantity(type=str, description='Allowed variance in the approach to the reversal field (Hr).')
    pause_at_reversal_fields = Quantity(type=np.float64, unit='s', description='Wait time to stabilize at reversal field prior to sweep.')
    enable_subtract_last_branches = Quantity(type=bool, description='Indicates if the last major branch was subtracted from the FORCs.')
    last_branch_iterations = Quantity(type=np.int32, description='Number of points averaged for the last branch subtraction.')
    field_step_size = Quantity(type=np.float64, unit='A/m', description='Increment size of the applied magnetic field sweep.')
    include_initial_curve = Quantity(type=bool, description='Indicates if the initial magnetization curve is included in the sequence.')
    averaging_time = Quantity(type=np.float64, unit='s', description='Time spent collecting signal per data point.')
    show_forc_diagram_on_the_fly = Quantity(type=bool, description='Indicates if software plotting of the FORC diagram was active.')
    smoothing_factor = Quantity(type=np.float64, description='Smoothing factor applied internally by the instrument.')
    rotate_45_degrees = Quantity(type=bool, description='Indicates if the FORC diagram coordinates were rotated to Hc/Hu.')
    truncate_for_a_rectangle_diagram = Quantity(type=bool, description='Indicates if data outside a rectangular bounding box was discarded.')
    number_of_contours = Quantity(type=np.int32, description='Visual contour limits set in the plotting software.')
    correct_for_drift = Quantity(type=bool, description='Indicates if a baseline drift correction was applied.')
    advanced_acquisition_setup = SubSection(sub_section=AdvancedAcquisitionSetup)

class DisplaySetup(ArchiveSection):
    x_axis = Quantity(type=str, description='Quantity plotted on the X-axis in the Lake Shore software.')
    left_y_axis = Quantity(type=str, description='Quantity plotted on the primary Y-axis.')
    right_y_axis = Quantity(type=str, description='Quantity plotted on the secondary Y-axis.')

class ELNVibratingSampleMagnetometry(BaseMagnetometry, EntryData):
    m_def = Section(label='Lake Shore VSM')
    data_file = Quantity(
        type=str,
        a_eln=ELNAnnotation(component=ELNComponentEnum.FileEditQuantity),
        description='The raw .csv data file exported from the Lake Shore software.',
    )

    field_configurations = SubSection(sub_section=FieldConfigurations)
    acquisition_setup = SubSection(sub_section=AcquisitionSetup)
    display_setup = SubSection(sub_section=DisplaySetup)

    def _get_cleaners(self, metadata):
        def clean_float(key, strip_str=None):
            val = metadata.get(key)
            if val:
                if strip_str: val = val.replace(strip_str, '')
                try: return float(val.strip())
                except ValueError: return None
            return None

        def clean_float_oe(key, strip_str=None):
            v = clean_float(key, strip_str)
            return v * OE_TO_AM if v is not None else None

        def clean_float_emu(key, strip_str=None):
            v = clean_float(key, strip_str)
            return v * EMU_TO_AM2 if v is not None else None

        def clean_float_emu_v(key, strip_str=None):
            v = clean_float(key, strip_str)
            return v * EMU_TO_AM2 if v is not None else None # Voltage is untouched, emu becomes A*m^2

        def clean_int(key):
            val = metadata.get(key)
            if val:
                try: return int(val.strip())
                except ValueError: return None
            return None

        def clean_bool(key):
            val = metadata.get(key, '').strip().lower()
            return val == 'true' if val in ['true', 'false'] else None

        return {'float': clean_float, 'float_oe': clean_float_oe, 'float_emu': clean_float_emu, 'float_emu_v': clean_float_emu_v, 'int': clean_int, 'bool': clean_bool}

    def _map_acquisition_and_display(self, metadata, cleaners):
        cf, c_oe, ci, cb = cleaners['float'], cleaners['float_oe'], cleaners['int'], cleaners['bool']

        acq = AcquisitionSetup()
        acq.saturation_field = metadata.get('Saturation field')
        acq.max_field = metadata.get('Max field')
        acq.forc_type = metadata.get('FORC type')
        acq.max_hc_field = c_oe('Max Hc field', 'Oe')
        acq.max_hu_field = c_oe('Max Hu field', 'Oe')
        acq.min_hu_field = c_oe('Min Hu field', 'Oe')
        acq.calibration_field_tolerance = metadata.get('Calibration field tolerance')
        acq.pause_at_calibration_field = cf('Pause at calibration field', 's')
        acq.number_of_forcs = ci('Number of FORCs')
        acq.saturation_field_tolerance = metadata.get('Saturation field tolerance')
        acq.pause_at_saturation_field = cf('Pause at saturation field', 's')
        acq.reversal_field_tolerance = metadata.get('Reversal field tolerance')
        acq.pause_at_reversal_fields = cf('Pause at reversal fields', 's')
        acq.enable_subtract_last_branches = cb('Enable subtract Last branches')
        acq.last_branch_iterations = ci('Last branch iterations')
        acq.field_step_size = c_oe('Field_step size', 'Oe')
        acq.include_initial_curve = cb('Include initial curve')
        acq.averaging_time = cf('Averaging time', 's')
        acq.show_forc_diagram_on_the_fly = cb('Show FORC diagram on the fly')
        acq.smoothing_factor = cf('Smoothing factor')
        acq.rotate_45_degrees = cb('Rotate 45 degrees')
        acq.truncate_for_a_rectangle_diagram = cb('Truncate for a rectangle diagram')
        acq.number_of_contours = ci('Number of contours')
        acq.correct_for_drift = cb('Correct for drift')

        adv = AdvancedAcquisitionSetup()
        adv.acquisition_mode = metadata.get('Acquisition mode')
        adv.pause_at_plus_minus_max_fields = cf('Pause at +/- max fields', 's')
        adv.moment_meter_range_mode = metadata.get('Moment meter range mode')
        adv.gaussmeter_range_mode = metadata.get('Gaussmeter range mode')
        adv.gaussmeter_fixed_range = metadata.get('Gaussmeter fixed range')
        acq.advanced_acquisition_setup = adv
        self.acquisition_setup = acq

        ds = DisplaySetup()
        ds.x_axis = metadata.get('X axis')
        ds.left_y_axis = metadata.get('Left Y axis')
        ds.right_y_axis = metadata.get('Right Y axis')
        self.display_setup = ds

    def _map_sample_and_configs(self, metadata, cleaners):
        cf, c_oe, c_emu, c_emu_v = cleaners['float'], cleaners['float_oe'], cleaners['float_emu'], cleaners['float_emu_v']

        fc = FieldConfigurations()
        fc.magnet_model = metadata.get('Magnet')
        fc.power_supply = metadata.get('Power supply')
        fc.magnet_mode = metadata.get('Magnet mode')
        fc.head_amplitude = metadata.get('Head amplitude')
        fc.gap_settings = metadata.get('Gap settings')
        fc.coil_set_name = metadata.get('Coil set name')
        fc.coil_set_serial_number = metadata.get('Coil set serial number')
        fc.coil_set_balance_number = cf('Coil set balance number')
        fc.moment_x_calibration_value = c_emu_v('Moment X calibration value', 'emu/volt')
        fc.moment_x_calibration_field = c_oe('Moment X calibration field', 'Oe')
        fc.moment_x_calibration_expected_moment = c_emu('Moment X calibration expected moment', 'emu')
        fc.moment_x_calibration_standard_id = metadata.get('Moment X calibration standard ID')
        fc.moment_x_calibration_comments = metadata.get('Moment X calibration comments')
        self.field_configurations = fc

        if not self.sample_setup:
            self.sample_setup = MagnetometrySample()

        self.sample_setup.sample_id = metadata.get('ID')
        self.sample_setup.volume = cf('Volume', 'cm³')
        self.sample_setup.area = cf('Area', 'cm²')
        self.sample_setup.mass = cf('Mass', 'g')
        self.sample_setup.density = cf('Density', 'g/cm³')
        self.sample_setup.thickness = cf('Thickness', 'mm')
        self.sample_setup.demagnetizing_factor = cf('Demagnetization factor in SI')
        self.sample_setup.demagnetizing_factor_cgs = cf('Demagnetization factor in cgs')

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger'):
        if not self.data_file:
            super().normalize(archive, logger)
            return

        try:
            with archive.m_context.raw_file(self.data_file) as file:
                vsm_data = read_lakeshore_vsm(file.name)

            cleaners = self._get_cleaners(vsm_data.metadata)

            self.instrument_model = 'Lake Shore VSM'
            self.software_version = vsm_data.metadata.get('Software Version')
            self.start_time = vsm_data.metadata.get('START TIME')
            self.finish_time = vsm_data.metadata.get('FINISH TIME')
            self.measurement_type = vsm_data.metadata.get('Measurement Type')

            self._map_sample_and_configs(vsm_data.metadata, cleaners)
            self._map_acquisition_and_display(vsm_data.metadata, cleaners)

            if not self.results:
                self.results = [MagnetometryResult()]

            res = self.results[0]
            res.step_array = vsm_data.step
            res.iteration_array = vsm_data.iteration
            res.segment_array = vsm_data.segment
            res.time_stamp = vsm_data.time_stamp
            res.field_status = vsm_data.field_status
            res.moment_status = vsm_data.moment_status

            # Apply SI Conversion to data arrays!
            res.magnetic_field = vsm_data.magnetic_field * OE_TO_AM if vsm_data.magnetic_field is not None else None
            res.magnetic_moment = vsm_data.magnetic_moment * EMU_TO_AM2 if vsm_data.magnetic_moment is not None else None

        except Exception as e:
            logger.error(f'Error parsing VSM file: {e}')

        super().normalize(archive, logger)

m_package.__init_metainfo__()