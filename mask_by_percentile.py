"""Mask percentile tails to nodata."""
import argparse
import logging
import os
import shutil
import tempfile

from osgeo import gdal
from ecoshard import geoprocessing
import numpy

gdal.SetCacheMax(2**28)
logging.basicConfig(
    level=logging.DEBUG,
    format=(
        '%(asctime)s (%(relativeCreated)d) %(levelname)s %(name)s'
        ' [%(funcName)s:%(lineno)d] %(message)s'))
logging.getLogger('taskgraph').setLevel(logging.WARN)
LOGGER = logging.getLogger(__name__)


def _clamp_value_op(value_array, nodata, min_clamp, max_clamp):
    """Set values outside of [min_clamp, max_clamp] to nodata."""
    valid_mask = (value_array != nodata) & (
        (value_array < min_clamp) | (value_array > max_clamp))
    result = numpy.copy(value_array)
    result[valid_mask] = nodata
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Mask values outside of percentile tails to nodata.')
    parser.add_argument('raster_path', type=str, help='path to raster')
    parser.add_argument(
        'percentile_cutoff', type=float, help='upper/lower percentile')
    parser.add_argument(
        '--band_index', type=int, default=1, help='band index to operate on')
    parser.add_argument(
        '--nodata', type=float, help='specify the nodata value')
    args = parser.parse_args()

    raster_info = geoprocessing.get_raster_info(args.raster_path)
    if args.nodata is not None:
        nodata = args.nodata
    else:
        nodata = raster_info['nodata'][args.band_index-1]
        if nodata is None:
            raise ValueError(
                'raster has undefined nodata value, use the flag --nodata to '
                'define your own')

    LOGGER.info(f'calculating percentiles for {args.percentile_cutoff} tails')
    percentile_working_dir = tempfile.mkdtemp(
        dir='.', prefix=os.path.basename(args.raster_path))
    min_clamp, max_clamp = geoprocessing.raster_band_percentile(
        (args.raster_path, args.band_index), percentile_working_dir,
        [args.percentile_cutoff, 100-args.percentile_cutoff])

    target_raster_path = (
        f'%s_clamped_{args.percentile_cutoff}%s' % os.path.splitext(
            os.path.basename((args.raster_path))))

    LOGGER.info(
        f'clamping {os.path.basename(args.raster_path)} '
        f'band: {args.band_index} '
        f'{args.percentile_cutoff}: {min_clamp}; '
        f'{100-args.percentile_cutoff}: {max_clamp} '
        f'with nodata: {nodata}')

    geoprocessing.raster_calculator(
        [(args.raster_path, args.band_index), (nodata, 'raw'),
         (min_clamp, 'raw'), (max_clamp, 'raw')], _clamp_value_op,
        target_raster_path, raster_info['datatype'],
        nodata)
    shutil.rmtree(percentile_working_dir)
