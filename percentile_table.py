"""Create percentile table for raster."""
import argparse
import logging
import os

from osgeo import gdal
from ecoshard import geoprocessing
import numpy
import pandas

gdal.SetCacheMax(2**28)
logging.basicConfig(
    level=logging.DEBUG,
    format=(
        '%(asctime)s (%(relativeCreated)d) %(levelname)s %(name)s'
        ' [%(funcName)s:%(lineno)d] %(message)s'))
LOGGER = logging.getLogger(__name__)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Build percentile table')
    parser.add_argument('raster_path', type=str, help='path to raster')
    parser.add_argument(
        '--percentile_stepsize', type=float, default=0.5,
        help='steps between percentile to sample default is 0.5')
    parser.add_argument(
        '--initial_stepsize', type=float, default=0.1,
        help='initial percentile stepsize 0 to ``--percentile_stepsize``')
    parser.add_argument(
        '--nodata', type=float, help=(
            'DANGER: specify is nodata is undefined, will overwrite nodata '
            'value in raster'))
    args = parser.parse_args()

    percentile_table_path = (
        f'%s_{args.initial_stepsize}_{args.percentile_stepsize}.csv' %
        os.path.splitext(os.path.basename(args.raster_path))[0])
    raster_info = geoprocessing.get_raster_info(args.raster_path)

    if args.nodata is not None:
        raster = gdal.OpenEx(args.raster_path, gdal.OF_RASTER | gdal.GA_Update)
        for band_index in range(raster.RasterCount):
            band = raster.GetRasterBand(band_index+1)
            band.SetNoDataValue(args.nodata)
        band = None
        raster = None

    percentile_working_dir = 'percentile_workspace'
    percentile_threshold_list = list(numpy.arange(
        0, args.percentile_stepsize,
        args.initial_stepsize)) + list(numpy.arange(
            args.percentile_stepsize, 100+args.percentile_stepsize,
            args.percentile_stepsize))
    LOGGER.info(f'percentile thresholds: {percentile_threshold_list}')

    column_names = ['percentile_thresholds']
    percentile_table = {
        column_names[0]: percentile_threshold_list
    }

    for band_index in range(len(raster_info['nodata'])):
        LOGGER.info(f'calculating percentiles for band {band_index+1}')
        percentile_values_list = geoprocessing.raster_band_percentile(
            (args.raster_path, band_index+1), percentile_working_dir,
            percentile_threshold_list)
        column_names.append(f'band_{band_index+1}')
        percentile_table[column_names[-1]] = percentile_values_list
        break

    LOGGER.info(f'saving to {percentile_table_path}')
    df = pandas.DataFrame.from_dict(percentile_table)
    df.to_csv(percentile_table_path, columns=column_names)
