
from requests.exceptions import ConnectionError
from requests.exceptions import MissingSchema
import logging
import ftplib
from ftplib import FTP, error_perm
import os
import sys
# Perform the communication with the TPS manager
class FTP_API:
    def __init__(self, url, username="guess",password="guess"):
        self.base_url = url
        self.username = username
        self.password = password
        self.checkConnection()
        self.logger = logging.getLogger()
        self.CWD = os.getcwd()

    def Fix(self):
        os.chdir(self.CWD)
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

    def downloadFiles(self,source,destination,file_to_downlaod = None):
    #path & destination are str of the form "/dir/folder/something/"
    #path should be the abs path to the root FOLDER of the file tree to download
        try:
            ftp=FTP(self.base_url)
            ftp.login(self.username,self.password)
            ftp.cwd(source)
            #clone path to destination
            self.logger.error("FTP SORUCE : "+source)
            self.logger.error("FTP destination : "+destination)

            os.makedirs(destination, exist_ok=True)
            #os.chdir(destination) #workflow schema
        except OSError:
            #folder already exists at destination
            self.logger.error("FTP folder exist")
            pass
        except error_perm:
            #invalid entry (ensure input form: "/dir/folder/something/")
            print ("error: could not change to "+source)
            sys.exit("ending session")

        #list children:
        filelist=ftp.nlst()
        ftp.quit()
        if file_to_downlaod is not None: #if only a file must be downloaded
            file2download = file_to_downlaod
            self.logger.error("FTP FILE 2 downlaod : "+file2download)

            ftp=FTP(self.base_url)
            ftp.login(self.username,self.password)
            ftp.cwd(source)
            try:
                ftp.retrbinary("RETR "+file2download, open(os.path.join(destination,file2download),"wb").write)
                print (file2download + " downloaded")
            except error_perm as er:
                print("ignoring symbolic links")
            ftp.quit()
            return

        for file in filelist:
            try:
                ftp=FTP(self.base_url)
                ftp.login(self.username,self.password)
                ftp.cwd(source)

                #this will check if file is folder:
                ftp.cwd(file+"/")
                #if so, explore it:
                ftp.quit()
                self.downloadFiles(source+"/"+file+"/",destination+"/"+file+"/")
            except error_perm:

                #not a folder with accessible content
                #download & return
                #os.chdir(destination)
                #possibly need a permission exception catch:
                try:
                    ftp.retrbinary("RETR "+file, open(os.path.join(destination,file),"wb").write)
                    print (file + " downloaded")
                except error_perm:
                    print("ignoring symbolic links")
                ftp.quit()

        return

