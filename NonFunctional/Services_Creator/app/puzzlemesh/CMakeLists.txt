cmake_minimum_required(VERSION 3.19)
project(puzzlemesh)

set(CMAKE_CXX_STANDARD 20)

#Include Curl library
include(FindCURL)
find_package(CURL REQUIRED)
if (NOT CURL_FOUND)
    message (FATAL_ERROR "Curl is not supported")
endif (NOT CURL_FOUND)
include_directories(CURL_INCLUDE_DIRS)
set(CMAKE_REQUIRED_LIBRARIES "${CURL_LIBRARIES}")
list(APPEND LIBS "${CURL_LIBRARIES}")

set(Boost_USE_STATIC_LIBS ON)
set(Boost_USE_MULTITHREADED ON)
set(Boost_NO_BOOST_CMAKE ON)
find_package(Boost COMPONENTS fiber system filesystem iostreams REQUIRED)

find_package(jsoncpp CONFIG REQUIRED)

SET(CMAKE_CXX_FLAGS  "-pthread -lboost_iostreams -isystem \"${JSONCPP_INCLUDE_DIR}\"")
add_executable(puzzlemesh main.cpp ${puzzlemesh_SRC} skycds/APISkyCDS.cpp skycds/APISkyCDS.h skycds/CDNFile.cpp skycds/CDNFile.h skycds/Curl.cpp skycds/Curl.h skycds/Catalog.cpp skycds/Catalog.h buildingcomponents/buildingblock.cpp buildingcomponents/buildingblock.h buildingcomponents/pattern.cpp buildingcomponents/pattern.h buildingcomponents/pipeline.cpp buildingcomponents/pipeline.h buildingcomponents/single.cpp buildingcomponents/single.h buildingcomponents/stage.cpp buildingcomponents/stage.h buildingcomponents/workflow.cpp buildingcomponents/workflow.h functions/stringfunctions.cpp functions/stringfunctions.h io/filesystem/files.cpp io/filesystem/files.h logs/logs.cpp logs/logs.h launcher.cpp launcher.h parser.cpp parser.h)
target_link_libraries(puzzlemesh PRIVATE Boost::headers Boost::fiber Boost::system Boost::filesystem Boost::iostreams ${LIBS} jsoncpp)