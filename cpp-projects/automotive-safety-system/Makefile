# Makefile for Automotive Safety System
# Simple single-file C++ project with atomic variables

CXX = g++
CXXFLAGS = -std=c++17 -g -O0 -pthread
TARGET = automotive_safety
SOURCE = main.cpp

.PHONY: all clean run

all: $(TARGET)

$(TARGET): $(SOURCE)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(SOURCE)

run: $(TARGET)
	./$(TARGET)

clean:
	rm -f $(TARGET)

# Build with optimizations
release: CXXFLAGS = -std=c++17 -O2 -pthread
release: $(TARGET)

# Build with debugging and address sanitizer
debug: CXXFLAGS = -std=c++17 -g -O0 -pthread -fsanitize=address
debug: $(TARGET)