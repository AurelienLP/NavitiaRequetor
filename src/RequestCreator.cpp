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
    auto const pointFrom = parametersValue.at(0) + ";" + parametersValue.at(1);
    auto const pointTo = parametersValue.at(2) + ";" + parametersValue.at(3);
    addParameter(request, "from", pointFrom);
    addParameter(request, "to", pointTo);
    addParameter(request, "datetime", parametersValue.at(4));
    addParameter(request, "first_section_mode", "walking");
    addParameter(request, "last_section_mode", "car");

    requestList_.push_back(request);
}