#include "parser.h"

unordered_map<string, Single *> ConfigParser::searchSingles(vector<string> lines)
{
    bool found;
    unordered_map<string, Single *> singles;
    tsl::ordered_map<string, string> environment;
    string name, command, image, memory  = "", limit_mem = "", cpus = "";
    vector<string> inputs, outputs, ports;

    found = false;

    for (auto &i : lines)
    {
        if (found)
        {
            if (i.compare("[END]") == 0)
            {
                found = !found;
                singles[name] = new Single(name, command, inputs, outputs, image, ports, environment, memory, limit_mem, cpus);

                this->bbs[name] = singles[name];
                Logger("PARSER: Configured single " + name, true);
                inputs = {};
                outputs = {};
                ports = {};
                memory = "";
                limit_mem  = ""; 
                cpus  = "";
            }
            else
            {
                vector<string> v{explode_one(i, '=')};
                if (v.size() == 2)
                {

                    v[0] = trim(v[0]);

                    if (v[0].compare("name") == 0)
                    {
                        name = trim(v[1]);
                    }
                    else if (v[0].compare("command") == 0)
                    {
                        command = trim(v[1]);
                    }
                    else if (v[0].compare("source") == 0)
                    {
                        inputs = explode(trim(v[1]), ' ');
                    }
                    else if (v[0].compare("sink") == 0)
                    {
                        outputs = explode(trim(v[1]), ' ');
                    }
                    else if (v[0].compare("image") == 0)
                    {
                        image = trim(v[1]);
                    }
                    else if (v[0].compare("port") == 0)
                    {
                        ports = explode(trim(v[1]), ' ');
                    }
                    else if (v[0].compare("environment") == 0)
                    {
                        auto first_token = i.substr(i.find('=') + 1, i.size());
                        vector<string> environment_vars{explode(first_token, ';')};
                        vector<string> aux;

                        for (auto &ev : environment_vars)
                        {
                            aux = explode_one(trim(ev), '=');
                            if (aux.size() == 2)
                            {
                                environment[aux[0]] = aux[1];
                            }
                        }
                    }
                    else if (v[0].compare("memory") == 0)
                    {
                        memory = trim(v[1]);
                    }
                    else if (v[0].compare("memory_limit") == 0)
                    {
                        limit_mem = trim(v[1]);
                    }
                    else if (v[0].compare("CPUS") == 0)
                    {
                        cpus = trim(v[1]);
                    }
                }
                else
                {
                    cerr << i << "Bad configuration" << endl;
                    exit(1); // call system to stop
                }
            }
        }
        else if (i.compare("[BB]") == 0) // New BB found, next lines are the BB metadata
        {
            found = !found;
        }
    }
    return singles;
}

unordered_map<string, Pattern *> ConfigParser::searchPatterns(vector<string> lines,
                                                              unordered_map<string, Single *> singles)
{
    bool found;
    unordered_map<string, Pattern *> patterns;
    string name, pattern, lb, workerName, lbmode;
    vector<string> inputs, outputs;
    int nWorkers;

    found = false;

    for (auto &i : lines)
    {
        if (found)
        {
            if (i.compare("[END]") == 0)
            {
                found = !found;
                patterns[name] = new Pattern(name, nWorkers, lb, lbmode, pattern,
                                             singles[workerName], inputs, outputs);
                this->bbs[name] = patterns[name];
                Logger("PARSER: Configured pattern " + name, true);
            }
            else
            {
                vector<string> v{explode(i, '=')};
                if (v.size() == 2)
                {
                    v[0] = trim(v[0]);
                    if (v[0].compare("name") == 0)
                    {
                        name = trim(v[1]);
                    }
                    else if (v[0].compare("task") == 0)
                    {
                        workerName = trim(v[1]);
                    }
                    else if (v[0].compare("source") == 0)
                    {
                        inputs = explode(trim(v[1]), ' ');
                    }
                    else if (v[0].compare("pattern") == 0)
                    {
                        pattern = trim(v[1]);
                    }
                    else if (v[0].compare("workers") == 0)
                    {
                        nWorkers = stoi(trim(v[1]));
                    }
                    else if (v[0].compare("loadbalancer") == 0)
                    {
                        vector<string> v2{explode(trim(v[1]), ':')};
                        lb = v2[0];
                        lbmode = v2[1];
                    }
                    else if (v[0].compare("sink") == 0)
                    {
                        outputs = explode(trim(v[1]), ' ');
                    }
                }
                else
                {
                    cerr << i << "Bad configuration" << endl;
                    exit(1); // call system to stop
                }
            }
        }
        else if (i.compare("[PATTERN]") == 0) // New Pattern found, next lines are the Pattern metadata
        {
            found = !found;
        }
    }
    return patterns;
}

unordered_map<string, Stage *> ConfigParser::searchStages(vector<string> lines,
                                                          unordered_map<string, Single *> singles,
                                                          unordered_map<string, Pattern *> patterns)
{
    bool found;
    unordered_map<string, Stage *> stages;
    string name, basepath;
    vector<string> inputs, outputs, transformationNames;

    basepath = this->workpath;
    basepath += +"/results/";
    found = false;

    for (auto &i : lines)
    {
        if (found)
        {
            if (i.compare("[END]") == 0)
            {
                found = !found;
                stages[name] = new Stage(name, inputs, outputs, transformationNames);
                this->bbs[name] = stages[name];
                Logger("PARSER: Configured stage " + name, true);
            }
            else
            {
                vector<string> v{explode(i, '=')};
                if (v.size() == 2)
                {
                    v[0] = trim(v[0]);
                    boost::replace_all(v[1], "@PWD", basepath);

                    if (v[0].compare("name") == 0)
                    {
                        name = trim(v[1]);
                    }
                    else if (v[0].compare("source") == 0)
                    {
                        inputs = explode(trim(v[1]), ' ');
                    }
                    else if (v[0].compare("sink") == 0)
                    {
                        outputs = explode(trim(v[1]), ' ');
                    }
                    else if (v[0].compare("transformation") == 0)
                    {
                        transformationNames = explode(trim(v[1]), ' ');
                    }
                }
                else
                {
                    cerr << i << "Bad configuration" << endl;
                    exit(1); // call system to stop
                }
            }
        }
        else if (i.compare("[STAGE]") == 0) // New Pattern found, next lines are the Pattern metadata
        {
            found = !found;
        }
    }
    return stages;
}

Workflow *ConfigParser::searchWorkflow(vector<string> lines)
{
    bool found;
    string name, network = "", memory  = "", limit_mem = "", cpus = "";
    vector<string> inputs, outputs, transformationNames;
    vector<Catalog *> catalogs;
    Workflow *workflow;

    found = false;

    for (auto &i : lines)
    {
        if (found)
        {
            if (i.compare("[END]") == 0)
            {
                found = !found;
                workflow = new Workflow(name, inputs, outputs, transformationNames, catalogs, network, memory, limit_mem, cpus);
                Logger("PARSER: Configured workflow " + name, true);
            }
            else
            {
                vector<string> v{explode(i, '=')};
                if (v.size() == 2)
                {
                    v[0] = trim(v[0]);
                    if (v[0].compare("name") == 0)
                    {
                        name = trim(v[1]);
                    }
                    else if (v[0].compare("stages") == 0)
                    {
                        transformationNames = explode(trim(v[1]), ' ');
                    }
                    else if (v[0].compare("source") == 0)
                    {
                        inputs = explode(trim(v[1]), ' ');
                    }
                    else if (v[0].compare("sink") == 0)
                    {
                        outputs = explode(trim(v[1]), ' ');
                    }
                    else if (v[0].compare("catalogs") == 0)
                    {
                        vector<string> strCatalogs = explode(trim(v[1]), ' ');
                        for (auto &sc : strCatalogs)
                        {
                            vector<string> catalogParts = explode(sc, ':');

                            if (catalogParts.size() == 2)
                            {
                                catalogs.push_back(new Catalog(catalogParts[0], catalogParts[1]));
                            }
                        }
                    }
                    else if (v[0].compare("network") == 0)
                    {
                        network = trim(v[1]);
                    }
                    else if (v[0].compare("memory") == 0)
                    {
                        memory = trim(v[1]);
                    }
                    else if (v[0].compare("memory_limit") == 0)
                    {
                        limit_mem = trim(v[1]);
                    }
                    else if (v[0].compare("CPUS") == 0)
                    {
                        cpus = trim(v[1]);
                    }
                }
                else
                {
                    cerr << i << "Bad configuration" << endl;
                    exit(1); // call system to stop
                }
            }
        }
        else if (i.compare("[WORKFLOW]") == 0) // New Pattern found, next lines are the Pattern metadata
        {
            found = !found;
        }
    }
    return workflow;
}

int ConfigParser::readConfig(string filepath, string apikey, string token, string access)
{
    ifstream inFile;
    string line;
    vector<string> lines;
    vector<string> skycdsLines;

    inFile.open(filepath);

    if (!inFile)
    {
        cerr << "Unable to open file configuration.cfg";
        exit(1); // call system to stop
    }

    while (getline(inFile, line))
    {
        lines.push_back(line);
    }

    inFile.close();

    // Search for singles
    this->singles = this->searchSingles(lines);
    this->patterns = this->searchPatterns(lines, singles);
    this->stages = this->searchStages(lines, singles, patterns);
    this->workflow = this->searchWorkflow(lines);

    inFile.open("config.db");

    if (!inFile)
    {
        cerr << "Unable to open file skycds configuration file";
        return 0;
    }

    while (getline(inFile, line))
    {
        skycdsLines.push_back(line);
    }

    inFile.close();

    if (skycdsLines.size() < 8)
    {
        cerr << "Bad skycds configuration file";
        return 0;
    }

    APISkyCDS *api = new APISkyCDS(skycdsLines[6], skycdsLines[5], token, access, apikey);
    this->workflow->setApi(api);

    return 0;
}

unordered_map<string, Single *> ConfigParser::getSingles()
{
    return this->singles;
}

unordered_map<string, Pattern *> ConfigParser::getPatterns()
{
    return this->patterns;
}

unordered_map<string, Stage *> ConfigParser::getStages()
{
    return this->stages;
}

Workflow *ConfigParser::getWorkflow()
{
    return this->workflow;
}

unordered_map<string, BuildingBlock *> ConfigParser::getBBs()
{
    return this->bbs;
}
