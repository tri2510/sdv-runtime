# Makefile for ADAS Systems Monitor
CXX = g++
CXXFLAGS = -g -O0 -std=c++17 -Wall -Wextra -pthread
TARGET = adas_monitor
SOURCES = adas_systems.cpp

# Default target
all: $(TARGET)

# Build the executable
$(TARGET): $(SOURCES)
	@echo "Building ADAS Systems Monitor with Makefile..."
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(SOURCES)
	@echo "Build successful! Executable: $(TARGET)"

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -f $(TARGET)

# Run the program
run: $(TARGET)
	@echo "Running ADAS Systems Monitor..."
	./$(TARGET)

# Help target
help:
	@echo "Available targets:"
	@echo "  all     - Build the ADAS monitor (default)"
	@echo "  clean   - Remove build artifacts"  
	@echo "  run     - Build and run the program"
	@echo "  help    - Show this help message"

.PHONY: all clean run help