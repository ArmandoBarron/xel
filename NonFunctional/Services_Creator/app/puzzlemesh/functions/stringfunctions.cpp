#include "stringfunctions.h"

std::string &ltrim(std::string &str)
{
	str.erase(0, str.find_first_not_of(" \n\r\t\f\v"));
	return str;
}

std::string &rtrim(std::string &str)
{
	str.erase(str.find_last_not_of(" \n\r\t\f\v") + 1);
	return str;
}

std::string &trim(std::string &str)
{
	return ltrim(rtrim(str));
}

const std::vector<std::string> explode(const std::string &s, const char &c)
{
	std::string buff{""};
	std::vector<std::string> v;

	for (auto n : s)
	{
		if (n != c)
			buff += n;
		else if (n == c && buff != "")
		{
			v.push_back(buff);
			buff = "";
		}
	}
	if (buff != "")
		v.push_back(buff);

	return v;
}

const std::vector<std::string> explode_one(const std::string &s, const char &c)
{
	std::string buff{""};
	std::vector<std::string> v;
	int aux = 0;

	for (auto n : s)
	{
		if (n != c)
			buff += n;
		else if (n == c && buff != "" && aux==0)
		{
			v.push_back(buff);
			buff = "";
			aux = 1;
		}
	}
	if (buff != "")
		v.push_back(buff);

	return v;
}
