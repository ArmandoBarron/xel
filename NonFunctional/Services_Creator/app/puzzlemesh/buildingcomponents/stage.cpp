#include "stage.h"


void Stage::setPrevious(vector<Stage *> previous)
{
    this->previous = previous;
}

void Stage::setNext(vector<Stage *> next)
{
    this->next = next;
}

void Stage::setBBs(tsl::ordered_map<string, BuildingBlock *> bb)
{
  this->bbs = bb;
}

tsl::ordered_map<string, BuildingBlock *> Stage::getBBs()
{
  return this->bbs;
}

bool Stage::hasBB(string name)
{
  return bbs.find(name) != bbs.end();
}

void Stage::addPrevious(Stage *previous)
{
    this->previous.push_back(previous);
}

void Stage::addNext(Stage *next)
{
    this->next.push_back(next);
}


void Stage::setBB(BuildingBlock *bb)
{
    Logger(this->name + ": Added building block " + bb->getName(), true);
    this->bbs[bb->getName()] = bb;
}

BuildingBlock* Stage::getBB(string name)
{
  return this->bbs.find(name) != this->bbs.end() ? this->bbs[name] : NULL;
}

vector<string> Stage::getBBsStr()
{
  return this->bbsStr;
}

string Stage::getDependencieDir(BuildingBlock* bb, string basedir)
{
  switch (bb->getType()) {
    case SINGLE:
    {
      return basedir + "/" + bb->getWorkdir();
    }
    case PATTERN:
    {
      Pattern* pt = (Pattern*) bb;
      return this->getDependencieDir(pt->getWorker(), basedir + "/" + bb->getWorkdir());
    }
    case STAGE:
    {
      Stage* stg = (Stage *) bb;
      BuildingBlock* last = stg->getBB(stg->getBBsStr()[stg->getBBsStr().size()-1]);
      //cout << last->getName() << endl;
      return this->getDependencieDir(last, basedir + "/" + bb->getWorkdir());
    }
  }
  return "";
}

void Stage::execute(const string& workdirbase,  const vector<string>& sourcesPaths, const string& compose_command, APISkyCDS *api, Catalog *father)
{
  vector<string> sourcesStg;
  Logger(this->name + ": waiting", true);
  this->state = WAITING;
  int previousCompleted = 0;

  while ( previousCompleted < this->sources.size() )
  {
    previousCompleted = 0;
    for (auto s : this->sources)
    {
      previousCompleted += s.second->getState() == COMPLETED ? 1 : 0;
    }
  }
  auto start_ptr = chrono::steady_clock::now();
  Logger(this->name + ": WORKING", true);
  this->state = WORKING;
  for (auto s : this->sources)
  {
    sourcesStg.push_back(this->getDependencieDir(s.second, workdirbase + "/"));
  }

  for (auto s : this->sourcesStr)
  {
    if (dirExists(s.c_str()) == 1)
    {
      sourcesStg.push_back(s);
    }
  }

  Logger(this->name + ": has " + ::to_string(this->sourcesStr.size()) + " sources", true);
  std::vector<string> inputs, outputsPaths;
  bool first = true;

  for(auto b : this->bbs)
  {
    inputs = first ? sourcesStg : outputsPaths;
    switch (b.second->getType()) {
      case SINGLE:
        ((Single* ) b.second)->execute( workdirbase + "/" + this->workdir, inputs, compose_command, !first, 0);
        outputsPaths.clear();
        break;
      case PATTERN:
        ((Pattern* ) b.second)->execute( workdirbase + "/" + this->workdir, inputs, compose_command);
        break;
      case STAGE:
        ((Stage* ) b.second)->execute( workdirbase + "/" + this->workdir, inputs, compose_command , api, father);
        break;
    }

    outputsPaths.push_back(workdirbase + "/" + this->workdir);
  }


  uploadData(api, workdirbase, father);
  this->state = COMPLETED;
  auto end_ptr = chrono::steady_clock::now();

  Logger(this->name + ": stage executed in ST = " + ::to_string(chrono::duration_cast<chrono::milliseconds>(end_ptr - start_ptr).count()) + " miliseconds", true);
}

void Stage::uploadData(APISkyCDS *api, const string& workdirbase, Catalog *father)
{
    auto start_ptr = chrono::steady_clock::now();

    chrono::milliseconds ms = chrono::duration_cast< chrono::milliseconds >(
            chrono::system_clock::now().time_since_epoch()
    );

    ofstream myfile;
    myfile.open (workdirbase + "/uploads.txt", std::ios_base::app);

    this->catalog = api->createCat( father->getName() + "/" + this->getWorkdir() + "-" + ::to_string(ms.count()), father->getToken(), true);
    string java_down_cmd = "java -jar Upload.jar " + api->getTokenUser() + " " + api->getApikey() + " " + this->catalog->getToken() + " IDA bob 2 '" + workdirbase + "/" + this->workdir + "' cinves true " + api->getAccessToken() + " true true 4";
    cout << java_down_cmd << endl;
    string output =  this->exec_cmd(java_down_cmd.c_str());

    myfile << output + "\n\n";
    myfile.close();

    auto end_ptr = chrono::steady_clock::now();
    Logger(this->name + ": data satage upload in ST = " + ::to_string(chrono::duration_cast<chrono::milliseconds>(end_ptr - start_ptr).count()) + " miliseconds", true);
}

Catalog *Stage::getCatalog() const {
    return catalog;
}

void Stage::setCatalog(Catalog *catalog) {
    Stage::catalog = catalog;
}
