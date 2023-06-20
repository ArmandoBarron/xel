
import logging
from threading import Thread
import os
from shutil import rmtree
from time import sleep
from datetime import datetime, timedelta


class GarbageCollector(Thread):

    def __init__(self,PROPOSER,FOLDER,LOGER=None,stopwatch=10):
        Thread.__init__(self)

        #super(postman, self).__init__()
        if LOGER is None:
            self.LOGER = logging.getLogger()
        else:
            self.LOGER=LOGER

        ####
        self.PROPOSER=PROPOSER
        self.FOLDER = FOLDER
        self.FOLDER = FOLDER
        self.STOPWATCH = stopwatch * 60 #minutes

    def run(self):
        while True:
            self.LOGER.info("GARBAGE COLLECTOR: Cleaning %s" %self.FOLDER)
            # clean folder
            self.GarbageCollector()
            # wait
            self.LOGER.info("GARBAGE COLLECTOR: Cleaning for %s complete" %self.FOLDER)
            self.LOGER.info("GARBAGE COLLECTOR: Cooldown - %s seconds" %self.STOPWATCH)

            sleep(self.STOPWATCH)

    def GarbageCollector(self):
        list_saved_solutions = self.PROPOSER.DirectRequest({},request="LIST_ALL_SOLUTIONS")['value'] #select
        # Extraer los valores de cada objeto en una nueva lista
        list_saved_solutions = [objeto['token_solution'] for objeto in list_saved_solutions]

        # Iterar sobre todos los archivos de la carpeta

        for nombre_archivo in os.listdir(self.FOLDER):
            ruta_archivo = os.path.join(self.FOLDER, nombre_archivo)
            if nombre_archivo in list_saved_solutions:
                self.LOGER.debug("solucion esta guardada")
            else:
                hora_modificacion = datetime.fromtimestamp(os.path.getmtime(ruta_archivo))
                # Obtener la hora actual
                hora_actual = datetime.now()
                # Calcular la diferencia de tiempo entre la hora de modificación y la hora actual
                diferencia_tiempo = hora_actual - hora_modificacion

                # Verificar si la diferencia de tiempo es menor a 1 hora (60 minutos)
                if diferencia_tiempo > timedelta(minutes=60):
                    self.LOGER.debug("solucion temporal detectada, toca borrarla")
                    try:
                        rmtree(ruta_archivo)
                    except NotADirectoryError as nadr:
                        os.remove(ruta_archivo)
                    