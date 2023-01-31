//
// Created by domizzi on 07/06/21.
//

#include "Curl.h"

static size_t
WriteMemoryCallback(void *contents, size_t size, size_t nmemb, void *userp)
{
    size_t realsize = size * nmemb;
    struct MemoryStruct *mem = (struct MemoryStruct *)userp;

    char *ptr = static_cast<char *>(realloc(mem->memory, mem->size + realsize + 1));
    if(!ptr) {
        /* out of memory! */
        printf("not enough memory (realloc returned NULL)\n");
        return 0;
    }

    mem->memory = ptr;
    memcpy(reinterpret_cast<wchar_t *>(&(mem->memory[mem->size])), contents, realsize);
    mem->size += realsize;
    mem->memory[mem->size] = 0;

    return realsize;
}

std::string Curl::doPost(const std::string& url, const std::string& inputJson) {
    CURL *curl;
    CURLcode res;

    curl_global_init(CURL_GLOBAL_ALL);
    curl = curl_easy_init();

    if (curl == nullptr) {
        throw "CURL error 128";
    }

    struct MemoryStruct chunk{};

    chunk.memory = static_cast<char *>(malloc(1));  /* will be grown as needed by the realloc above */
    chunk.size = 0;    /* no data at this point */

    struct curl_slist *headers = nullptr;
    curl_slist_append(headers, "Accept: application/json");
    curl_slist_append(headers, "Content-Type: application/json");
    curl_slist_append(headers, "charset: utf-8");

    curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteMemoryCallback);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, (void *)&chunk);
    curl_easy_setopt(curl, CURLOPT_CUSTOMREQUEST, "POST");
    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
    curl_easy_setopt(curl, CURLOPT_POSTFIELDS, inputJson.c_str());
    curl_easy_setopt(curl, CURLOPT_USERAGENT, "libcurl-agent/1.0");

    res = curl_easy_perform(curl);

    /* check for errors */
    if(res != CURLE_OK) {
        throw "curl_easy_perform() failed: " + std::string(curl_easy_strerror(res));
    }

    curl_easy_cleanup(curl);
    curl_global_cleanup();

    return chunk.memory;
}

std::string Curl::doGet(const std::string &url) {
    CURL *curl;
    CURLcode res;

    curl_global_init(CURL_GLOBAL_ALL);
    curl = curl_easy_init();

    if (curl == nullptr) {
        throw "CURL error 128";
    }

    struct MemoryStruct chunk{};

    chunk.memory = static_cast<char *>(malloc(1));  /* will be grown as needed by the realloc above */
    chunk.size = 0;    /* no data at this point */

    struct curl_slist *headers = nullptr;
    curl_slist_append(headers, "Accept: application/json");
    curl_slist_append(headers, "Content-Type: application/json");
    curl_slist_append(headers, "charset: utf-8");

    curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteMemoryCallback);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, (void *)&chunk);
    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
    curl_easy_setopt(curl, CURLOPT_USERAGENT, "libcurl-agent/1.0");

    res = curl_easy_perform(curl);

    /* check for errors */
    if(res != CURLE_OK) {
        throw "curl_easy_perform() failed: " + std::string(curl_easy_strerror(res));
    }

    curl_easy_cleanup(curl);
    curl_global_cleanup();

    return chunk.memory;
}


std::string Curl::uploadFileGet(const std::string &url, FILE* file, std::string filename) {
    CURL *curl;
    CURLcode res;

    struct curl_httppost *formpost = nullptr;
    struct curl_httppost *lastptr = nullptr;
    struct curl_slist *headerlist = nullptr;
    static const char buf[] =  "Expect:";

    struct MemoryStruct chunk{};

    fseek(file, 0, SEEK_END); // seek to end of file
    size_t size = ftell(file); // get current file pointer
    fseek(file, 0, SEEK_SET); // seek back to beginning of file

    curl_global_init(CURL_GLOBAL_ALL);

    // set up the header
    curl_formadd(&formpost,
                 &lastptr,
                 CURLFORM_COPYNAME, "cache-control:",
                 CURLFORM_COPYCONTENTS, "no-cache",
                 CURLFORM_END);

    curl_formadd(&formpost,
                 &lastptr,
                 CURLFORM_COPYNAME, "content-type:",
                 CURLFORM_COPYCONTENTS, "multipart/form-data",
                 CURLFORM_END);

    curl_formadd(&formpost, &lastptr,
                 CURLFORM_COPYNAME, "uploadedfile",  // <--- the (in this case) wanted file-Tag!
                 CURLFORM_BUFFER, "data",
                 CURLFORM_BUFFERPTR, file,
                 CURLFORM_BUFFERLENGTH, size,
                 CURLFORM_END);

    curl = curl_easy_init();

    headerlist = curl_slist_append(headerlist, buf);
    if (curl) {

        curl_easy_setopt(curl, CURLOPT_URL, url.c_str());

        curl_easy_setopt(curl, CURLOPT_HTTPPOST, formpost);
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteMemoryCallback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, (void *)&chunk);
        //curl_easy_setopt(curl, CURLOPT_VERBOSE, 1L);

        res = curl_easy_perform(curl);
        /* Check for errors */
        if (res != CURLE_OK)
            fprintf(stderr, "curl_easy_perform() failed: %s\n",
                    curl_easy_strerror(res));


        curl_easy_cleanup(curl);


        curl_formfree(formpost);

        curl_slist_free_all(headerlist);
    }
    return chunk.memory;;

}


std::string Curl::uploadFileFS(const std::string &url, std::string filename, std::string content) {
    CURL *curl;
    CURLcode res;

    struct curl_httppost *formpost = nullptr;
    struct curl_httppost *lastptr = nullptr;
    struct curl_slist *headerlist = nullptr;
    static const char buf[] =  "Expect:";

    struct MemoryStruct chunk{};
//    std::string contents;
    std::ifstream in( "/home/domizzi/Documents/BERNOULLI/v2_final/piece/cmake-build-debug/0_W0x0_test.txt", std::ios::in | std::ios::binary);

//    if (in)
//    {
//        in.seekg(0, std::ios::end);
//        contents.resize(in.tellg());
//        in.seekg(0, std::ios::beg);
//        in.read(&contents[0], contents.size());
//        in.close();
//    }

    std::string contents( (std::istreambuf_iterator<char>(in) ),
                         (std::istreambuf_iterator<char>()    ) );


//    fseek(file, 0, SEEK_END); // seek to end of file
//    size_t size = ftell(file); // get current file pointer
//    fseek(file, 0, SEEK_SET); // seek back to beginning of file

    curl_global_init(CURL_GLOBAL_ALL);
//    std::cout  << "aaaa" << contents << std::endl;
    // set up the header
    curl_formadd(&formpost,
                 &lastptr,
                 CURLFORM_COPYNAME, "cache-control:",
                 CURLFORM_COPYCONTENTS, "no-cache",
                 CURLFORM_END);

    curl_formadd(&formpost,
                 &lastptr,
                 CURLFORM_COPYNAME, "content-type:",
                 CURLFORM_COPYCONTENTS, "multipart/form-data",
                 CURLFORM_END);

    //std::cout << "SIZEEEE "  << filename << "\t" << content.size() << std::endl;

    curl_formadd(&formpost, &lastptr,
                 CURLFORM_COPYNAME, "uploadedfile",  // <--- the (in this case) wanted file-Tag!
                 CURLFORM_BUFFER, "data",
                 CURLFORM_BUFFERPTR, content.data(),
                 CURLFORM_BUFFERLENGTH, content.size(),
                 CURLFORM_END);

    curl = curl_easy_init();

    headerlist = curl_slist_append(headerlist, buf);
    if (curl) {

        curl_easy_setopt(curl, CURLOPT_URL, url.c_str());

        curl_easy_setopt(curl, CURLOPT_HTTPPOST, formpost);
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteMemoryCallback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, (void *)&chunk);
        //curl_easy_setopt(curl, CURLOPT_VERBOSE, 1L);

        res = curl_easy_perform(curl);
        /* Check for errors */
        if (res != CURLE_OK)
            fprintf(stderr, "curl_easy_perform() failed: %s\n",
                    curl_easy_strerror(res));


        curl_easy_cleanup(curl);


        curl_formfree(formpost);

        curl_slist_free_all(headerlist);
    }
    return chunk.memory;;

}

static size_t write_data(void *ptr, size_t size, size_t nmemb, void *stream)
{
    size_t written = fwrite(ptr, size, nmemb, (FILE *)stream);
    return written;
}

FILE *Curl::downloadFile(const std::string &url, const std::string &filename) {
    CURL *curl_handle;
    FILE *pagefile;
    curl_global_init(CURL_GLOBAL_ALL);

    /* init the curl session */
    curl_handle = curl_easy_init();

    /* set URL to get here */
    curl_easy_setopt(curl_handle, CURLOPT_URL, url.c_str());

    /* Switch on full protocol/debug output while testing */
//    curl_easy_setopt(curl_handle, CURLOPT_VERBOSE, 1L);

    /* disable progress meter, set to 0L to enable it */
    curl_easy_setopt(curl_handle, CURLOPT_NOPROGRESS, 1L);

    /* send all data to this function  */
    curl_easy_setopt(curl_handle, CURLOPT_WRITEFUNCTION, write_data);

    /* open the file */
//    pagefile = fopen(pagefilename, "wb");
    char *buf;
    size_t len;
//    pagefile = open_memstream (&buf, &len);
//    std::cout << filename.c_str() << std::endl;
//    std::cout << std::filesystem::current_path() << std::endl;
//    std::string filename2 = std::filesystem::current_path().string() + filename;
    pagefile =  fopen(filename.c_str(), "wb");
    if(pagefile) {
//        std::cout << "ENTROOO" << std::endl;
        /* write the page body to this file handle */
        curl_easy_setopt(curl_handle, CURLOPT_WRITEDATA, pagefile);

        /* get it! */
        curl_easy_perform(curl_handle);

        /* close the header file */
        fclose(pagefile);
    }

    /* cleanup curl stuff */
    curl_easy_cleanup(curl_handle);

    curl_global_cleanup();
//    std::cout << "aaa" << len << std::endl;
    return pagefile;
}
