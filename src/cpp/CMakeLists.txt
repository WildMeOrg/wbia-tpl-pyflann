# include_directories(${CMAKE_SOURCE_DIR}/include algorithms ext util nn .)

message(STATUS "PYFLANN_VERSION = ${PYFLANN_VERSION}")
set(FLANN_VERSION ${PYFLANN_VERSION})
message(STATUS "FLANN_VERSION = ${FLANN_VERSION}")
add_definitions(-D_PYFLANN_VERSION=${PYFLANN_VERSION})
add_definitions(-DPYFLANN_VERSION_=${PYFLANN_VERSION})
add_definitions(-DPYFLANN_VERSION=${PYFLANN_VERSION})
add_definitions(-D_FLANN_VERSION=${FLANN_VERSION})
add_definitions(-DFLANN_VERSION_=${FLANN_VERSION})
add_definitions(-DFLANN_VERSION=${FLANN_VERSION})

configure_file(${CMAKE_CURRENT_SOURCE_DIR}/flann/config.h.in
               ${CMAKE_CURRENT_SOURCE_DIR}/flann/config.h)

file(GLOB_RECURSE C_SOURCES flann.cpp lz4.c lz4hc.c)
file(GLOB_RECURSE CPP_SOURCES flann_cpp.cpp lz4.c lz4hc.c)
file(GLOB_RECURSE CU_SOURCES *.cu)
file(GLOB_RECURSE HEADER_SOURCES flann.h lz4hc.h lz4.h)

link_directories(${LZ4_LIBRARY_DIRS})
include_directories(${LZ4_INCLUDE_DIRS})

add_library(flann_cpp_s STATIC ${CPP_SOURCES})

if(USE_MPI)
  target_link_libraries(flann_cpp_s ${MPI_LIBRARIES})
endif()

if(LZ4_FOUND)
  target_link_libraries(flann_cpp_s ${LZ4_LIBRARIES})
  target_include_directories(flann_cpp_s PUBLIC ${LZ4_INCLUDE_DIRS})
endif()

if(OPENMP_FOUND)
  target_link_libraries(flann_cpp_s ${OpenMP_CXX_LIBRARIES})
endif()

if(Boost_FOUND)
  target_link_libraries(flann_cpp_s ${Boost_LIBRARIES})
endif()

if(CMAKE_COMPILER_IS_GNUCC OR CMAKE_COMPILER_IS_CLANG)
  set_target_properties(flann_cpp_s PROPERTIES COMPILE_FLAGS -fPIC)
endif()

set_property(TARGET flann_cpp_s PROPERTY COMPILE_DEFINITIONS FLANN_STATIC
                                         FLANN_USE_CUDA)

if(BUILD_C_BINDINGS)
  add_library(flann_s STATIC ${C_SOURCES})

  if(USE_MPI)
    target_link_libraries(flann_s ${MPI_LIBRARIES})
  endif()

  if(LZ4_FOUND)
    target_link_libraries(flann_s ${LZ4_LIBRARIES})
    target_include_directories(flann_s PUBLIC ${LZ4_INCLUDE_DIRS})
  endif()

  if(OPENMP_FOUND)
    target_link_libraries(flann_s ${OpenMP_C_LIBRARIES})
  endif()

  if(Boost_FOUND)
    target_link_libraries(flann_s ${Boost_LIBRARIES})
  endif()

  if(CMAKE_COMPILER_IS_GNUCC OR CMAKE_COMPILER_IS_CLANG)
    set_target_properties(flann_s PROPERTIES COMPILE_FLAGS -fPIC)
  endif()

  set_property(TARGET flann_s PROPERTY COMPILE_DEFINITIONS FLANN_STATIC)
endif()

if(BUILD_CUDA_LIB)
  set(CUDA_NVCC_FLAGS "${CUDA_NVCC_FLAGS};-DFLANN_USE_CUDA")

  if(CMAKE_COMPILER_IS_GNUCC)
    set(CUDA_NVCC_FLAGS "${CUDA_NVCC_FLAGS};-Xcompiler;-fPIC;")
    if(NVCC_COMPILER_BINDIR)
      set(CUDA_NVCC_FLAGS
          "${CUDA_NVCC_FLAGS};--compiler-bindir=${NVCC_COMPILER_BINDIR}")
    endif()
  else()
    set(CUDA_NVCC_FLAGS "${CUDA_NVCC_FLAGS};")
  endif()

  cuda_add_library(flann_cuda_s STATIC ${CU_SOURCES})

  set_property(TARGET flann_cuda_s PROPERTY COMPILE_DEFINITIONS FLANN_STATIC)
endif()

add_library(flann_cpp SHARED "${CMAKE_CURRENT_SOURCE_DIR}/flann/flann.h")

if(BUILD_C_BINDINGS)
  add_library(flann SHARED "${CMAKE_CURRENT_SOURCE_DIR}/flann/flann.h")
endif()

if(BUILD_CUDA_LIB)
  cuda_add_library(flann_cuda SHARED
                   "${CMAKE_CURRENT_SOURCE_DIR}/flann/flann.h")
endif()

if(OS_IS_LINUX)
  set_target_properties(flann_cpp PROPERTIES LINKER_LANGUAGE CXX)
  set(LINK_FLAG_PREFIX "-Wl,--whole-archive")
  set(LINK_FLAG_POSTFIX "-Wl,--no-whole-archive")

  if(BUILD_C_BINDINGS)
    set_target_properties(flann PROPERTIES LINKER_LANGUAGE CXX)
  endif()

  if(BUILD_CUDA_LIB)
    set_target_properties(flann_cuda PROPERTIES LINKER_LANGUAGE CXX)
  endif()
elseif(OS_IS_MACOS)
  set(LINK_FLAG_PREFIX "-Wl,-force_load")
else()
  set_target_properties(flann_cpp PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS YES)
  set(LINK_FLAG_PREFIX "/WHOLEARCHIVE")

  if(BUILD_C_BINDINGS)
    set_target_properties(flann PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS YES)
  endif()

  if(BUILD_CUDA_LIB)
    set_target_properties(flann_cuda PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS YES)
  endif()
endif()

target_link_libraries(flann_cpp ${LINK_FLAG_PREFIX} flann_cpp_s
                      ${LINK_FLAG_POSTFIX})

if(BUILD_C_BINDINGS)
  target_link_libraries(flann ${LINK_FLAG_PREFIX} flann_s ${LINK_FLAG_POSTFIX})
endif()

if(BUILD_CUDA_LIB)
  target_link_libraries(flann_cpp_cuda ${LINK_FLAG_PREFIX} flann_cuda_s
                        ${LINK_FLAG_POSTFIX})
  # target_link_libraries(flann_cuda cudpp_x86_64)
endif()

set_target_properties(
  flann_cpp PROPERTIES VERSION ${PYFLANN_VERSION} SOVERSION ${FLANN_SOVERSION}
                       DEFINE_SYMBOL FLANN_EXPORTS)

if(BUILD_C_BINDINGS)
  set_target_properties(
    flann PROPERTIES VERSION ${PYFLANN_VERSION} SOVERSION ${FLANN_SOVERSION}
                     DEFINE_SYMBOL FLANN_EXPORTS)
endif()

if(BUILD_CUDA_LIB)
  set_target_properties(
    flann_cuda
    PROPERTIES VERSION ${PYFLANN_VERSION} SOVERSION ${FLANN_SOVERSION}
               DEFINE_SYMBOL FLANN_EXPORTS)
endif()

if(USE_MPI AND HDF5_IS_PARALLEL)
  add_executable(flann_mpi_server flann/mpi/flann_mpi_server.cpp)
  target_link_libraries(
    flann_mpi_server
    ${LINK_FLAG_PREFIX}
    flann_cpp_s
    ${LINK_FLAG_POSTFIX}
    ${HDF5_LIBRARIES}
    ${MPI_LIBRARIES}
    ${Boost_LIBRARIES})

  add_executable(flann_mpi_client flann/mpi/flann_mpi_client.cpp)
  target_link_libraries(
    flann_mpi_client
    ${LINK_FLAG_PREFIX}
    flann_cpp_s
    ${LINK_FLAG_POSTFIX}
    ${HDF5_LIBRARIES}
    ${MPI_LIBRARIES}
    ${Boost_LIBRARIES})
endif()

if(NOT SKBUILD)
  if(WIN32)
    if(BUILD_C_BINDINGS AND BUILD_MATLAB_BINDINGS)
      install(TARGETS flann RUNTIME DESTINATION share/flann/matlab)
    endif()
  endif(WIN32)

  install(
    TARGETS flann_cpp flann_cpp_s
    EXPORT ${targets_export_name}
    INCLUDES
    DESTINATION include
    RUNTIME DESTINATION bin
    LIBRARY DESTINATION ${FLANN_LIB_INSTALL_DIR}
    ARCHIVE DESTINATION ${FLANN_LIB_INSTALL_DIR})

  if(BUILD_C_BINDINGS)
    install(
      TARGETS flann flann_s
      EXPORT ${targets_export_name}
      INCLUDES
      DESTINATION include
      RUNTIME DESTINATION bin
      LIBRARY DESTINATION ${FLANN_LIB_INSTALL_DIR}
      ARCHIVE DESTINATION ${FLANN_LIB_INSTALL_DIR})
  endif()

  if(BUILD_CUDA_LIB)
    install(
      TARGETS flann_cuda flann_cuda_s
      EXPORT ${targets_export_name}
      INCLUDES
      DESTINATION include
      RUNTIME DESTINATION bin
      LIBRARY DESTINATION ${FLANN_LIB_INSTALL_DIR}
      ARCHIVE DESTINATION ${FLANN_LIB_INSTALL_DIR})
  endif()

  if(USE_MPI AND HDF5_IS_PARALLEL)
    install(
      TARGETS flann_mpi_client flann_mpi_server
      EXPORT ${targets_export_name}
      INCLUDES
      DESTINATION include
      RUNTIME DESTINATION bin
      LIBRARY DESTINATION ${FLANN_LIB_INSTALL_DIR}
      ARCHIVE DESTINATION ${FLANN_LIB_INSTALL_DIR})
  endif()

  install(
    DIRECTORY flann
    DESTINATION include
    FILES_MATCHING
    PATTERN "*.h"
    PATTERN "*.hpp")

else()
  # Only install the library files when building with skbuild
  install(
    TARGETS flann_cpp flann_cpp_s
    EXPORT ${targets_export_name}
    LIBRARY DESTINATION ${FLANN_LIB_INSTALL_DIR}
    ARCHIVE DESTINATION ${FLANN_LIB_INSTALL_DIR})

  if(BUILD_C_BINDINGS)
    install(
      TARGETS flann flann_s
      EXPORT ${targets_export_name}
      LIBRARY DESTINATION ${FLANN_LIB_INSTALL_DIR}
      ARCHIVE DESTINATION ${FLANN_LIB_INSTALL_DIR})
  endif()

  if(BUILD_CUDA_LIB)
    install(
      TARGETS flann_cuda flann_cuda_s
      EXPORT ${targets_export_name}
      LIBRARY DESTINATION ${FLANN_LIB_INSTALL_DIR}
      ARCHIVE DESTINATION ${FLANN_LIB_INSTALL_DIR})
  endif()

  if(USE_MPI AND HDF5_IS_PARALLEL)
    install(
      TARGETS flann_mpi_client flann_mpi_server
      EXPORT ${targets_export_name}
      LIBRARY DESTINATION ${FLANN_LIB_INSTALL_DIR}
      ARCHIVE DESTINATION ${FLANN_LIB_INSTALL_DIR})
  endif()
endif()
