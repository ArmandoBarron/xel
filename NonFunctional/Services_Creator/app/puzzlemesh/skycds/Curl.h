//
// Created by domizzi on 07/06/21.
//

#ifndef PIECE_CURL_H
#define PIECE_CURL_H

#include<string>
#include <curl/curl.h>
#include <stdexcept>
#include <cstring>
#include <sys/stat.h>
#include <iostream>
#include <filesystem>
#include <fstream>
#define DATA_SIZE 10



struct MemoryStruct {
    char *memory;
    size_t size;
};

struct data {
    char trace_ascii; /* 1 or 0 */
};

class Curl {
public:
    int Curr_index ;
    static std::string doPost(const std::string& url, const std::string& inputJson);
    static std::string doGet(const std::string& url);

    static std::string uploadFileGet(const std::string &url, FILE *file, std::string filename);
    static FILE * downloadFile(const std::string &url, const std::string &filename);
//    static std::string uploadFileFS(const std::string &url, std::string filename);

    static std::string uploadFileFS(const std::string &url, std::string filename, std::string content);
};


#endif //PIECE_CURL_H
