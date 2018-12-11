#include "Curler.h"

#include <iostream>
#include <utility>

Curler::Curler()
{
    curl_ = curl_easy_init();

    curl_easy_setopt(curl_, CURLOPT_IPRESOLVE, CURL_IPRESOLVE_V4);

    // Don't wait forever, time out after 10 seconds.
    curl_easy_setopt(curl_, CURLOPT_TIMEOUT, 10);

    // Follow HTTP redirects if necessary.
    curl_easy_setopt(curl_, CURLOPT_FOLLOWLOCATION, 1L);

    // Response information.
    httpCode_ = 0;
    httpResponse_ = std::string();

    // Hook up data handling function.
    curl_easy_setopt(curl_, CURLOPT_WRITEFUNCTION, callback);

    // Hook up data container (will be passed as the last parameter to the
    // callback handling function).  Can be any pointer type, since it will
    // internally be passed as a void pointer.
    curl_easy_setopt(curl_, CURLOPT_WRITEDATA, &httpResponse_);
}

Curler::~Curler()
{
    curl_easy_cleanup(curl_);
}

std::string Curler::lauchRequest(const std::string &request)
{
    httpCode_ = 0;
    httpResponse_ = std::string();

    curl_easy_setopt(curl_, CURLOPT_URL, (url_ + request).c_str());
    curl_easy_perform(curl_);
    curl_easy_getinfo(curl_, CURLINFO_RESPONSE_CODE, &httpCode_);

    if (httpCode_ == 200)
    {
        std::cout << "\nGot successful response from " << (url_ + request) << std::endl;
        return std::move(httpResponse_);
    }
    else
    {
        std::cout << "Couldn't GET from " << (url_ + request) << std::endl;
        return {};
    }
}