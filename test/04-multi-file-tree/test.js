// Copyright (c) 2025 Eclipse Foundation.
// 
// This program and the accompanying materials are made available under the
// terms of the MIT License which is available at
// https://opensource.org/licenses/MIT.
//
// SPDX-License-Identifier: MIT

// Test 04: Multi-file Project (Tree Structure Format)
const testConfig = require('../utils/test-config');

const TEST_NAME = '04 Multi-file Project (Tree Structure Format)';

const FILES = [
    {
        type: "folder", 
        name: "src",
        items: [
            {
                type: "file",
                name: "main.cpp",
                content: `#include <iostream>
#include "math/calculator.h"
#include "utils/logger.h"

int main() {
    Logger::info("Tree structure multi-file project starting");
    
    Calculator calc;
    int sum = calc.add(25, 17);
    int product = calc.multiply(6, 8);
    
    std::cout << "25 + 17 = " << sum << std::endl;
    std::cout << "6 × 8 = " << product << std::endl;
    
    Logger::info("Tree structure project completed successfully");
    return 0;
}`
            },
            {
                type: "folder",
                name: "math",
                items: [
                    {
                        type: "file", 
                        name: "calculator.h",
                        content: `#pragma once

class Calculator {
private:
    int operationCount;
    
public:
    Calculator();
    int add(int a, int b);
    int subtract(int a, int b);
    int multiply(int a, int b);
    int divide(int a, int b);
    int getOperationCount() const;
};`
                    },
                    {
                        type: "file",
                        name: "calculator.cpp", 
                        content: `#include "calculator.h"
#include <stdexcept>

Calculator::Calculator() : operationCount(0) {}

int Calculator::add(int a, int b) {
    operationCount++;
    return a + b;
}

int Calculator::subtract(int a, int b) {
    operationCount++;
    return a - b;
}

int Calculator::multiply(int a, int b) {
    operationCount++;
    return a * b;
}

int Calculator::divide(int a, int b) {
    operationCount++;
    if (b == 0) {
        throw std::runtime_error("Division by zero");
    }
    return a / b;
}

int Calculator::getOperationCount() const {
    return operationCount;
}`
                    }
                ]
            },
            {
                type: "folder",
                name: "utils",
                items: [
                    {
                        type: "file",
                        name: "logger.h",
                        content: `#pragma once
#include <iostream>
#include <string>
#include <ctime>

class Logger {
public:
    static void info(const std::string& message);
    static void error(const std::string& message);
    static void warning(const std::string& message);
private:
    static std::string getCurrentTime();
};`
                    },
                    {
                        type: "file", 
                        name: "logger.cpp",
                        content: `#include "logger.h"
#include <iomanip>
#include <sstream>

void Logger::info(const std::string& message) {
    std::cout << "[INFO] " << getCurrentTime() << " - " << message << std::endl;
}

void Logger::error(const std::string& message) {
    std::cout << "[ERROR] " << getCurrentTime() << " - " << message << std::endl;
}

void Logger::warning(const std::string& message) {
    std::cout << "[WARN] " << getCurrentTime() << " - " << message << std::endl;
}

std::string Logger::getCurrentTime() {
    time_t now = time(0);
    tm* timeinfo = localtime(&now);
    std::stringstream ss;
    ss << std::setfill('0') << std::setw(2) << timeinfo->tm_hour 
       << ":" << std::setw(2) << timeinfo->tm_min
       << ":" << std::setw(2) << timeinfo->tm_sec;
    return ss.str();
}`
                    }
                ]
            }
        ]
    }
];

testConfig.runTest({
    testName: TEST_NAME,
    files: FILES,
    appName: 'MultiFileTree',
    run: true,
    timeout: 35000,
    expectedOutput: '25 + 17 = 42'
});