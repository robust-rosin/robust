#ifndef PARAM_READER_H
#define PARAM_READER_H

#include <string>
#include <utility>
#include <map>

#include "tinyxml2.h"

using tinyxml2::XMLDocument;
using tinyxml2::XMLElement;

typedef std::pair<std::string, std::string> Param;
typedef std::map<std::string, Param> M_param;

class ParamReader {
public:
    ParamReader();
    M_param *parseLaunch(const char *file);

private:
    void parseParams(XMLElement *el, std::string const& ns, M_param &priv_params);
    void readParam(XMLElement *el, std::string const& ns, M_param &priv_params);
    void readGroup(XMLElement *el, std::string const& ns, M_param priv_params);
    void readNode(XMLElement *el, std::string const& ns, M_param priv_params);
    void makePrivParams(std::string const& ns, M_param const& priv_params);
    std::string resolve(std::string const& ns, const char *name);

    M_param *params_;
    bool node_scope_;
};

ParamReader::ParamReader() : params_(NULL), node_scope_(false) {}

M_param *ParamReader::parseLaunch(const char *file) {
    XMLDocument doc;
    doc.LoadFile(file);
    if (doc.ErrorID()) { return NULL; }
    XMLElement *launch = doc.FirstChildElement("launch");
    if (!launch) { return NULL; }
    std::string ns("");
    M_param *params = params_ = new M_param();
    M_param priv_params;
    for (XMLElement *child = launch->FirstChildElement(); child;
            child = child->NextSiblingElement()) {
        parseParams(child, ns, priv_params);
    }
    params_ = NULL;
    return params;
}

void ParamReader::parseParams(XMLElement *el, std::string const& ns,
                                M_param &priv_params) {
    if (!el) return;
    std::string tag(el->Name());
    if (tag == "param") {
        readParam(el, ns, priv_params);
    } else if (tag == "group") {
        readGroup(el, ns, priv_params);
    } else if (tag == "node") {
        readNode(el, ns, priv_params);
    }
}

void ParamReader::readParam(XMLElement *el, std::string const& ns,
                            M_param &priv_params) {
    const char *name = el->Attribute("name");
    const char *type = el->Attribute("type");
    const char *value = el->Attribute("value");
    if (!type) type = "auto";
    if (!value) value = "";
    Param data = std::make_pair(type, value);
    if (name[0] == '/') {
        (*params_)[name] = data;
    } else if (name[0] == '~') {
        if (node_scope_) {
            (*params_)[resolve(ns, name + 1)] = data;
        } else {
            priv_params[name + 1] = data;
        }
    } else {
        (*params_)[resolve(ns, name)] = data;
    }
}

void ParamReader::readGroup(XMLElement *el, std::string const& ns,
                            M_param priv_params) {
    std::string subns = resolve(ns, el->Attribute("ns"));
    for (XMLElement *child = el->FirstChildElement(); child;
            child = child->NextSiblingElement()) {
        parseParams(child, subns, priv_params);
    }
}

void ParamReader::readNode(XMLElement *el, std::string const& ns,
                           M_param priv_params) {
    node_scope_ = true;
    const char *name = el->Attribute("name");
    if (!name) name = el->Attribute("type");
    std::string subns = resolve(ns, name);
    makePrivParams(subns, priv_params);
    for (XMLElement *child = el->FirstChildElement(); child;
            child = child->NextSiblingElement()) {
        parseParams(child, subns, priv_params);
    }
    node_scope_ = false;
}

void ParamReader::makePrivParams(std::string const& ns,
                                 M_param const& priv_params) {
    for(M_param::const_iterator it = priv_params.begin();
            it != priv_params.end(); ++it) {
        (*params_)[resolve(ns, it->first.c_str())] = it->second;
    }
}

std::string ParamReader::resolve(std::string const& ns, const char *name) {
    if (!name) return std::string(ns);
    if (name[0] == '/') return std::string(name);
    return std::string(ns) + "/" + name;
}

#endif
