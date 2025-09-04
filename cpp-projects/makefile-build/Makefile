# Makefile for testing Makefile-based compilation
CXX = g++
CXXFLAGS = -Wall -Wextra -std=c++17 -g -O0 -pthread
INCLUDES = -Iinclude
SRCDIR = src
OBJDIR = obj
TARGET = makefile_system

# Source files
SOURCES = $(wildcard $(SRCDIR)/*.cpp)
OBJECTS = $(SOURCES:$(SRCDIR)/%.cpp=$(OBJDIR)/%.o)

.PHONY: all clean debug

all: $(TARGET)

$(TARGET): $(OBJECTS)
	$(CXX) $(OBJECTS) -o $@ $(CXXFLAGS)
	@echo "✅ Makefile build completed: $(TARGET)"

$(OBJDIR)/%.o: $(SRCDIR)/%.cpp | $(OBJDIR)
	$(CXX) $(CXXFLAGS) $(INCLUDES) -c $< -o $@
	@echo "🔧 Compiled: $<"

$(OBJDIR):
	mkdir -p $(OBJDIR)

debug: CXXFLAGS += -DDEBUG -g
debug: $(TARGET)

clean:
	rm -rf $(OBJDIR) $(TARGET)
	@echo "🧹 Cleaned build artifacts"

# Display build info
info:
	@echo "📋 Build Configuration:"
	@echo "   CXX: $(CXX)"
	@echo "   CXXFLAGS: $(CXXFLAGS)"
	@echo "   Sources: $(SOURCES)"
	@echo "   Target: $(TARGET)"