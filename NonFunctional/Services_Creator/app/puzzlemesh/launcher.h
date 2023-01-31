#ifndef LAUNCHER_H
#define LAUNCHER_H

#include <unordered_map>
#include <string>
#include <boost/algorithm/string.hpp>
#include <iostream>
#include <fstream>
#include <sstream>
#include <thread>
#include <algorithm>
#include <set>
#include<filesystem>

#include "functions/stringfunctions.h"

#include "buildingcomponents/workflow.h"
#include "buildingcomponents/buildingblock.h"
#include "buildingcomponents/single.h"
#include "buildingcomponents/pattern.h"
#include "buildingcomponents/stage.h"
#include "logs/logs.h"
#include "io/filesystem/files.h"

using namespace std;
namespace fs = std::filesystem;

class Launcher
{
private:
    unordered_map<string, Single *> singles;
    unordered_map<string, Pattern *> patterns;
    unordered_map<string, Stage *> stages;
    unordered_map<string, BuildingBlock *> bbs;
    Workflow *workflow;
    string workpath;
    string filename;
public:
    Launcher(){};
    Launcher(Workflow *workflow, unordered_map<string, Single *> singles,
            unordered_map<string, Pattern *> patterns,
            unordered_map<string, Stage *> stages,
            unordered_map<string, BuildingBlock *> bbs, std::string filename)
    {
        this->singles = singles;
        this->patterns = patterns;
        this->stages = stages;
        this->workflow = workflow;
        this->bbs = bbs;
        this->filename = filename;
        this->workpath = std::getenv("HOST_PATH") == nullptr ? pwd() : std::getenv("HOST_PATH");
    };

    void start(string mode);
    void buildYML(string mode);
    void coupling();
    void prepareBB(BuildingBlock* bb, string basedir);
    void getVolumes(BuildingBlock* b, string target, set<vector<string>> &volumes);
    void execute(string mode);
    void printJSON(string);
    bool downloadData(string apikey, string token, string access);
    bool uploadData(string apikey, string token, string access);
    void printMonitoringFile(vector<string> id_containers);
    void generateNormas(std::string json_file);

    string getFilename() const { return filename; }
    void setFilename(const string &filename_) { filename = filename_; }
};

#endif
