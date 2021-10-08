import logging
import inspring.sdr_c_factor
logging.basicConfig(level=logging.INFO)

args = {
    'biophysical_table_path': './cFactor_GloblBioPhysTable.csv',
    'dem_path': './DEM_hydrosheds_CR90m.tif',
    'drainage_path': './LULC_water_1_drainages.tif',
    'erodibility_path': './erodibility_gapfilled_CR.tif',
    'erosivity_path': './erosivity_gapfilled_CR.tif',
    'ic_0_param': '0.5',
    'k_param': '2',
    'l_cap': 122,
    'lulc_path': './MODIS_merge_Clip1.tif',
    'results_suffix': '16Aug2021_1606h_Landsat2012simpleExpLS122',
    'sdr_max': '0.8',
    'threshold_flow_accumulation': '1000',
    'watersheds_path': './CR_500m_buffer.shp',
    'workspace_dir': './Landsat2012exp',
    'c_factor_path': './Landsat2012_reflect_simpleExpCap.tif'
}

if __name__ == '__main__':
    inspring.sdr_c_factor.execute(args)

# CD to the correct dir
# docker login
# docker pull therealspring/inspring:latest
# docker run -it --rm -v "%CD%":/usr/local/workspace therealspring/inspring:latest Landsat2012simpleExpLS122.py