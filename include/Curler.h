#pragma once

#include <curl/curl.h>

#include <vector>
#include <string>

class Curler
{
  public:
    Curler();
    ~Curler();

    Curler(const Curler &) = delete;

    std::string lauchRequest(const std::string& request);

  private:
    static std::size_t callback(const char *in, std::size_t size, std::size_t num, std::string *out)
    {
        const std::size_t totalBytes(size * num);
        out->append(in, totalBytes);
        return totalBytes;
    }

  private:
    CURL *curl_;
    int httpCode_;
    std::string httpResponse_;

    const std::string url_ = "localhost:5000/v1/coverage/default/journeys?";
};