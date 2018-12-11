#pragma once

#include <boost/filesystem.hpp>

#include <string>
#include <iostream>
#include <fstream>

class RequestCreator
{
  public:
    RequestCreator(const boost::filesystem::path &fileToParsePath) : fileToParsePath_(fileToParsePath) {}

    RequestCreator(const RequestCreator &) = delete;

    void parseFileAndCreateRequests();

    const std::vector<std::string> &getRequestList() const { return requestList_; }

  private:
    void addParameter(std::string& request, const std::string& key, const std::string& value);
    void createAndAddRequest(const std::string &line);

  private:
    const boost::filesystem::path fileToParsePath_;
    std::vector<std::string> requestList_;
};
