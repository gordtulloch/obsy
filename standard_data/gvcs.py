import csv
import logging

logger = logging.getLogger(__name__)

CONSTELLATIONS = {
    '01': 'AND',
    '02': 'ANT',
    '03': 'APS',
    '04': 'AQR',
    '05': 'AQL',
    '06': 'ARA',
    '07': 'ARI',
    '08': 'AUR',
    '09': 'BOO',
    '10': 'CAE',
    '11': 'CAM',
    '12': 'CNC',
    '13': 'CVN',
    '14': 'CMA',
    '15': 'CMI',
    '16': 'CAP',
    '17': 'CAR',
    '18': 'CAS',
    '19': 'CEN',
    '20': 'CEP',
    '21': 'CET',
    '22': 'CHA',
    '23': 'CIR',
    '24': 'COL',
    '25': 'COM',
    '26': 'CRA',
    '27': 'CRB',
    '28': 'CRV',
    '29': 'CRT',
    '30': 'CRU',
    '31': 'CYG',
    '32': 'DEL',
    '33': 'DOR',
    '34': 'DRA',
    '35': 'EQU',
    '36': 'ERI',
    '37': 'FOR',
    '38': 'GEM',
    '39': 'GRU',
    '40': 'HER',
    '41': 'HOR',
    '42': 'HYA',
    '43': 'HYI',
    '44': 'IND',
    '45': 'LAC',
    '46': 'LEO',
    '47': 'LMI',
    '48': 'LEP',
    '49': 'LIB',
    '50': 'LUP',
    '51': 'LYN',
    '52': 'LYR',
    '53': 'MEN',
    '54': 'MIC',
    '55': 'MON',
    '56': 'MUS',
    '57': 'NOR',
    '58': 'OCT',
    '59': 'OPH',
    '60': 'ORI',
    '61': 'PAV',
    '62': 'PEG',
    '63': 'PER',
    '64': 'PHE',
    '65': 'PIC',
    '66': 'PSC',
    '67': 'PSA',
    '68': 'PUP',
    '69': 'PYX',
    '70': 'RET',
    '71': 'SGE',
    '72': 'SGR',
    '73': 'SCO',
    '74': 'SCL',
    '75': 'SCT',
    '76': 'SER',
    '77': 'SEX',
    '78': 'TAU',
    '79': 'TEL',
    '80': 'TRI',
    '81': 'TRA',
    '82': 'TUC',
    '83': 'UMA',
    '84': 'UMI',
    '85': 'VEL',
    '86': 'VIR',
    '87': 'VOL',
    '88': 'VUL',
}


TRANSLATION_MAP = {ord(ch): None for ch in '():/'}


class GcvsParser(object):
    """
    A parser for GCVS data format.

    Example usage:

        >>> with open('iii.dat', 'rb') as fp:
        ...     parser = GcvsParser(fp)
        ...     for star in parser:
        ...         print(star['name'])
        R AND
        S AND
        #...
        V0515 VUL
        V0516 VUL
    """

    def __init__(self, fp):
        """
        Creates the parser and feeds it a file-like object.

        :param fp: a file-like object or a generator yielding strings
        """
        self.reader = csv.reader(fp, delimiter=str('|'))
        # skip two initial lines
        next(self.reader)
        next(self.reader)

    def __iter__(self):
        for row in self.reader:
            if len(row) != 15:
                continue
            try:
                yield self.row_to_dict(row)
            except Exception:
                logger.exception("Error in row: %s", row)
                continue

    def row_to_dict(self, row):
        """
        Converts a raw GCVS record to a dictionary of star data.
        """
        constellation = self.parse_constellation(row[0])
        name = self.parse_name(row[1])
        ra, dec = self.parse_coordinates(row[2])
        variable_type = row[3].strip()
        max_magnitude, symbol = self.parse_magnitude(row[4])
        min_magnitude, symbol = self.parse_magnitude(row[5])
        if symbol == '(' and max_magnitude is not None:
            # this is actually amplitude
            min_magnitude = max_magnitude + min_magnitude
        epoch = self.parse_epoch(row[8])
        period = self.parse_period(row[10])
        return {
            'constellation': constellation,
            'name': name,
            'ra': ra,
            'dec': dec,
            'variable_type': variable_type,
            'max_magnitude': max_magnitude,
            'min_magnitude': min_magnitude,
            'epoch': epoch,
            'period': period,
        }

    def parse_constellation(self, constellation_str):
        constellation_num = constellation_str[:2]
        return CONSTELLATIONS[constellation_num]

    def parse_name(self, name_str):
        """
        Normalizes variable star designation (name).
        """
        name = name_str[:9]
        return ' '.join(name.split()).upper()

    def parse_coordinates(self, coords_str):
        """
        Returns a pair of PyEphem-compatible coordinate strings (Ra, Dec).

        If the star has no coordinates in GCVS (there are such cases), a pair
        of None values is returned.
        """
        if coords_str.strip() == '':
            return (None, None)
        ra = '%s:%s:%s' % (coords_str[0:2], coords_str[2:4], coords_str[4:8])
        dec = '%s:%s:%s' % (coords_str[8:11], coords_str[11:13], coords_str[13:15])
        return (ra, dec)

    def parse_magnitude(self, magnitude_str):
        """
        Converts magnitude field to a float value, or ``None`` if GCVS does
        not list the magnitude.

        Returns a tuple (magnitude, symbol), where symbol can be either an
        empty string or a single character - one of '<', '>', '('.
        """
        symbol = magnitude_str[0].strip()
        magnitude = magnitude_str[1:6].strip()
        return magnitude if magnitude else None, symbol

    def parse_epoch(self, epoch_str):
        """
        Converts epoch field to a float value (adding 24... prefix), or
        ``None`` if there is no epoch in GCVS record.
        """
        epoch = epoch_str.translate(TRANSLATION_MAP)[:10].strip()
        return 2400000.0 + float(epoch) if epoch else None

    def parse_period(self, period_str):
        """
        Converts period field to a float value or ``None`` if there is
        no period in GCVS record.
        """
        period = period_str.translate(TRANSLATION_MAP)[3:14].strip()
        return float(period) if period else None
    
with open('/home/gtulloch/obsy.dev/standard_data/iii.txt', 'r') as fp:
    parser = GcvsParser(fp)
    for star in parser:
        print(star['name'],star['ra'],star['dec'],star['max_magnitude'],star['min_magnitude'],star['epoch'],star['period'])