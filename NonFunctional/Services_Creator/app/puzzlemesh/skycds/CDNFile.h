//
// Created by domizzi on 14/06/21.
//

#ifndef PIECE_CDNFILE_H
#define PIECE_CDNFILE_H

#include <string>

class CDNFile {
private:
    std::string id;
    std::string name;
    long size;
    std::string path;
    int chunks;
public:
    CDNFile(const std::string &id, const std::string &name, long size, int chunks);

    const std::string &getId() const;

    void setId(const std::string &id);

    const std::string &getName() const;

    void setName(const std::string &name);

    long getSize() const;

    void setSize(long size);

    const std::string &getPath() const;

    void setPath(const std::string &path);

    int getChunks() const;

    void setChunks(int chunks);

};


#endif //PIECE_CDNFILE_H
