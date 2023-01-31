//
// Created by domizzi on 08/06/21.
//

#include "Catalog.h"

const std::string &Catalog::getName() const {
    return name;
}

void Catalog::setName(const std::string &name) {
    Catalog::name = name;
}

const std::string &Catalog::getToken() const {
    return token;
}

void Catalog::setToken(const std::string &token) {
    Catalog::token = token;
}

Catalog::Catalog(const std::string &name, const std::string &token) : name(name), token(token) {
    this->name = name;
    this->token = token;
}

Catalog::Catalog(const std::string &token) : token(token) {
    this->token = token;
}
