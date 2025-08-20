# Syncer C++ Compilation Test Suite

Test suite for validating C++ compilation through the syncer.py middleware layer.

## Architecture Being Tested

```
Web Client → syncer.py (port 55555) → Kit-Manager (port 3090)
```

This tests the production communication flow where:
1. Web frontend sends `compile_cpp_app` commands to syncer.py
2. syncer.py forwards to Kit-Manager's `compile_cpp` endpoint  
3. Kit-Manager processes and streams results back through syncer.py
4. syncer.py forwards results to web client

## Test Structure

```
test/syncer-cpp-tests/
├── 01-basic-hello/          # Basic Hello World through syncer
├── 02-multi-file/           # Multi-file project through syncer  
├── 03-error-handling/       # Error scenarios through syncer
├── 04-concurrent/           # Multiple simultaneous requests
└── utils/                   # Shared test utilities
```

## Running Tests

### Prerequisites
```bash
# Ensure SDV runtime container is running
docker run -d --name sdv-runtime-test --user root \
  -p 3090:3090 -p 55555:55555 \
  -v "$(pwd)/output:/home/dev/data/output:rw" \
  sdv-runtime-production:latest

# Wait for services to start
sleep 20
```

### Individual Tests
```bash
cd test/syncer-cpp-tests/01-basic-hello && node test.js
cd test/syncer-cpp-tests/02-multi-file && node test.js
```

### All Tests
```bash
node test/syncer-cpp-tests/run-all-tests.js
```

## Key Differences from Direct Kit-Manager Tests

- **Port**: Connects to syncer.py on port 55555 (not Kit-Manager on 3090)
- **Command**: Uses `messageToKit` event with `compile_cpp_app` command
- **Response**: Receives `messageToKit-kitReply` events with compilation status
- **Data Format**: Same tree structure, but wrapped in `messageToKit` protocol

## Test Data Format

```javascript
// Message sent to syncer.py
{
  cmd: "compile_cpp_app",
  request_from: "test-client-123", 
  data: {
    files: [/* tree structure */],
    app_name: "TestApp",
    run: true
  }
}

// Response from syncer.py  
{
  kit_id: "runtime-kit-id",
  request_from: "test-client-123",
  cmd: "compile_cpp_app", 
  status: "compile-start|build-done|run-done|...",
  result: "compilation output...",
  isDone: false|true,
  code: 0|1
}
```