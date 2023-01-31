#ifndef BB_H
#define BB_H

#include <iostream>
#include <string>
#include <ctime>
#include <sstream>
#include <sys/stat.h>

#include "../logs/logs.h"
#include "../ordered/ordered_map.h"

using namespace std;

//States in a building block
enum State {WORKING = 2, FAILED = 0, WAITING = 1, COMPLETED = 3};

//Types of building BLOCKS
enum Type {WORKFLOW = 0, STAGE = 1, PIPELINE = 2, PATTERN = 3, SINGLE = 4};

class BuildingBlock
{
protected:
    tsl::ordered_map<string, BuildingBlock *> sources;
    tsl::ordered_map<string, BuildingBlock *> sinks;
    vector<string> sourcesStr;
    vector<string> sinksStr;
    Type type;
    string name;
    State state;
    string workdir;
    string memory, limit_mem, cpus;
    int *ptr;
public:
    BuildingBlock()
    {
      this->state = WAITING;
    }

    BuildingBlock(Type type)
    {
      this->state = WAITING;
      this->type = type;
    }

    BuildingBlock(string name, Type type)
    {
        this->name = name;
        this->state = state;
        this->type = type;
        this->state = WAITING;
    }

    BuildingBlock(string name, Type type, vector<string> sourcesStr, vector<string> sinksStr)
    {
        this->name = name;
        this->state = state;
        this->type = type;
        this->state = WAITING;
        this->sourcesStr = sourcesStr;
        this->sinksStr = sinksStr;
    }

    BuildingBlock(string name, Type type, tsl::ordered_map<string, BuildingBlock *> sources,
          tsl::ordered_map<string, BuildingBlock *> sinks)
    {
        this->name = name;
        this->state = state;
        this->type = type;
        this->state = WAITING;
        this->sources = sources;
        this->sinks = sinks;
    }

    void setSource(tsl::ordered_map<string, BuildingBlock *> source);
    void setSink(tsl::ordered_map<string, BuildingBlock *> sink);
    void addSource(BuildingBlock* source);
    void addSink(BuildingBlock* sink);
    void setSourceStr(vector<string> sourceStr);
    void setSinkStr(vector<string> sinkStr);
    void addSourceStr(string sourceStr);
    void addSinkStr(string sinkStr);
    void setType(Type type);
    void setState(State state);
    void setName(string name);
    tsl::ordered_map<string, BuildingBlock *> getSource();
    tsl::ordered_map<string, BuildingBlock *> getSink();
    BuildingBlock* getSource(string name);
    BuildingBlock* getSink(string name);
    vector<string> getSourceStr();
    vector<string> getSinkStr();
    vector<string> getPorts();
    Type getType();
    State getState();
    string getName();
    void setWorkdir(string workdir);
    string getWorkdir();
    string createWorkdir(string basedir);
    void execute(string workdirbase, vector<string> sourcesPaths);
    string exec_cmd(const char *cmd);
    bool hasBB(BuildingBlock *target);
};
#endif
