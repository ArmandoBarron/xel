
from requests.exceptions import ConnectionError
from requests.exceptions import MissingSchema
import logging
from ftplib import FTP
import os
import ftplib
import sys
# Perform the communication with the TPS manager
class FTP_API:
    def __init__(self, url, username="guess",password="guess"):
        self.base_url = url
        self.username = username
        self.password = password
        self.checkConnection()
        self.logger = logging.getLogger()


    # check if the service URL is valid or a service is available
    def checkConnection(self):
        """
        check if the service URL is valid or a service is available

        :raises ConnectionError: when it's not possible to connect to the URL provided
        """
        try:
            self.ftp=FTP(self.base_url)
            self.ftp.login(self.username,self.password)
            self.ftp.quit()
        except ConnectionError as e:
            raise ConnectionError("It is not possible connect to the URL %s" % self.base_url)
        except MissingSchema:
            raise ConnectionError("Bad URL %s" % self.base_url)

    def downloadFiles(self,source,destination):
    #path & destination are str of the form "/dir/folder/something/"
    #path should be the abs path to the root FOLDER of the file tree to download
        try:
            ftp=FTP(self.base_url)
            ftp.login(self.username,self.password)
            ftp.cwd(source)
            #clone path to destination
            self.logger.error("destination : "+destination)

            os.makedirs(destination, exist_ok=True)
            os.chdir(destination) #workflow schema
        except OSError:
            #folder already exists at destination
            self.logger.error("folder exist")
            pass
        except ftplib.error_perm:
            #invalid entry (ensure input form: "/dir/folder/something/")
            print ("error: could not change to "+source)
            sys.exit("ending session")

        #list children:
        filelist=ftp.nlst()
        ftp.quit()

        for file in filelist:
            try:
                ftp=FTP(self.base_url)
                ftp.login(self.username,self.password)
                ftp.cwd(source)
                #this will check if file is folder:
                ftp.cwd(file+"/")
                #self.ftp.cwd("..")
                #if so, explore it:
                ftp.quit()
                self.downloadFiles(source+"/"+file+"/",destination+"/"+file+"/")
            except ftplib.error_perm:

                #not a folder with accessible content
                #download & return
                os.chdir(destination)
                #possibly need a permission exception catch:
                ftp.retrbinary("RETR "+file, open(os.path.join(destination,file),"wb").write)
                print (file + " downloaded")
                ftp.quit()

        return

