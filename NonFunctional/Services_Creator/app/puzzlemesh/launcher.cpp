#include "launcher.h"

void Launcher::execute(string mode)
{
	string compose_command, up_command, down_command;
	string pwdStr;

	pwdStr = this->workpath;

	this->coupling();
	this->buildYML(mode);

	compose_command = "docker-compose --log-level ERROR -p " + pwdStr + "/results/" + this->workflow->getWorkdir() +
					  " -f " + pwdStr + "/results/" + this->workflow->getWorkdir() + "/docker-compose.yml ";

	// Deploy YML
	Logger("LAUCHER: deploying virtual containers of workflow " + this->workflow->getName(), true);

	// system(up_command.c_str());
	this->workflow->downloadInputData(pwdStr + "/results");
	this->workflow->execute(pwdStr + "/results", compose_command);
}

void Launcher::start(string mode)
{
	string compose_command, up_command, down_command;
	string pwdStr;

	pwdStr = this->workpath;
	fs::create_directories(pwdStr + "/results/");

	this->coupling();
	this->buildYML(mode);

	if (boost::iequals(mode, "swarm"))
	{
		up_command = "docker stack deploy --compose-file " + pwdStr + "/results/" + this->workflow->getWorkdir() + "/docker-compose.yml " + this->workflow->getWorkdir();
		;
	}
	else
	{
		compose_command = "docker-compose --log-level ERROR -p " + pwdStr + "/results/" + this->workflow->getWorkdir() +
						  " -f " + pwdStr + "/results/" + this->workflow->getWorkdir() + "/docker-compose.yml ";
		up_command = compose_command + " up -d --build";
		// //search fo replicas
		for (auto x : patterns)
		{
			up_command += " --scale " + x.second->getWorker()->getName() + "=" + ::to_string(x.second->getNWorkers()) + " ";
		}

		up_command += " 2> /dev/null";
	}

	cout << up_command << endl;
	// Deploy YML
	Logger("LAUCHER: deploying virtual containers of workflow " + this->workflow->getName(), true);

	system(up_command.c_str());

	if (!boost::iequals(mode, "swarm"))
	{
		down_command = compose_command + " down";
	}
	else
	{
		down_command = "docker stack rm " + this->workflow->getWorkdir();
	}

	Logger("LAUCHER: to shutdown the containers execute  \n\n" + down_command + "\n\n", true);
	// printJSON(compose_command);
}

void Launcher::printMonitoringFile(vector<string> containers)
{
	string pwdStr;
	ofstream config_file, myfile;
	string configuration = this->workflow->getName() + "\nService E-Salud\n";
	pwdStr = this->workpath;
	int i = 1;
	string conf_path = pwdStr + "/results/" + this->workflow->getWorkdir() + "/" + this->workflow->getName() + ".cfg";
	string mon_cmd = "python3 representation/model_application.py " + conf_path;
	config_file.open(conf_path);

	for (auto c : containers)
	{
		configuration += "-cont\n";
		configuration += c + "\n";
		configuration += "Service " + std::to_string(i++) + "\n";
	}
	config_file << configuration << endl;
	config_file.close();

	myfile.open(pwdStr + "/results/" + this->workflow->getName() + "/monitoring.txt");
	string output = this->workflow->exec_cmd(mon_cmd.c_str());
	myfile << output << endl;
	myfile.close();
}

void Launcher::generateNormas(std::string json_file)
{
	string pwdStr;
	pwdStr = this->workpath;
	ofstream myfile;
	string ymlpath = pwdStr + "/results/" + this->workflow->getWorkdir() + "/docker-compose.yml";
	string outputNormas = pwdStr + "/results/" + this->workflow->getWorkdir();
	string normas_cmd = "python3 normas/main.py " + this->getFilename() + " " + json_file + " " + ymlpath + " " + outputNormas;

	string output = this->workflow->exec_cmd(normas_cmd.c_str());
	myfile.open(pwdStr + "/results/" + this->workflow->getName() + "/normas.txt");
	myfile << output << endl;
	myfile.close();
}

void Launcher::printJSON(string compose_cmd_base)
{

	string pwdStr;
	ofstream json_file;

	pwdStr = this->workpath;

	cout << pwdStr + "/results/" + this->workflow->getWorkdir() + "/stages.json" << endl;

	json_file.open(pwdStr + "/results/" + this->workflow->getWorkdir() + "/stages.json");
	string json = "{\n\t\"workflow_name\":\"" + this->workflow->getName() + "\",\n\t\"stages\":[";
	long unsigned int j = 1;
	long unsigned int i;
	for (auto s : this->workflow->getStages())
	{
		json += "\n\t\t\t{\"name\":\"" + s->getName() + "\",\"sources\":[";
		i = 1;
		for (auto s2 : s->getSource())
		{
			json += "\"" + s->getDependencieDir(s2.second, pwdStr + "/results" + "/" + this->workflow->getWorkdir() + "/") + "\"";
			if (i < s->getSource().size())
			{
				json += ",";
			}
			i++;
			// std::cout << "source" << "\t" << s->getName() << "\t" << s->getDependencieDir(s2.second, pwdStr + "/results" + "/" +  this->workflow->getWorkdir() + "/") << std::endl;
			// sourcesStg.push_back(this->getDependencieDir(s.second, workdirbase + "/"));
		}

		std::vector<std::string> sources_str;

		for (auto s2 : s->getSourceStr())
		{
			if (dirExists(s2.c_str()) == 1)
			{
				sources_str.push_back(s2);
				// std::cout << "source" << "\t" << s->getName() << "\t" << s2 << std::endl;
			}
		}
		i = 1;
		for (auto s2 : sources_str)
		{
			json += "\"" + s2 + "\"";
			if (i < sources_str.size())
			{
				json += ",";
			}
			i++;
		}

		// cout <<  pwdStr + "/results/" + this->workflow->getWorkdir() + "/" + s->getName() << endl;

		json += "], \"sinks\":[";
		json += "\"" + pwdStr + "/results/" + this->workflow->getWorkdir() + "/" + s->getName() + "\"";
		json += "]}";

		if (j < this->workflow->getStages().size())
		{
			json += ",";
		}
		j++;
		// std::cout << "sink" << "\t" << s->getName() << "\t" << pwdStr + "/results" + "/" +  this->workflow->getWorkdir() + "/" + s->getWorkdir() << std::endl;
	}
	// json += "\n\t\t]\n}";

	json += "\n\t\t],";

	string get_ids_cmd = compose_cmd_base + " ps -q";
	string cont_cmd_name_base = "docker inspect --format='{{.Name}}' ";
	string get_name = "";
	string id_containers_str = this->workflow->exec_cmd(get_ids_cmd.c_str());
	string cont_name;
	vector<string> id_containers{explode(id_containers_str, '\n')};
	vector<string> containers_names;

	json += "\n\t\"containers\":[\n";
	j = 1;
	for (auto &c : id_containers)
	{
		get_name = cont_cmd_name_base + c;
		cont_name = this->workflow->exec_cmd(get_name.c_str());
		json += "\t\t\t{";
		json += "\"name\":\"" + trim(cont_name) + "\",";
		json += "\"id\":\"" + c + "\"";
		json += "}";
		if (j < id_containers.size())
		{
			json += ",\n";
		}
		containers_names.push_back(trim(cont_name));
		j++;
		// cout << c << "\t" << cont_name << endl;
	}

	json += "\n\t\t]\n}";
	json_file << json << endl;
	json_file.close();

	// generateNormas(pwdStr + "/results/" + this->workflow->getWorkdir() + "/stages.json");
	// printMonitoringFile(containers_names);
}

void Launcher::prepareBB(BuildingBlock *bb, string basepath)
{
	string auxbasepath = bb->createWorkdir(basepath);

	for (auto &x : bb->getSourceStr())
	{
		if (this->bbs.find(x) != this->bbs.end())
		{
			bb->addSource(this->bbs[x]);
		}
	}

	for (auto &x : bb->getSinkStr())
	{
		if (this->bbs.find(x) != this->bbs.end())
		{
			bb->addSink(this->bbs[x]);
		}
	}

	switch (bb->getType())
	{
	case STAGE:
	{
		Stage *stage = (Stage *)bb;

		for (auto y : stage->getBBsStr())
		{
			if (this->bbs.find(y) != this->bbs.end())
			{
				stage->setBB(this->bbs[y]);
				this->prepareBB(this->bbs[y], auxbasepath);
			}
		}
		break;
	}
	case PATTERN:
	{
		Pattern *pattern = (Pattern *)bb;
		prepareBB(pattern->getWorker(), auxbasepath);
		break;
	}
	}
}

void Launcher::coupling()
{
	Logger("LAUCHER: Coupling stages and building blocks", true);
	string basepath, auxbasepath;

	basepath = this->workpath;
	basepath += "/results/";

	basepath = workflow->createWorkdir(basepath);

	for (auto x : this->workflow->getStagesSrt())
	{
		if (this->stages.find(x) != this->stages.end())
		{
			this->workflow->addStage(this->stages[x]);
			this->prepareBB(this->bbs[x], basepath);
		}
	}
}

void Launcher::getVolumes(BuildingBlock *b, string target, set<vector<string>> &volumes)
{
	switch (b->getType())
	{
	case WORKFLOW:
	{
		for (auto y : this->stages)
		{
			getVolumes(y.second, target, volumes);
		}
		break;
	}
	case STAGE:
	{
		BuildingBlock *bb;
		Stage *stg = (Stage *)b;
		bb = stg->getBB(target);
		if (bb != NULL)
		{
			for (auto s : stg->getSourceStr())
			{
				if (s.find("/") == 0)
				{ // pos=0 limits the search to the prefix
					if (dirExists(s.c_str()) != 1)
					{
						fs::create_directories(s);
					}
					volumes.insert({s, s});
				}
			}

			for (auto s : stg->getSinkStr())
			{
				vector<string> v{explode(s, ':')};
				if (v.size() > 1)
				{
					volumes.insert(v);
				}
				else if (dirExists(s.c_str()) == 1)
				{
					volumes.insert({s, s});
				}
			}
		}
		// search in subblocks
		for (auto x : stg->getBBs())
		{
			if (x.second->getName().compare(target) != 0)
			{
				getVolumes(x.second, target, volumes);
			}
		}
	}
	break;
	case PATTERN:
	{
		Pattern *w = (Pattern *)b;

		if (w->getWorker()->getName().compare(target) == 0)
		{
			for (auto s : w->getSourceStr())
			{
				vector<string> v{explode(s, ':')};

				if (s.find("/") == 0)
				{ // pos=0 limits the search to the prefix
					if (dirExists(s.c_str()) != 1)
					{
						fs::create_directories(s);
					}
					volumes.insert({s, s});
				}
			}
			getVolumes(this->workflow, w->getName(), volumes);
		}
		getVolumes(w->getWorker(), target, volumes);
	}
	break;
	}
}
// yml_base += "        deploy: \n";
// yml_base += "                placement: \n";
// yml_base += "                        constraints: [node.hostname == " + x.second->getNode() + "]\n";

void Launcher::buildYML(string mode)
{
	string yml_base = {"version: \'3\'\nservices:\n"};
	string links, auxPath, pwdStr;
	ofstream yml;
	vector<string> ports;
	BuildingBlock *bb;
	Single auxSingle;
	Pattern auxPatt;
	set<vector<string>> volumes;
	tsl::ordered_map<string, string> environment;

	if (boost::iequals(mode, "swarm"))
	{
		yml_base = "version: \'3\'\nservices:\n";
	}
	else
	{
		yml_base = "version: \'2.3\'\nservices:\n";
	}

	pwdStr = this->workpath;

	Logger("LAUNCHER: Creating YML file at " + this->workflow->getWorkdir() + "/docker-compose.yml", true);

	yml.open(pwdStr + "/results/" + this->workflow->getWorkdir() + "/docker-compose.yml");

	ifstream test;

	for (auto x : singles)
	{
		std::cout << x.second->getName() << std::endl;
		yml_base += "    " + x.second->getName() + ": \n";

		if (boost::iequals(mode, "swarm"))
		{
			yml_base += "        image: " + x.second->getImage() + "\n";
		}
		else
		{
			yml_base += "        image: " + x.second->getImage() + "\n";
		}

		yml_base += "        restart: always\n";
		yml_base += "        expose:\n            - \"5000/tcp\"\n";

		if (!boost::iequals(mode, "swarm"))
		{

			yml_base += "        volumes:\n";
			yml_base += "            - \"" + pwdStr + "/results/" + this->workflow->getWorkdir() + ":" + pwdStr + "/results/" + this->workflow->getWorkdir() + "\"\n";

			getVolumes(this->workflow, x.second->getName(), volumes);

			for (auto vl : volumes)
			{
				yml_base += "            - \"" + vl[0] + ":" + vl[1] + "\"\n";
			}

			volumes.clear();

			if (!boost::iequals(mode, "swarm"))
			{
				if (this->workflow->getCPUS().compare("") != 0 && this->workflow->getLimit().compare("") != 0 && this->workflow->getMemory().compare("") != 0)
				{
					yml_base += "\n        mem_limit: '" + this->workflow->getLimit() + "'\n";
					yml_base += "        mem_reservation: '" + this->workflow->getMemory() + "'\n";
					yml_base += "        cpus: '" + this->workflow->getCPUS() + "'\n";
				}
			}
		}
		else
		{
			yml_base += "        deploy:\n";
			yml_base += "            mode: replicated\n";

			if (this->workflow->getCPUS().compare("") != 0 && this->workflow->getLimit().compare("") != 0 && this->workflow->getMemory().compare("") != 0)
			{
				yml_base += "        deploy:\n";
				yml_base += "            resources:\n";
				yml_base += "                limits:\n";
				yml_base += "                    cpus: '" + this->workflow->getCPUS() + "'\n";
				yml_base += "                    memory: '" + this->workflow->getLimit() + "'\n";
				yml_base += "                reservations:\n";
				yml_base += "                    cpus: '" + this->workflow->getCPUS() + "'\n";
				yml_base += "                    memory: '" + this->workflow->getMemory() + "'\n";
			}

			for (auto p : patterns)
			{
				if (boost::iequals(p.second->getWorker()->getName(), x.second->getName()))
				{
					yml_base += "            replicas: " + std::to_string(p.second->getNWorkers()) + "\n";
					break;
				}
			}
		}

		ports = x.second->getPorts();
		if (ports.size() > 0)
		{
			yml_base += "        ports:\n";
			for (auto vl : ports)
			{
				yml_base += "            - \"" + vl + "\"\n";
			}
		}

		links += "             - " + x.second->getName() + "\n";

		if (this->workflow->getNetwork().empty())
		{
			yml_base += "        networks:\n             - " + this->workflow->getName() + "\n";
		}
		else
		{
			yml_base += "        networks:\n             - " + this->workflow->getNetwork() + "\n";
		}

		environment = x.second->getEnvironment();
		if (environment.size() > 0)
		{
			yml_base += "        environment:\n";
			for (auto vl : environment)
			{
				yml_base += "            " + vl.first + ": " + vl.second + "\n";
			}
		}
	}

	for (auto x : patterns)
	{
		if (x.second->getPattern().compare("MW") == 0)
		{
			yml_base += "    lb" + x.second->getName() + ": \n";

			if (boost::iequals(mode, "swarm"))
			{
				yml_base += "        image: ddomizzi/" + boost::algorithm::to_lower_copy(x.second->getLB()) + ":balancer\n";
			}
			else
			{
				yml_base += "        image: ddomizzi/" + boost::algorithm::to_lower_copy(x.second->getLB()) + ":balancer\n";
			}

			yml_base += "        restart: always\n";
			yml_base += "        expose:\n            - \"5000/tcp\"\n";

			if (boost::iequals(mode, "swarm"))
			{

				yml_base += "        volumes:\n";
				yml_base += "            - \"" + pwdStr + "/results/" + this->workflow->getWorkdir() + ":" + pwdStr + "/results/" + this->workflow->getWorkdir() + "\"\n";

				for (auto y : this->stages)
				{
					bb = y.second->getBB(x.second->getName());
					if (bb != NULL)
					{
						auxPath = pwdStr + "/results/" + this->workflow->getWorkdir() + "/" + y.second->getWorkdir();
						yml_base += "            - \"" + auxPath + ":" + auxPath + "\"\n";

						for (auto s : y.second->getSourceStr())
						{
							if (dirExists(s.c_str()) == 1)
							{
								yml_base += "            - \"" + s + ":" + s + "\"\n";
							}
						}
					}
				}
			}

			// yml_base += "            - \""+x.second->getSource()+":"+x.second->getSource()+"\"\n";
			// yml_base += "            - \""+x.second->getSink()+":"+x.second->getSink()+"\"\n";
			if (this->workflow->getNetwork().empty())
			{
				yml_base += "        networks:\n             - " + this->workflow->getName() + "\n";
			}
			else
			{
				yml_base += "        networks:\n             - " + this->workflow->getNetwork() + "\n";
			}
			yml_base += "        links:\n";
			yml_base += "            - " + x.second->getWorker()->getName() + "\n";
			links += "             - lb" + x.second->getName() + "\n";
		}
	}

	if (this->workflow->getNetwork().empty())
	{
		yml_base += "\n\nnetworks:\n    " + this->workflow->getName() + ":";
	}
	else
	{
		// cout << "\n\n\nHOLAAA\n\n\n" ;
		yml_base += "\n\nnetworks:\n    " + this->workflow->getNetwork() + ":\n        external: true";
	}

	/*if (boost::iequals(mode, "swarm"))
	{
		yml_base += "    proxy:\n        image: 127.0.0.1:5000/microservice:base\n        links:\n" + links;
	}
	else
	{
		yml_base += "    proxy:\n        image: microservice:base\n        links:\n" + links;
	}*/

	// cout << yml_base << endl;

	yml << yml_base << endl;
	yml.close();
}

bool Launcher::downloadData(string apikey, string token, string access)
{
	vector<Catalog *> catalogs = this->workflow->getCatalogs();
	string pwdStr = this->workpath;
	ofstream myfile;
	myfile.open(pwdStr + "/results/" + this->workflow->getName() + "/downloads.txt");
	for (auto catalog : catalogs)
	{
		string java_down_cmd = "java -jar Download.jar " + token + " " + apikey + " " + catalog->getToken() + " 2 1 cinves '" + pwdStr + "/results/" + this->workflow->getName() + "/catalogs" + "/" + catalog->getName() + "' " + access;
		string output = this->workflow->exec_cmd(java_down_cmd.c_str());
		// system(java_down_cmd.c_str());
		myfile << output + "\n\n";
	}
	myfile.close();
	return false;
}

bool Launcher::uploadData(string apikey, string token, string access)
{
	vector<Catalog *> catalogs = this->workflow->getCatalogs();
	string pwdStr = this->workpath;
	for (auto catalog : catalogs)
	{
		string java_down_cmd = "java -jar Upload.jar " + token + " " + apikey + " " + catalog->getToken() + " single bob 2 '" + pwdStr + "/results/catalogs" + "/" + catalog->getName() + "' cinves true " + access;
		string output = this->workflow->exec_cmd(java_down_cmd.c_str());
		// system(java_down_cmd.c_str());
	}
	return false;
}
