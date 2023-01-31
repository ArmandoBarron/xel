#include <string>
#include <vector>

std::string& ltrim(std::string& str);
std::string& rtrim(std::string& str);
std::string& trim(std::string& str);
const std::vector<std::string> explode(const std::string& s, const char& c);
const std::vector<std::string> explode_one(const std::string& s, const char& c);
