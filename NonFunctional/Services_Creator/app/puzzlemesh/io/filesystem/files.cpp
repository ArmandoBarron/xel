#include "files.h"


int dirExists(const char *path)
{
    struct stat info;

    if (stat(path, &info) != 0)
        return 0;
    else if (info.st_mode & S_IFDIR)
        return 1;
    else
        return 0;
}

string getFileName(const string &s)
{

    char sep = '/';

#ifdef _WIN32
    sep = '\\';
#endif

    size_t i = s.rfind(sep, s.length());
    if (i != string::npos)
    {
        return (s.substr(i + 1, s.length() - i));
    }

    return ("");
}

string getFileNameWithoutExt(const string &s)
{

    char sep = '/';

    #ifdef _WIN32
        sep = '\\';
    #endif

    size_t i = s.rfind(sep, s.length());
    if (i != string::npos)
    {
        string aux = (s.substr(i + 1, s.length() - i));
        size_t lastindex = aux.find_first_of(".");
        return aux.substr(0, lastindex);
    }

    return ("");
}


string pwd()
{
    char cwd[1024];
    getcwd(cwd, sizeof(cwd));
    return string(cwd);
}

void listFiles(const std::string &path, std::vector<string> &v)
{
    if (auto dir = opendir(path.c_str()))
    {
        while (auto f = readdir(dir))
        {
            if (!f->d_name || f->d_name[0] == '.')
                continue;
            if (f->d_type == DT_DIR)

                listFiles(path + f->d_name + "/", v);

            if (f->d_type == DT_REG)
                v.push_back(path + f->d_name);
        }
        closedir(dir);
    }
}

vector<string> getFilesInDir(string path)
{
    std::vector<string> files;
    listFiles(path, files);
    return files;
}

bool isDir(string dir)
{
    struct stat fileInfo;
    stat(dir.c_str(), &fileInfo);
    if (S_ISDIR(fileInfo.st_mode))
    {
        return true;
    }
    else
    {
        return false;
    }
}

void recursive_file_list(string directory, vector<string> &paths)
{
    DIR *dir;
    dirent *pdir;
    dir = opendir(directory.c_str());
    if (dir)
    {

        while (pdir = readdir(dir))
        {
            if (pdir->d_type == DT_DIR)
            {
                if (pdir->d_name[0] != '.')
                {
                    recursive_file_list(directory + "/" + pdir->d_name, paths);
                }
            }
            else
            {
                paths.push_back(directory + "/" + pdir->d_name);
            }
        }
        closedir(dir);
    }
}

string dirnameOf(const std::string& fname)
{
     size_t pos = fname.find_last_of("\\/");
     return (std::string::npos == pos)
         ? ""
         : fname.substr(0, pos);
}


/**
 * Returns the size of a file
 */
long filesize(const char *filename)
{
    struct stat stat_buf;
    int rc = stat(filename, &stat_buf);
    return rc == 0 ? stat_buf.st_size : -1;
}

static int do_mkdir(const char *path, mode_t mode)
{
    Stat            st;
    int             status = 0;

    if (stat(path, &st) != 0)
    {
        /* Directory does not exist. EEXIST for race condition */
        if (mkdir(path, mode) != 0 && errno != EEXIST)
            status = -1;
    }
    else if (!S_ISDIR(st.st_mode))
    {
        errno = ENOTDIR;
        status = -1;
    }

    return(status);
}

