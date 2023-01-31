#include "single.h"

void Single::setCommand(string command)
{
    this->command = command;
}

void Single::setInputs(list<string> inputs)
{
    this->inputs = inputs;
}

void Single::setImage(string image)
{
    this->image = image;
}

string Single::getCommnad()
{
    return this->command;
}

list<string> Single::getInputs()
{
    return this->inputs;
}

string Single::getImage()
{
    return this->image;
}

json Single::processFile(string workdirbase, string c, string compose_command)
{
    string complete_workdir, final_cmd, curl_command, result;
    json j;
    long fSize;

    complete_workdir = workdirbase + "/" + this->workdir;
    //cout << "FILEEEE " << c << endl;
    //final_curl = boost::replace_all_copy(curl_command, "COMMMAND", command.c_str());
    final_cmd = boost::replace_all_copy(this->getCommnad(), "@I", c.c_str());
    final_cmd = boost::replace_all_copy(final_cmd, "@F", (complete_workdir + "/" + getFileName(c)).c_str());
    final_cmd = boost::replace_all_copy(final_cmd, "@D", (complete_workdir + "/").c_str());
    final_cmd = boost::replace_all_copy(final_cmd, "@N", getFileNameWithoutExt(c).c_str());
    final_cmd = boost::replace_all_copy(final_cmd, "@L", getFileName(c).c_str());
    final_cmd = boost::replace_all_copy(final_cmd, "@S", dirnameOf(c).c_str());
    curl_command = compose_command + " exec -T " + this->getName() + " sh -c \"" + final_cmd + "\"";
    cout << final_cmd << endl;
    fSize = filesize(c.c_str());

    //Execute bb command
    result = exec_cmd(curl_command.c_str());

    json json_result;

    //cout << result << endl;

    json_result["std_out"] = result;

    json_result["size"] = fSize;

    return json_result;
}

results Single::execute(string workdirbase, vector<string> contents, string compose_command, bool readFromDir, int id_worker)
{
    float totalTime;
    long sizeTotal;
    json j;
    vector<string> filesInDir;
    Logger(this->name + ": waiting", true);
    this->state = WAITING;

    this->state = WORKING;
    Logger(this->name + ": running", true);

    totalTime = 0;
    sizeTotal = 0;
    auto start = chrono::steady_clock::now();
    for (auto c : contents)
    {
        // if (isDir(c))
        // {
        //     recursive_file_list(c.c_str(), filesInDir);
        //     for (auto f : filesInDir)
        //     {
        //         j = this->processFile(workdirbase, f, compose_command);
        //     }
        // }
        // else
        // {
            j = this->processFile(workdirbase, c, compose_command);
        // }
        // totalTime += stof(j["response_time"].dump());
        sizeTotal += stol(j["size"].dump());
        //Logger(this->name + ": executed in ST=" + json_result["response_time"].dump() + " RT = " + ::to_string(chrono::duration_cast<chrono::milliseconds>(end - start).count()) + " miliseconds", true);
    }
    auto end = chrono::steady_clock::now();
    double th = sizeTotal / totalTime;
    Logger(this->name + ": processed " + ::to_string(sizeTotal) + " bytes in ST=" + ::to_string(totalTime) + " RT = " + ::to_string(chrono::duration_cast<chrono::milliseconds>(end - start).count()) + " miliseconds", true);
    this->state = COMPLETED;
    results rs;
    rs.size = sizeTotal;
    rs.th = th;
    rs.st = totalTime;
    return rs;
}

vector<string> Single::getPorts()
{
    return this->ports;
}

void Single::setPorts(vector<string> ports)
{
    this->ports = ports;
}

void Single::setNode(string node)
{
    this->node = node;
}

string Single::getNode()
{
    return this->node;
}

tsl::ordered_map<string, string> Single::getEnvironment()
{
    return this->environment;
}

string Single::getMemory(){
    return this->memory;
}

string Single::getLimit(){
    return this->limit_mem;
}

string Single::getCPUS(){
    return this->cpus;
}