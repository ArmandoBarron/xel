#include "logs.h"

using namespace std;

string getCurrentDateTime( string s ){
    time_t now = time(0);
    struct tm  tstruct;
    char  buf[80];
    tstruct = *localtime(&now);
    if(s=="now")
        strftime(buf, sizeof(buf), "%Y-%m-%d %X", &tstruct);
    else if(s=="date")
        strftime(buf, sizeof(buf), "%Y-%m-%d", &tstruct);
    return string(buf);
}

void Logger( string logMsg, bool verbose ){

    string filePath =  "logs/log_"+getCurrentDateTime("now")+".txt";
    string now = getCurrentDateTime("now");
    ofstream ofs(filePath.c_str(), std::ios_base::out | std::ios_base::app );
    ofs << now << '\t' << logMsg << '\n';
    if (verbose) cout << now << '\t' << logMsg << '\n';
    ofs.close();
}
