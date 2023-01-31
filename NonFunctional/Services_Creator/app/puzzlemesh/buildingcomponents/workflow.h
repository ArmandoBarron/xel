#ifndef WORKFLOW_H
#define WORKFLOW_H

#include <string>
#include <vector>

#include "stage.h"
//#include "catalog.h"
#include "../logs/logs.h"
#include "../skycds/Catalog.h"

class Workflow : public BuildingBlock
{
private:
  vector<Stage *> stages;
  vector<string> stagesStr;
  vector<Catalog *> catalogKeys;
  Stage start;
  Stage last;
  string apikey, token, access, id, network;
  APISkyCDS *api;

public:
  Workflow() : BuildingBlock(WORKFLOW){};
  Workflow(string name) : BuildingBlock(name, WORKFLOW) {}
  Workflow(string name, vector<string> sourcesStr, vector<string> sinksStr)
      : BuildingBlock(name, WORKFLOW, sourcesStr, sinksStr) {}
  Workflow(string name, vector<string> sourcesStr, vector<string> sinksStr, vector<string> stagesStr, vector<Catalog *> catalogs, string network, string memory, string limit_mem, string cpus)
      : BuildingBlock(name, WORKFLOW, sourcesStr, sinksStr)
  {
    this->stagesStr = stagesStr;
    this->catalogKeys = catalogs;
    this->network = network;
    this->memory = memory;
    this->limit_mem = limit_mem;
    this->cpus = cpus;
  }

  void setStages(vector<Stage *> stages);
  void addStage(Stage *stg);
  vector<string> getStagesSrt();
  void setStart(Stage stg);
  void setLast(Stage stg);
  vector<Stage *> getStages();
  Stage *getStage(int idx);
  Stage getStart();
  Stage getLast();

  const string &getApikey() const;

  void setApikey(const string &apikey);

  const string &getToken() const;

  void setToken(const string &token);

  const string &getAccess() const;

  void setAccess(const string &access);

  vector<Catalog *> getCatalogs();
  void execute(const string &workdirbase, const string &compose_command);
  void downloadInputData(const string &workdirbase);

  APISkyCDS *getApi() const;

  void setApi(APISkyCDS *api);

  const string &getId() const;

  void setId(const string &id);

  const string &getNetwork() const;
  string getMemory();
  string getLimit();
  string getCPUS();
};

#endif
