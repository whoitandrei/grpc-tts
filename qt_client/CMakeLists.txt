cmake_minimum_required(VERSION 3.21)

project(TTSQtClient VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)

find_package(Qt6 REQUIRED COMPONENTS Widgets Network Multimedia)

qt_add_executable(tts_qt_client
    src/main.cpp
    src/MainWindow.cpp
)

target_link_libraries(tts_qt_client
    PRIVATE
        Qt6::Widgets
        Qt6::Network
        Qt6::Multimedia
)

if(APPLE)
    set_target_properties(tts_qt_client PROPERTIES MACOSX_BUNDLE TRUE)
endif()
