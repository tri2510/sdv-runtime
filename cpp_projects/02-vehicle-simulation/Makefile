CXX = g++
CXXFLAGS = -std=c++17 -g -O0 -Wall
TARGET = vehicle_sim
SOURCE = main.cpp

$(TARGET): $(SOURCE)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(SOURCE)

clean:
	rm -f $(TARGET)

.PHONY: clean