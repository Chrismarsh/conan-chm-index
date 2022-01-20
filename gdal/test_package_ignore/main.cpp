#include <iostream>

#include "gdal.h"

int main(int argc, char *argv[]) {
    const char* request = "GDAL_VERSION_NUM";
    const char* info = GDALVersionInfo(request);
    std::cout << "Hello Gdal " << info << std::endl;
    return 0;
}
