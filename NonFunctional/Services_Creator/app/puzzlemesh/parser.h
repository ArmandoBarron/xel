#ifndef PARSER_H
#define PARSER_H

#include <iostream>
#include <iomanip>
#include <fstream>
#include <string>
#include <list>
#include <fstream>
#include <unordered_map>
#include <boost/algorithm/string/replace.hpp>
#include <boost/filesystem.hpp>

#include "buildingcomponents/workflow.h"
#include "buildingcomponents/buildingblock.h"
#include "functions/stringfunctions.h"
#include "buildingcomponents/single.h"
#include "buildingcomponents/pattern.h"
#include "buildingcomponents/stage.h"
#include "logs/logs.h"
#include "skycds/APISkyCDS.h"

using namespace std;

class ConfigParser
{
private:
    unordered_map<string, BuildingBlock *> bbs;
    unordered_map<string, Single *> singles;
    unordered_map<string, Pattern *> patterns;
    unordered_map<string, Stage *> stages;
    Workflow* workflow;
    string workpath;
public:
    ConfigParser()
    {
        this->workpath = std::getenv("HOST_PATH") == nullptr ? pwd() : std::getenv("HOST_PATH");
    };
    int readConfig(string filePath,  string apikey,  string token, string access);
    unordered_map<string, Single *> searchSingles(vector<string> lines);
    unordered_map<string, Pattern *> searchPatterns(vector<string> lines, unordered_map<string, Single *> singles);
    unordered_map<string, Stage *> searchStages(vector<string> lines, unordered_map<string, Single *> singles, unordered_map<string, Pattern *> patterns);
    unordered_map<string, Single *> getSingles();
    unordered_map<string, Pattern *> getPatterns();
    unordered_map<string, BuildingBlock *> getBBs();
    unordered_map<string, Stage *> getStages();
    Workflow* searchWorkflow(vector<string> lines);
    Workflow * getWorkflow();
};

#endif
