#ifndef PATTERN_H
#define PATTERN_H

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
using json = nlohmann::json;

class Pattern : public BuildingBlock
{
private:
    int nWorkers;
    string loadBalancer;
    string pattern;
    string lbmode;
    Single *worker;

public:
    Pattern():BuildingBlock(PATTERN){};

    Pattern(string name, int nWorkers, string loadBalancer, string lbmode, string pattern,
            Single *worker, vector<string> sourcesStr, vector<string> sinksStr)
    :BuildingBlock(name, PATTERN, sourcesStr, sinksStr)
    {
        this->nWorkers = nWorkers;
        this->loadBalancer = loadBalancer;
        this->pattern = pattern;
        this->worker = worker;
        this->lbmode = lbmode;
    }

    Pattern(string name, int nWorkers, string loadBalancer, string lbmode, string pattern,
            Single *worker, tsl::ordered_map<string, BuildingBlock *> sources,
            tsl::ordered_map<string, BuildingBlock *> sinks)
    :BuildingBlock(name, PATTERN, sources, sinks)
    {
        this->nWorkers = nWorkers;
        this->loadBalancer = loadBalancer;
        this->pattern = pattern;
        this->worker = worker;
        this->lbmode = lbmode;
    }

    void setNWorkers(int nWorkers);
    void setLB(string loadBalancer);
    void setPattern(string pattern);
    void setWorker(Single* worker);
    int getNWorkers();
    string getLB();
    string getPattern();
    Single* getWorker();
    void execute(string workdirbase, vector<string> sourcesPaths, string compose_command);
};
#endif
