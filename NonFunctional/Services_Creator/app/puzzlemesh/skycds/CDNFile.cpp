//
// Created by domizzi on 14/06/21.
//

#include "CDNFile.h"

CDNFile::CDNFile(const std::string &id, const std::string &name, long size, int chunks) : id(id), name(name), size(size), chunks(chunks) {
    this->id = id;
    this->name = name;
    this->size = size;
    this->chunks = chunks;
}

const std::string &CDNFile::getId() const {
    return id;
}

void CDNFile::setId(const std::string &id) {
    CDNFile::id = id;
}

const std::string &CDNFile::getName() const {
    return name;
}

void CDNFile::setName(const std::string &name) {
    CDNFile::name = name;
}

long CDNFile::getSize() const {
    return size;
}

void CDNFile::setSize(long size) {
    CDNFile::size = size;
}

const std::string &CDNFile::getPath() const {
    return path;
}

void CDNFile::setPath(const std::string &path) {
    CDNFile::path = path;
}

int CDNFile::getChunks() const {
    return chunks;
}

void CDNFile::setChunks(int chunks) {
    CDNFile::chunks = chunks;
}


