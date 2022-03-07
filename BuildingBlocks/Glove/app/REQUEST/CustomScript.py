import json
import os
import logging #logger
import shutil

LOGER = logging.getLogger()

def config_env():
    pass

def custom_app(app_params,reserved_params):

    glove_path = reserved_params['CWD']+"GloVe/"

    CORPUS = app_params['corpus_filename']
    VECTOR_SIZE = app_params['vector_size']
    MAX_ITER = app_params['max_iter']
    WINDOW_SIZE = app_params['window_size']

    # call the application
    execution_status = os.system('%sdemo.sh %s %s %s %s %s %s' %(glove_path, glove_path, reserved_params['SOURCE'], CORPUS,VECTOR_SIZE,MAX_ITER,WINDOW_SIZE ))

    # move results to sink
    shutil.copyfile(glove_path+"vectors.txt", reserved_params['SINK']+"vectors.txt")
    shutil.copyfile(glove_path+"vocab.txt", reserved_params['SINK']+"vocab.txt")
