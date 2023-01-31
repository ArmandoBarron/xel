#include "pattern.h"

void Pattern::setNWorkers(int nWorkers)
{
    this->nWorkers = nWorkers;
}

void Pattern::setLB(string loadBalancer)
{
    this->loadBalancer = loadBalancer;
}

void Pattern::setPattern(string pattern)
{
    this->pattern = pattern;
}

void Pattern::setWorker(Single *worker)
{
    this->worker = worker;
}

int Pattern::getNWorkers()
{
    return this->nWorkers;
}

string Pattern::getLB()
{
    return this->loadBalancer;
}

string Pattern::getPattern()
{
    return this->pattern;
}

Single *Pattern::getWorker()
{
    return this->worker;
}

void Pattern::execute(string workdirbase, vector<string> sourcesPaths, string compose_command)
{
    vector<future<results>> threadsvec;
    vector<string> contents;
    int i;
    string curl_command, result, command;
    std::stringstream ss;
    Logger(this->name + ": waiting", true);
    this->state = WAITING;

    auto start_ptr = chrono::steady_clock::now();
    //add number of workers to json
    // j.push_back(std::to_string(this->getNWorkers()));
    //
    //
    // j.push_back(this->lbmode);
    //
    // //add source paths to json
    // for (auto x : sourcesPaths)
    // {
    //     j.push_back(x);
    // }

    ss << "./main " << this->getNWorkers() << " " << this->lbmode << " ";

    for (auto x : sourcesPaths)
    {
      ss << x << " ";
    }


    curl_command = compose_command + " exec -T lb" + this->getName() + " " +
                   " sh -c \"" + ss.str() + "\"" ;

    this->state = WORKING;
    Logger(this->name + ": running", true);
    Logger(this->name + ": executing load balancer", true);
    //execute load balancing command

    auto start = chrono::steady_clock::now();
    result = exec_cmd(curl_command.c_str());
    auto end = chrono::steady_clock::now();
    //parse result
    // cout << result << endl;
    auto json_result = json::parse(result);
    Logger(this->name + ": load balancer executed in RT = " + ::to_string(chrono::duration_cast<chrono::milliseconds>(end - start).count()) + " miliseconds", true);
    auto elements = json_result["result"];
    // cout << data << endl;
    //result.substr(1, result.size() - 1);
    // auto elements = json::parse(result);
    // cout << "aqui" << endl;
    for (i = 0; i < this->getNWorkers(); i++)
    {
        contents = elements[i].get<std::vector<string>>();
        threadsvec.push_back(async(&Single::execute, worker, workdirbase + "/" + this->getWorkdir(), contents, compose_command, false,i));
        // threadsvec.push_back(thread(&Single::execute, this->getWorker(), workdirbase + "/" + this->getWorkdir(),
        //                             elements[i], compose_command));
    }
    i = 0;
    for (auto &t : threadsvec)
    {
        auto r = t.get();
        //cout << i <<  "  " << worker->getName() << " " << r.size << " " << r.st << " " << r.th << endl;
        i++;
    }
    auto end_ptr = chrono::steady_clock::now();
    this->state = COMPLETED;
    Logger(this->name + ": pattern executed in ST = " + ::to_string(chrono::duration_cast<chrono::milliseconds>(end_ptr - start_ptr).count()) + " miliseconds", true);
}
