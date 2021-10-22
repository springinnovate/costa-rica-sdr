"""Reclassify raster by given table."""
import argparse
import logging
import os

from ecoshard import geoprocessing
from osgeo import gdal
import pandas

gdal.SetCacheMax(2**28)
logging.basicConfig(
    level=logging.DEBUG,
    format=(
        '%(asctime)s (%(relativeCreated)d) %(levelname)s %(name)s'
        ' [%(funcName)s:%(lineno)d] %(message)s'))
LOGGER = logging.getLogger(__name__)


def _base_filename(path):
    """Get the filename without dir or extension."""
    return os.path.basename(os.path.splitext(path)[0])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Reclassify raster by table')
    parser.add_argument('raster_path', type=str, help='path to raster')
    parser.add_argument(
        'reclassify_table_path', type=str, help='path to table')
    parser.add_argument(
        'base_lulc_field', type=str, help=(
            'column name in `reclassify_table_path` that corresponds to the '
            '"input" lulc in `raster_path`'))
    parser.add_argument(
        'target_lulc_field', type=str, help=(
            'column name in `reclassify_table_path` that corresponds to the '
            '"output" lulc in `raster_path`'))

    args = parser.parse_args()

    df = pandas.read_csv(args.reclassify_table_path)
    value_map = {
        int(base_lucode): int(target_lucode)
        for base_lucode, target_lucode in zip(
            df[args.base_lulc_field], df[args.target_lulc_field])}
    LOGGER.info(f'reclassification map: {value_map}')

    target_raster_path = f'''reclassified_{
        _base_filename(args.raster_path)}_{
        _base_filename(args.reclassify_table_path)}.tif'''
    LOGGER.info(f'reclassifying to: {target_raster_path}')
    raster_info = geoprocessing.get_raster_info(args.raster_path)
    geoprocessing.reclassify_raster(
        (args.raster_path, 1), value_map, target_raster_path,
        raster_info['datatype'], raster_info['nodata'][0],
        values_required=False)
    LOGGER.info('all done!')
