#ifndef PIPELINE_H
#define PIPELINE_H

#include <iostream>
#include <string>
#include <vector>
#include <thread>
#include <nlohmann/json.hpp>
#include <chrono>
#include <unistd.h>
#include <future>

#include "buildingblock.h"
#include "single.h"

using namespace std;

class Pipeline : public BuildingBlock
{
private:
    vector<Single*> stages;
public:
    Pipeline():BuildingBlock(PIPELINE){};

    Pipeline(string name, vector<Single*> stages,  vector<string> sourcesStr,
             vector<string> sinksStr)
    :BuildingBlock(name, PIPELINE, sourcesStr, sinksStr)
    {
        this->stages = stages;
    }

    Pipeline(string name, vector<Single*> stages,  tsl::ordered_map<string, BuildingBlock *> sources,
          tsl::ordered_map<string, BuildingBlock *> sinks)
    :BuildingBlock(name, PIPELINE, sourcesStr, sinksStr)
    {
        this->stages = stages;
    }

    void setStages(vector<Single*> stages);
    vector<Single*> getStages();
    void execute(string workdirbase, vector<string> sourcesPaths, string compose_command);
};

#endif
