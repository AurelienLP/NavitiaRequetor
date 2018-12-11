#include "RequestCreator.h"

#include <boost/algorithm/string.hpp>

#include <iostream>
#include <utility>

void RequestCreator::parseFileAndCreateRequests()
{
    auto fileToParse = std::ifstream(fileToParsePath_.string());
    auto line = std::string();
    while (std::getline(fileToParse, line))
    {
        createAndAddRequest(line);
    }
}

void RequestCreator::addParameter(std::string& request, const std::string& key, const std::string& value)
{
    request += "&" + key + "=" + value;
}

void RequestCreator::createAndAddRequest(const std::string &line)
{
    std::vector<std::string> parametersValue;
    boost::split(parametersValue, line, boost::is_any_of(","));

    auto request = std::string();
    addParameter(request, "from", parametersValue.at(0));
    addParameter(request, "to", parametersValue.at(1));
    addParameter(request, "datetime", parametersValue.at(2));

    requestList_.push_back(request);
}