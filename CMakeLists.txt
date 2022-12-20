cmake_minimum_required(VERSION 3.18)

project(aldi-pixel-font LANGUAGES NONE)

find_package(Python REQUIRED)
find_package(Git REQUIRED)

set(REQUIRED_PACKAGES
    pyinstaller
    PyQt6
    construct
)

execute_process(COMMAND ${Python_EXECUTABLE} -m pip install ${REQUIRED_PACKAGES})
execute_process(COMMAND ${GIT_EXECUTABLE} describe --tags --always OUTPUT_VARIABLE VERSION OUTPUT_STRIP_TRAILING_WHITESPACE)
configure_file(${PROJECT_SOURCE_DIR}/pixelfont/fonteditor.spec.in fonteditor.spec)

find_program(PYINSTALLER NAMES pyinstaller)

add_custom_target(fonteditor-${VERSION}.exe ALL COMMAND ${PYINSTALLER} ${PROJECT_BINARY_DIR}/fonteditor.spec --distpath ${CMAKE_INSTALL_PREFIX} --workpath ${PROJECT_BINARY_DIR}/pixelfont -y)
configure_file(pack.cmake.in pack.cmake)
install(SCRIPT ${PROJECT_BINARY_DIR}/pack.cmake)
