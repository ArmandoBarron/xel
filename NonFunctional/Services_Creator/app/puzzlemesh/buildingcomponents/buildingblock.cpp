#include "buildingblock.h"

void BuildingBlock::setSource(tsl::ordered_map<string, BuildingBlock *> sources)
{
    this->sources = sources;
}

void BuildingBlock::setSink(tsl::ordered_map<string, BuildingBlock *> sinks)
{
    this->sinks = sinks;
}

void BuildingBlock::setType(Type type)
{
    this->type = type;
}

void BuildingBlock::setState(State type)
{
    this->state = state;
}

void BuildingBlock::setName(string name)
{
    this->name = name;
}

tsl::ordered_map<string, BuildingBlock *> BuildingBlock::getSource()
{
    return this->sources;
}

tsl::ordered_map<string, BuildingBlock *> BuildingBlock::getSink()
{
    return this->sinks;
}

Type BuildingBlock::getType()
{
    return this->type;
}

State BuildingBlock::getState()
{
    return this->state;
}

string BuildingBlock::getName()
{
    return this->name;
}

void BuildingBlock::addSource(BuildingBlock *source)
{
    Logger(this->name + ": Added source " + source->getName(), true);
    this->sources[source->getName()] = source;
}

void BuildingBlock::addSink(BuildingBlock *sink)
{
    Logger(this->name + ": Added sink " + sink->getName(), true);
    this->sinks[sink->getName()] = sink;
}

BuildingBlock *BuildingBlock::getSource(string name)
{
    return this->sources.find(name) != this->sources.end() ? this->sources[name] : NULL;
}

BuildingBlock *BuildingBlock::getSink(string name)
{
    return this->sinks.find(name) != this->sinks.end() ? this->sinks[name] : NULL;
}

string BuildingBlock::getWorkdir()
{
    return this->workdir;
}

void BuildingBlock::setWorkdir(string workdir)
{
    this->workdir = workdir;
}

vector<string> BuildingBlock::getSourceStr()
{
    return this->sourcesStr;
}

vector<string> BuildingBlock::getSinkStr()
{
    return this->sinksStr;
}

void BuildingBlock::setSourceStr(vector<string> sourceStr)
{
    this->sourcesStr = sourceStr;
}

void BuildingBlock::setSinkStr(vector<string> sinkStr)
{
    this->sinksStr = sinkStr;
}

void BuildingBlock::addSourceStr(string sourceStr)
{
    this->sourcesStr.push_back(sourceStr);
}

void BuildingBlock::addSinkStr(string sinkStr)
{
    this->sinksStr.push_back(sinkStr);
}

string BuildingBlock::createWorkdir(string basedir)
{
    time_t t;
    stringstream ss;
    string fullworkpath;
    struct stat sb;


    if (this->workdir.empty())
    {
        t = std::time(0);
        ss << t;
        this->workdir = this->name;
    }

    fullworkpath = basedir + "/" + this->workdir;

    Logger(this->name + ": Workdir " + this->workdir, true);

    if (stat(fullworkpath.c_str(), &sb) != 0)
    {
        const int dir_err = mkdir(fullworkpath.c_str(), S_IRWXU | S_IRWXG | S_IROTH | S_IXOTH);
        if (-1 == dir_err)
        {
            Logger("ERROR: Error creating directory " + fullworkpath, true);
            exit(1);
        }

        Logger(this->name + ": Workdir created", true);
    }
    else
    {
        Logger(this->name + ": Workdir exists", true);
    }



    return fullworkpath;
}

void BuildingBlock::execute(string workdirbase, vector<string> sourcesPaths)
{
}

string BuildingBlock::exec_cmd(const char *cmd)
{
    //cout << cmd << endl;
    std::array<char, 128> buffer;
    std::string result;
    std::unique_ptr<FILE, decltype(&pclose)> pipe(popen(cmd, "r"), pclose);
    if (!pipe)
    {
        throw std::runtime_error("popen() failed!");
    }
    while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr)
    {
        result += buffer.data();
    }
    return result;
}
