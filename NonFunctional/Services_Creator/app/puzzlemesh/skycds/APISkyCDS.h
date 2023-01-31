//
// Created by domizzi on 07/06/21.
//

#ifndef PIECE_APISKYCDS_H
#define PIECE_APISKYCDS_H

#include<string>
#include <curl/curl.h>
#include <jsoncpp/json/json.h>
#include <jsoncpp/json/reader.h>
#include <jsoncpp/json/writer.h>
#include <jsoncpp/json/value.h>
#include "Curl.h"
#include <iostream>
#include <fstream>
#include <sstream>
#include "Catalog.h"
#include "CDNFile.h"

struct ResultPull
{
    std::vector<std::string> server;
    std::string key;
};

class APISkyCDS {
private:
    std::string tokenUser, accessToken, url, metadatURL, apikey;

public:
    APISkyCDS(const std::string &url, const std::string &metadatURL, const std::string &tokenUser, const std::string &accessToken, const std::string &apikey);

    Catalog* createCat(const std::string& name, const std::string& father="/", bool isCiphered=false);
    static Json::Value parseJSONStr(const std::string& jsonString);
    bool uploadFile(Catalog *catalog, std::string filename, const std::string& content);
    ResultPull pushContent(Catalog *catalog, std::string filename, size_t size);
    bool insertFile(const std::string& keyfile, const std::string& keyresource);
    std::string getFileInformation(const std::string& keyfile);
    std::vector<CDNFile*> getFiles(const std::string& keycatalog);
    std::vector<CDNFile*> downloadFiles(const std::string &keycatalog, const std::string& destPath);
    ResultPull getFileServer(std::string file, std::string catalog);
    FILE *  retrieve(const std::string& keyfile, const std::string& filename, const std::string& oName, const std::string& path, const std::string& catalog);
    bool sendFile(const std::string &urlServer, std::string filename, std::string content);

    const std::string &getTokenUser() const;

    void setTokenUser(const std::string &tokenUser);

    const std::string &getAccessToken() const;

    void setAccessToken(const std::string &accessToken);

    const std::string &getUrl() const;

    void setUrl(const std::string &url);

    const std::string &getMetadatUrl() const;

    void setMetadatUrl(const std::string &metadatUrl);

    const std::string &getApikey() const;

    void setApikey(const std::string &apikey);

    Catalog *getCatInfo(const std::string &tokenCat);
};


#endif //PIECE_APISKYCDS_H
