//
// Created by domizzi on 08/06/21.
//

#ifndef PIECE_CATALOG_H
#define PIECE_CATALOG_H

#include<string>

class Catalog {
private:
    std::string name;
    std::string token;
public:
    Catalog(const std::string &token);

    Catalog(const std::string &name, const std::string &token);

    const std::string &getName() const;

    void setName(const std::string &name);

    const std::string &getToken() const;

    void setToken(const std::string &token);
};


#endif //PIECE_CATALOG_H
