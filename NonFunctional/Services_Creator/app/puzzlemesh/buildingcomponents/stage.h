#ifndef STAGE_H
#define STAGE_H

#include <iostream>
#include <string>
#include <vector>
#include <thread>
#include <sstream>
#include <nlohmann/json.hpp>
#include <unordered_map>
#include <boost/algorithm/string/replace.hpp>
#include <dirent.h>

#include "../io/filesystem/files.h"
#include "buildingblock.h"
#include "pattern.h"
#include "single.h"
#include "../logs/logs.h"
#include "../ordered/ordered_map.h"
#include "../ordered/ordered_set.h"
#include "../skycds/Catalog.h"
#include "../skycds/APISkyCDS.h"

using namespace std;
using json = nlohmann::json;

class Stage : public BuildingBlock
{
private:
    vector<Stage*> previous;
    vector<Stage*> next;
    tsl::ordered_map<string, BuildingBlock *> bbs;
    vector<string> bbsStr;
    Catalog *catalog;
public:
    Stage():BuildingBlock(STAGE){};
    Stage(string name):BuildingBlock(name, STAGE){}

    Stage(string name, vector<string> sourcesStr, vector<string> sinksStr, vector<string> bbsStr)
    :BuildingBlock(name, STAGE, sourcesStr, sinksStr)
    {
      this->bbsStr = bbsStr;
    }

    Stage(string name, vector<Stage*> previous, vector<Stage*> next,
          tsl::ordered_map<string, BuildingBlock *> bbs, vector<string> sourcesStr,
          vector<string> sinksStr, vector<string> bbsStr)
    :BuildingBlock(name, STAGE, sourcesStr, sinksStr)
    {
        this->previous = previous;
        this->next = next;
        this->bbs = bbs;
        this->bbsStr = bbsStr;
    }

    void setPrevious(vector<Stage *> previous);
    void setNext(vector<Stage *> next);
    void setBBs(tsl::ordered_map<string, BuildingBlock *> bb);
    tsl::ordered_map<string, BuildingBlock *> getBBs();
    BuildingBlock* getBB(string name);
    void setBB(BuildingBlock* bb);
    void addPrevious(Stage *previous);
    void addNext(Stage *next);
    vector<Stage *> getNext();
    vector<Stage *> getPrevious();
    vector<string> getBBsStr();
    void execute(const string&,  const vector<string>& sourcesPaths, const string& compose_command, APISkyCDS *api, Catalog *father);
    bool hasBB(string name);
    string getDependencieDir(BuildingBlock* bb, string basedir);
    void uploadData(APISkyCDS *api, const string& workdirbase, Catalog *father);

    Catalog *getCatalog() const;

    void setCatalog(Catalog *catalog);

};
#endif
