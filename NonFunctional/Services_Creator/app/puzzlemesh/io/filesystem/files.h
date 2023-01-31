#include <sys/types.h>
#include <sys/stat.h>
#include <stdio.h>
#include <stdlib.h>
#include <string>
#include <unistd.h>
#include <stdio.h>
#include <vector>
#include <functional>
#include <dirent.h>
#include <iostream>
#include <cstdlib>
#include <string.h>
#include <stddef.h>
#include <cstdio>
#include <fstream>

#include <errno.h>
#include <string.h>

typedef struct stat Stat;
using namespace std;

int dirExists(const char *path);
string getFileName(const string &s);
string pwd();
bool isDir(string dir);
void listFiles(const std::string &path, std::vector<string> &v);
vector<string> getFilesInDir(string path);
void recursive_file_list(string directory, vector<string> &paths);
string getFileNameWithoutExt(const string &s);
/**
 * Returns the size of a file
 * @param filename Path to the fole
 * @return Size of the file
 */
long filesize(const char *filename);
string dirnameOf(const std::string& fname);
