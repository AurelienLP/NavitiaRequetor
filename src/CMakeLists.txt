cmake_minimum_required(VERSION 3.0)

set(EXEC_NAME "navitiaRequetor")

add_executable(${EXEC_NAME}
  Requetor.cpp
  Curler.cpp
  RequestCreator.cpp
)

find_package( CURL COMPONENTS program_options REQUIRED )
find_package( Boost 1.65 COMPONENTS program_options REQUIRED )

include_directories("${CMAKE_SOURCE_DIR}/include"
                    ${Boost_INCLUDE_DIR}
                    ${CURL_INCLUDE_DIRS})

target_link_libraries(${EXEC_NAME} curl boost_system boost_filesystem)
                    
