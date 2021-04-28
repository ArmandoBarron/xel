import json
import os
import logging #logger
import shutil
from . import download_request as mod

def config_env():
    pass


def custom_app(app_params,reserved_params):
    st= mod.download_file(app_params['DOWNLOAD_server'],
                            reserved_params['SINK'],
                            app_params['NAMEFILE'],
                            app_params['EXT'],
                            app_params['URL'],
                            app_params['ID_FILE'],
                            app_params['USER'],
                            app_params['PASS']) # result
    #post processing
    new_destination = reserved_params['SINK'] +  app_params['NAMEFILE'] +"."+ app_params['EXT']
    if app_params['DOWNLOAD_server']=="BB_FILES":
        shutil.copyfile(reserved_params['CWD']+"input_data/"+app_params['NAMEFILE']+"."+app_params['EXT'], new_destination)
