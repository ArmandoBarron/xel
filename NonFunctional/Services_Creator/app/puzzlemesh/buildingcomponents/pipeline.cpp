
#include "pipeline.h"

void Pipeline::setStages(vector<Single*> stages)
{
    this->stages = stages;
}

vector<Single*> Pipeline::getStages()
{
    return this->stages;
}

void Pipeline::execute(string workdirbase, vector<string> sourcesPaths, string compose_command)
{
}
