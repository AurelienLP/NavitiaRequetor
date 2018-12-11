#include "RequestCreator.h"
#include "Curler.h"

#include <boost/filesystem.hpp>

#include <cstdint>
#include <iostream>
#include <memory>
#include <string>
#include <fstream>

void writeInFile(const boost::filesystem::path &outputDirectory, const std::string &s, size_t idRequest)
{
    auto outputFilePath = outputDirectory / std::string("response" + std::to_string(idRequest) + ".json");
    auto outputFile = std::ofstream(outputDirectory.string());
    outputFile.open(outputFilePath.string());
    outputFile << s;
    outputFile.close();
}

int main(int argc, char *argv[])
{
    if (argc != 3)
    {
        std::cerr << "ERROR : Not enough argument" << std::endl;
        return EXIT_FAILURE;
    }

    const auto fileToParsePath = boost::filesystem::path(argv[1]);
    if (!boost::filesystem::exists(fileToParsePath))
    {
        std::cerr << "ERROR : The input file doesn't exist" << std::endl;
        return EXIT_FAILURE;
    }

    const auto outputDirectory = boost::filesystem::path(argv[2]);
    if (!boost::filesystem::is_directory(outputDirectory))
    {
        std::cerr << "ERROR : The output path is not a directory" << std::endl;
        return EXIT_FAILURE;
    }

    RequestCreator rc(fileToParsePath);
    rc.parseFileAndCreateRequests();

    Curler c;
    size_t idRequest = 0;
    for (auto const &request : rc.getRequestList())
    {
        auto response = c.lauchRequest(request);
        if (!response.empty())
        {
            writeInFile(outputDirectory, response, ++idRequest);
        }
    }

    return EXIT_SUCCESS;
}