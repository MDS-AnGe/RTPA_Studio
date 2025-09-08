# RTPA Studio - Real-Time Poker Assistant
# Architecture C++20 + Qt6 + OpenCV + Tesseract + CUDA
# Version haute performance sans dépendances Python/Rust

cmake_minimum_required(VERSION 3.20)
project(RTPAStudio VERSION 2.0.0 LANGUAGES CXX)

# Configuration C++20 moderne
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Options de build
option(ENABLE_CUDA "Enable CUDA acceleration" ON)
option(BUILD_TESTS "Build unit tests" ON)
option(ENABLE_OPTIMIZATIONS "Enable aggressive optimizations" ON)

# Configuration Release par défaut
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

# Flags d'optimisation C++20
if(ENABLE_OPTIMIZATIONS)
    set(CMAKE_CXX_FLAGS_RELEASE "-O3 -march=native -mtune=native -flto -DNDEBUG")
    set(CMAKE_CXX_FLAGS_DEBUG "-O0 -g -DDEBUG")
    
    # Optimisations spécifiques GCC/Clang
    if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU" OR CMAKE_CXX_COMPILER_ID STREQUAL "Clang")
        add_compile_options(-ffast-math -funroll-loops -finline-functions)
    endif()
endif()

# Recherche des dépendances critiques
find_package(Qt6 REQUIRED COMPONENTS Core Widgets Gui Charts Network)
find_package(OpenCV REQUIRED)
find_package(PkgConfig REQUIRED)

# Tesseract via pkg-config
pkg_check_modules(TESSERACT REQUIRED tesseract lept)

# CUDA optionnel
if(ENABLE_CUDA)
    find_package(CUDAToolkit QUIET)
    if(CUDAToolkit_FOUND)
        enable_language(CUDA)
        set(CMAKE_CUDA_STANDARD 20)
        add_definitions(-DRTPA_CUDA_ENABLED)
        message(STATUS "✅ CUDA support enabled")
    else()
        message(STATUS "⚠️ CUDA not found, continuing without GPU acceleration")
    endif()
endif()

# SQLite3 pour persistence
find_package(SQLite3 REQUIRED)

# YAML-CPP pour configuration
find_package(PkgConfig REQUIRED)
pkg_check_modules(YAMLCPP REQUIRED yaml-cpp)

# Headers globaux
include_directories(src/)
include_directories(${OpenCV_INCLUDE_DIRS})
include_directories(${TESSERACT_INCLUDE_DIRS})

# Sources principales
set(RTPA_SOURCES
    src/main.cpp
    src/core/AppManager.cpp
    src/core/ConfigManager.cpp
    src/algorithms/CfrEngine.cpp
    src/algorithms/MonteCarloSimulator.cpp
    src/ocr/ScreenCapture.cpp
    src/ocr/TesseractOCR.cpp
    src/ocr/GameStateExtractor.cpp
    src/gui/MainWindow.cpp
    src/gui/GameTable.cpp
    src/gui/ConfigDialog.cpp
    src/gui/StatsWidget.cpp
    src/database/DatabaseManager.cpp
    src/utils/Logger.cpp
    src/utils/PlatformDetector.cpp
)

# Headers
set(RTPA_HEADERS
    src/core/AppManager.h
    src/core/ConfigManager.h
    src/algorithms/CfrEngine.h
    src/algorithms/MonteCarloSimulator.h
    src/ocr/ScreenCapture.h
    src/ocr/TesseractOCR.h
    src/ocr/GameStateExtractor.h
    src/gui/MainWindow.h
    src/gui/GameTable.h
    src/gui/ConfigDialog.h
    src/gui/StatsWidget.h
    src/database/DatabaseManager.h
    src/utils/Logger.h
    src/utils/PlatformDetector.h
    src/types/PokerTypes.h
    src/types/ConfigTypes.h
)

# Sources CUDA optionnels
if(ENABLE_CUDA AND CUDAToolkit_FOUND)
    set(CUDA_SOURCES
        src/cuda/CudaCfrKernels.cu
        src/cuda/CudaMonteCarloKernels.cu
    )
    list(APPEND RTPA_SOURCES ${CUDA_SOURCES})
endif()

# Création de l'exécutable principal
qt6_standard_project_setup()
qt6_add_executable(rtpa-studio ${RTPA_SOURCES} ${RTPA_HEADERS})

# Linking des bibliothèques
target_link_libraries(rtpa-studio 
    Qt6::Core Qt6::Widgets Qt6::Gui Qt6::Charts Qt6::Network
    ${OpenCV_LIBS}
    ${TESSERACT_LIBRARIES}
    SQLite::SQLite3
    ${YAMLCPP_LIBRARIES}
    pthread
)

# CUDA linking si disponible
if(ENABLE_CUDA AND CUDAToolkit_FOUND)
    target_link_libraries(rtpa-studio CUDA::cudart CUDA::curand)
endif()

# Propriétés spécifiques
set_target_properties(rtpa-studio PROPERTIES
    WIN32_EXECUTABLE TRUE
    MACOSX_BUNDLE TRUE
    OUTPUT_NAME "RTPA-Studio"
)

# Installation
install(TARGETS rtpa-studio
    BUNDLE DESTINATION .
    RUNTIME DESTINATION bin
)

# Tests unitaires
if(BUILD_TESTS)
    enable_testing()
    add_subdirectory(tests)
endif()

# Messages de configuration
message(STATUS "==========================================")
message(STATUS "🚀 RTPA Studio C++20 Configuration")
message(STATUS "==========================================")
message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "Qt6: ${Qt6_VERSION}")
message(STATUS "OpenCV: ${OpenCV_VERSION}")
message(STATUS "CUDA: ${CUDAToolkit_FOUND}")
message(STATUS "Optimizations: ${ENABLE_OPTIMIZATIONS}")
message(STATUS "==========================================")