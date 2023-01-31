//
// Created by domizzi on 07/06/21.
//

#include "APISkyCDS.h"

APISkyCDS::APISkyCDS(const std::string &url, const std::string &metadatURL, const std::string &tokenUser,
                     const std::string &accessToken, const std::string &apikey) :
                     url(url), tokenUser(tokenUser), accessToken(accessToken) {
    this->tokenUser = tokenUser;
    this->accessToken = accessToken;
    this->url = url;
    this->metadatURL = metadatURL;
    this->apikey = apikey;
}

Json::Value APISkyCDS::parseJSONStr(const std::string& jsonString){

    Json::CharReaderBuilder builder;
    Json::CharReader* reader = builder.newCharReader();

    Json::Value json;
    std::string errors;

    bool parsingSuccessful = reader->parse(
            jsonString.c_str(),
            jsonString.c_str() + jsonString.size(),
            &json,
            &errors
    );
    delete reader;

    if (!parsingSuccessful) {
        std::cout << "Failed to parse the JSON, errors:" << std::endl;
        std::cout << errors << std::endl;
        throw "Failed to parse the JSON" + errors;
    }
    return json;
}

Catalog* APISkyCDS::createCat(const std::string& name, const std::string& fatherToken, bool isCiphered) {
    const std::string json = "{ \"catalogname\": \" " + name + " \", \"dispersemode\": \"IDA\", \"encryption\":\""+
            (isCiphered ? "true" : "false") +"\", \"fathers_token\":\""+fatherToken+"\", \"processed\": \"true\" }";

    std::cout << json << std::endl;
    std::string serviceURL = this->url + "/pub_sub/v1/catalogs/create?access_token=" + this->accessToken;
    std::cout << serviceURL << std::endl;
    Catalog *c = nullptr;
    try{
        std::string result = Curl::doPost(serviceURL, json);
        Json::Value json = this->parseJSONStr(result);
//        std::cout << result << std::endl;
        if(json.isMember("tokencatalog")) {
            c = new Catalog(name, json.get("tokencatalog", "default value").asString());
        }else{
            throw json.get("message", "default value").asString();
        }
    } catch (const std::string& ex) {
        std::cout << ex << std::endl;
    }

    return c;
}



bool APISkyCDS::uploadFile(Catalog *catalog, std::string filename, const std::string& content) {
    //std::string serviceURL = this->url + "/pub_sub/v1/catalogs/create?access_token=" + this->accessToken;
    std::ofstream out_file(filename, std::ios_base::out | std::ios_base::binary);
    out_file << content;

//    FILE *stream;
//    char *buf, aux[content.size()];
//    size_t len;
//    ssize_t bytes_written;
//
//    stream = open_memstream (&buf, &len);
//
//    if (stream == NULL) {
//        /* handle error */;
//        throw "Error writing stream";
//    }
//    content.copy(aux,content.size());
////    bytes_written = write(fd, buf, nbytes);
//    fprintf (stream,  "%s", aux);
////    fwrite(content.data(),sizeof(char),sizeof(content.size()),stream);
//    fflush (stream);
//    std::cout << content.size()<< "   " << strlen(aux)<< std::endl;
//    printf ("buf=%s, len=%zu\n", buf, len);

//    stream = fmemopen(buffer, sizeof (buffer), "w+");createCat
//    std::cout << content.size() << std::endl;
//    int nbytes = fprintf(stream,"%s", content.data());
//    printf("+%u bytes: buf=%s\n",nbytes, buffer);
//    printf("%s\n", content.data());
//    if (stream == NULL) {
//        /* handle error */;
//        throw "Error writing stream";
//    }
    ResultPull resultPull = pushContent(catalog, filename, content.size());
    bool status = sendFile(resultPull.server[0], filename, content);
//    fclose(stream);
    if (status){
        return insertFile(resultPull.key, catalog->getToken());
    }

    return false;
}

ResultPull APISkyCDS::pushContent(Catalog *catalog, std::string filename, size_t size) {
    std::string serviceURL = this->metadatURL + "/push.php?tokenuser=" + this->tokenUser + "&keyresource=" + catalog->getToken()
                                                                  + "&namefile=" + filename
                                                                  + "&sizefile=" + std::to_string(size)
                                                                    + "&dispersemode=SINGLE&isciphered=false";
    std::vector<std::string> routes;
    std::string key;

    try{
        std::string result = Curl::doGet(serviceURL);
        Json::Value json = this->parseJSONStr(result);
        int status = stoi(json.get("status", "default value").asString());

        if (status == 200){
            Json::Value value = json.get("message","default value");
            for (Json::Value::ArrayIndex i = 0; i != value.size(); i++){
                if (value[i].isMember("ruta"))
                    routes.push_back(value[i]["ruta"].asString());
            }
//            std::cout << result << std::endl;
            key = json.get("key","default value")[0]["ruta"].asString();
//            std::cout << "key  " << key << std::endl;
            key = key.substr(key.find_last_of("//") + 1);
//            std::cout << "key  " << key << std::endl;
        }
//       std::cout << result << std::endl;

    } catch (const std::string& ex) {
        std::cout << ex << std::endl;
    }
    ResultPull result = {routes, key};
    return result;
}

bool APISkyCDS::sendFile(const std::string& urlServer, std::string filename, std::string content) {
    std::stringstream ss;
    std::string urlService = urlServer + "&tokenuser=" + this->tokenUser;
//    std::cout << urlService << std::endl;
    try{
        std::string result = Curl::uploadFileFS(urlService,filename, content);
        Json::Value json = this->parseJSONStr(result);
        int status = stoi(json.get("status", "default value").asString());
        return status == 200;
//        std::cout << result << std::endl;

    } catch (const std::string& ex) {
        std::cout << ex << std::endl;
    }
    return false;
}

//bool APISkyCDS::sendFile(FILE* file, const std::string& urlServer) {
//    std::stringstream ss;
//    std::string urlService = urlServer + "&tokenuser=" + this->tokenUser;
////    std::cout << urlService << std::endl;
//    try{
//        std::string result = Curl::uploadFileGet(urlService, file, "test");
//        Json::Value json = this->parseJSONStr(result);
//        int status = stoi(json.get("status", "default value").asString());
//        return status == 200;
////        std::cout << result << std::endl;
//
//    } catch (const std::string& ex) {
//        std::cout << ex << std::endl;
//    }
//    return false;
//}

bool APISkyCDS::insertFile(const std::string& keyfile, const std::string& keyresource) {
    std::string urlService = this->metadatURL + "/push_insert.php?"  +
                                                 + "tokenuser=" + this->tokenUser
                                                 + "&keyresource=" + keyresource
                                                 + "&keyfile=" + keyfile;
    try{
        std::string result = Curl::doGet(urlService);
        Json::Value json = this->parseJSONStr(result);
        int status = stoi(json.get("status", "default value").asString());
        return status == 200;
//        std::cout << result << std::endl;

    } catch (const std::string& ex) {
        std::cout << ex << std::endl;
    }

    return false;
}



std::string APISkyCDS::getFileInformation(const std::string &keyfile) {
    std::string urlService = this->metadatURL +"/file.php?"+
                             "tokenuser="+this->tokenUser+
                             "&keyfile="+keyfile;
    std::string files;
    try{
        std::string result = Curl::doGet(urlService);
        Json::Value json = this->parseJSONStr(result);
        int status = stoi(json.get("status", "default value").asString());
        if(status == 200){
            files = json.get("message", "default value").asString();
        }
//        std::cout << files << std::endl;

    } catch (const std::string& ex) {
        std::cout << ex << std::endl;
    }
    return files;
}

std::vector<CDNFile*> APISkyCDS::downloadFiles(const std::string &keycatalog, const std::string& destPath){
    std::vector<CDNFile*> files = getFiles(keycatalog);
    int i=0;
//    std::cout << files.size() << std::endl;
    std::vector<FILE*> retrieved;
    for(i=0;i<files.size();i++){
        files[i]->setPath(destPath + "/" + files[i]->getName());
        //std::cout << files[i]->getId() << std::endl;
        ResultPull rp = this->getFileServer(files[i]->getId(), keycatalog);
        retrieve(rp.server[0], files[i]->getName(),  files[i]->getPath(), files[i]->getPath(), keycatalog);
//        FILE* fileDown =retrieve(rp.server[0], files[i]->getName(), files[i]->getName(), files[i]->getPath(), keycatalog);
//        retrieved.push_back(fileDown);
    }

    return files;
}

std::vector<CDNFile*> APISkyCDS::getFiles(const std::string &keycatalog) {
    std::vector<CDNFile*> files;
    std::string  urlService = this->url + "/pub_sub/v1/view/files/catalog/" + keycatalog + "?access_token=" + this->accessToken;
    try{
        std::string result = Curl::doGet(urlService);
        Json::Value json = this->parseJSONStr(result);
        if (json.isMember("data")){
            Json::Value data = json.get("data", "default value");
            for (Json::Value::ArrayIndex i = 0; i != data.size(); i++){
                if (data[i].isMember("keyfile")){
//                    std::cout << data[i]["keyfile"].asString() << std::endl;
                    CDNFile *cf = new CDNFile(data[i]["keyfile"].asString(), data[i]["namefile"].asString(), atol(data[i]["sizefile"].asString().c_str()), atoi(data[i]["chunks"].asString().c_str()));
                    cf->setPath(cf->getName());
                    files.push_back(cf);
                }
            }
        }
    } catch (const std::string& ex) {
        std::cout << ex << std::endl;
    }
//    std::cout << files.size() << std::endl;
    return files;
}

ResultPull APISkyCDS::getFileServer(std::string file, std::string catalog) {
    std::string serverURL = this->metadatURL +"/pull.php?"+
                            "tokenuser="+ this->tokenUser +
                            "&keyresource="+ catalog +
                            "&keyfile="+ file +
                            "&dispersemode=SINGLE";
    std::vector<std::string> routes;
//    std::cout <<serverURL << std::endl;
    std::string key;
    try{
        std::string result = Curl::doGet(serverURL);
//        std::cout << result << std::endl;
        Json::Value json = this->parseJSONStr(result);
        int status = stoi(json.get("status", "default value").asString());
        if(status == 200){
            Json::Value data = json.get("message", "default value");
            for (Json::Value::ArrayIndex i = 0; i != data.size(); i++){
                if (data[i].isMember("ruta")){
                    routes.push_back(data[i]["ruta"].asString());
                }
                key = json.get("key", "default value")[0]["ruta"].asString();
            }
        }
    } catch (const std::string& ex) {
        std::cout << "AA" << ex << std::endl;
    }
    ResultPull result = {routes, key};
    return result;
}

FILE * APISkyCDS::retrieve(const std::string& keyfile, const std::string& filename, const std::string& oName, const std::string& path, const std::string& catalog){
//    std::ofstream outfile(path + "/" + oName,std::ios_base::out | std::ios_base::binary);
//    std::cout << keyfile << std::endl;
    FILE *f;
    try{
        f = Curl::downloadFile(keyfile, oName);
    } catch (const std::string& ex) {
        std::cout << ex << std::endl;
    }
    return f;
}

Catalog * APISkyCDS::getCatInfo(const std::string& tokenCat){
    std::string serverURL = this->url  + "/pub_sub/v1/view/catalog/" + tokenCat + "?access_token=" + this->accessToken;
    try{
        std::string result = Curl::doGet(serverURL);
//        std::cout << result << std::endl;
        Json::Value json = this->parseJSONStr(result);

        if(json.isMember("data")){
            Json::Value data = json.get("data", "default value");
//            std::cout << data.asString() << std::endl;
//            if(data.isMember("ketcatalog")){
//                std::cout << "entro" <<std::endl;
                auto *c = new Catalog(data.get("namecatalog", "default value").asString(), data.get("tokencatalog", "default value").asString());
                return c;
//            }

        }
    } catch (const std::string& ex) {
        std::cout << "AA" << ex << std::endl;
    }
    return nullptr;
}

const std::string &APISkyCDS::getTokenUser() const {
    return tokenUser;
}

void APISkyCDS::setTokenUser(const std::string &tokenUser) {
    APISkyCDS::tokenUser = tokenUser;
}

const std::string &APISkyCDS::getAccessToken() const {
    return accessToken;
}

void APISkyCDS::setAccessToken(const std::string &accessToken) {
    APISkyCDS::accessToken = accessToken;
}

const std::string &APISkyCDS::getUrl() const {
    return url;
}

void APISkyCDS::setUrl(const std::string &url) {
    APISkyCDS::url = url;
}

const std::string &APISkyCDS::getMetadatUrl() const {
    return metadatURL;
}

void APISkyCDS::setMetadatUrl(const std::string &metadatUrl) {
    metadatURL = metadatUrl;
}

const std::string &APISkyCDS::getApikey() const {
    return apikey;
}

void APISkyCDS::setApikey(const std::string &apikey) {
    APISkyCDS::apikey = apikey;
}


