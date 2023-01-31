#include "workflow.h"

void Workflow::setStages(vector<Stage*> stages)
{
    this->stages = stages;
}

void Workflow::addStage(Stage *stg)
{
    Logger(this->name + ": Stage " + stg->getName() + " added", true);
    this->stages.push_back(stg);
}

void Workflow::setStart(Stage start)
{
    this->start = start;
}

void Workflow::setLast(Stage last)
{
    this->last = last;
}

vector<Stage*> Workflow::getStages()
{
    return this->stages;
}

Stage* Workflow::getStage(int idx)
{
    return this->stages.at(idx);
}


Stage Workflow::getStart()
{
    return this->start;
}

Stage Workflow::getLast()
{
    return this->last;
}

vector<string> Workflow::getStagesSrt()
{
  return this->stagesStr;
}

vector<Catalog*> Workflow::getCatalogs()
{
  return this->catalogKeys;
}


void Workflow::execute(const string& workdirbase, const string& compose_command)
{
    Logger(this->name + ": executing ", true);
    vector<thread> threadsvec;
    vector<string> auxStrs;

    chrono::milliseconds ms = chrono::duration_cast< chrono::milliseconds >(
            chrono::system_clock::now().time_since_epoch()
    );

    Catalog *c = this->api->createCat(this->catalogKeys[0]->getName() + "/" + this->getName() + "-" + ::to_string(ms.count()), this->catalogKeys[0]->getToken(), true);

    for(auto s : this->stages)
    {
        threadsvec.emplace_back(&Stage::execute, s, workdirbase + "/" + this->workdir, auxStrs, compose_command, this->api, c);
    //s->execute(workdirbase + "/" + this->workdir);
    }

    for (auto &t : threadsvec)
    {
      t.join();
    }

    ofstream myfile;
    myfile.open (workdirbase +  "/" + this->workdir +  "/catalogs.txt", std::ios_base::app);

    for(auto s : this->stages)
    {
        myfile << s->getName() << "," << s->getCatalog()->getToken() << ","  << s->getCatalog()->getName() << "\n";
    }

    myfile.close();

}

void Workflow::downloadInputData(const string& workdirbase)
{
    string outDir = workdirbase + "/" + this->workdir;
    ofstream myfile;

    cout << outDir << endl;
    myfile.open (outDir + "/downloads.txt");

    
    for (auto catalog : this->catalogKeys)
    {
        string java_down_cmd = "java -jar Download.jar " + token + " " + apikey + " " + catalog->getToken() \
            + " 2 1 cinves '" + outDir + "/catalogs" + "/" + catalog->getName() + "' " + access + " true false 1";
        cout << java_down_cmd << endl;
        string output =  this->exec_cmd(java_down_cmd.c_str());
        //system(java_down_cmd.c_str());
        myfile << output + "\n\n";
    }
    myfile.close();
}

const string &Workflow::getApikey() const {
    return apikey;
}

void Workflow::setApikey(const string &apikey) {
    Workflow::apikey = apikey;
}

const string &Workflow::getToken() const {
    return token;
}

void Workflow::setToken(const string &token) {
    Workflow::token = token;
}

const string &Workflow::getAccess() const {
    return access;
}

void Workflow::setAccess(const string &access) {
    Workflow::access = access;
}

APISkyCDS *Workflow::getApi() const {
    return api;
}

void Workflow::setApi(APISkyCDS *api) {
    Workflow::api = api;
}

const string &Workflow::getId() const {
    return id;
}

void Workflow::setId(const string &id) {
    Workflow::id = id;
}

const string &Workflow::getNetwork() const {
    return network;
}

string Workflow::getMemory(){
    return this->memory;
}

string Workflow::getLimit(){
    return this->limit_mem;
}

string Workflow::getCPUS(){
    return this->cpus;
}