INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_MEROMORPH meromorph)

FIND_PATH(
    MEROMORPH_INCLUDE_DIRS
    NAMES meromorph/api.h
    HINTS $ENV{MEROMORPH_DIR}/include
        ${PC_MEROMORPH_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    MEROMORPH_LIBRARIES
    NAMES gnuradio-meromorph
    HINTS $ENV{MEROMORPH_DIR}/lib
        ${PC_MEROMORPH_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
          )

include("${CMAKE_CURRENT_LIST_DIR}/meromorphTarget.cmake")

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(MEROMORPH DEFAULT_MSG MEROMORPH_LIBRARIES MEROMORPH_INCLUDE_DIRS)
MARK_AS_ADVANCED(MEROMORPH_LIBRARIES MEROMORPH_INCLUDE_DIRS)
