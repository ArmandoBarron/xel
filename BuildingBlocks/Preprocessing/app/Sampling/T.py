import os
def execute(args):
    filepath = args[0]
    filename = args[1]
    destination = args[2]
    os.system('Rscript T.r "'+filepath+'" "'+filename+'" "'+destination+'"')