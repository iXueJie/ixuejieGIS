import os
# _here = os.path.dirname(__file__)


def setup_env():
    import sys
    sys.path.append("E:\\Program Files\\QGIS 3.22.10\\apps\\qgis-ltr\\python\\plugins")

    # if not os.path.exists(os.path.join(_here, 'share')):
    #     return
    #     # gdal data
    # os.environ['GDAL_DATA'] = os.path.join(_here, 'share', 'gdal')
    # # proj lib
    # os.environ['PROJ_LIB'] = os.path.join(_here, 'share', 'proj')
    # # geotiff_csv
    # os.environ['GEOTIFF_CSV'] = os.path.join(_here, 'share', 'epsg_csv')
    # # gdalplugins
    # # os.environ['GDAL_DRIVER_PATH'] = os.path.join(_here, 'gdalplugins')
