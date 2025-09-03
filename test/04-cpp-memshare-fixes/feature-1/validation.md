# Feature 1 Validation: Frontend Data Structure Fix

## What was Fixed
- Updated `DaRuntimeConnector.tsx` to send proper JSON project structure for C++ apps
- Enhanced debugging output for WebSocket messages
- Added comprehensive error logging in onKitReply handler

## Changes Made

### Frontend Changes (`autowrx/src/components/molecules/DaRuntimeConnector.tsx`)
1. **Project Structure**: For C++ apps, the `code` field now contains a JSON string with project structure:
   ```typescript
   const projectStructure = [
     {
       type: "file",
       name: "main.cpp", 
       content: code
     }
   ]
   messageData.code = JSON.stringify(projectStructure)
   ```

2. **Enhanced Logging**: Added debug logging for C++ project structure and WebSocket messages
3. **Error Handling**: Added comprehensive error logging in onKitReply

### Backend Changes (`sdv-runtime-fork/kuksa-syncer/syncer.py`)
1. **Added run_cpp_app Handler**: Complete C++ application processing pipeline:
   - Validates JSON project structure
   - Extracts main.cpp content
   - Compiles with g++ (C++17, pthread support)
   - Runs compiled binary using subpiper
   - Provides detailed error messages

2. **Error Validation**: Comprehensive validation of request format:
   - Checks for data field presence
   - Validates code field in data
   - JSON parsing validation
   - File extraction validation

3. **Module Dependencies**: Fixed velocitas module issue with stub functions

## Test Procedure

### Step 1: Deploy Test C++ Project
1. Create a C++ prototype with language set to "cpp"
2. Add watch variables: `counter`, `speed`, `active`
3. Use the test.cpp code provided
4. Deploy and run the project

### Step 2: Verify WebSocket Messages
Check browser console for:
```
[C++] Sending project structure: [{type: "file", name: "main.cpp", content: "..."}]
[C++] Watch vars: counter, speed, active
[runApp] Sending run_cpp_app with data: {language: "cpp", watch_vars: "counter, speed, active", code: "[{...}]", name: "TestApp"}
```

### Step 3: Verify Backend Processing
Check runtime logs for:
```
Valid JSON code received, processing project data...
App directory cleaned successfully
Project content created successfully
Compiling project...
Running app...
Starting automatic variable monitoring using shared memory...
```

### Step 4: Verify Variable Updates
Check browser console for:
```
[trace_vars] Received data from Runtime-XXX: {counter: "5", speed: "62.5", active: "1"}
[trace_vars] Updated traceVars with 3 variables
```

### Step 5: Verify UI Display
- Variables should appear in the prototype variables watch panel
- Values should update in real-time as the C++ app runs
- Changes should be visible every second

## Expected Results

✅ **PASS Criteria:**
- Frontend sends correct JSON project structure
- Backend processes project without errors
- C++ app compiles and runs successfully
- Shared memory monitoring starts
- trace_vars messages are received
- Variables display in frontend UI with real-time updates

❌ **FAIL Criteria:**
- JSON parsing errors in backend
- Compilation failures
- No trace_vars messages received
- Variables not displaying in UI
- Values not updating

## Debugging Commands

If issues occur:
1. Check browser console for WebSocket message logs
2. Check runtime container logs: `docker logs <runtime_container>`
3. Verify shared memory: `ls -la /dev/shm/my_shm` inside container
4. Check C++ process: `ps aux | grep main_bin` inside container

## Status
- [ ] Test created
- [ ] Manual test passed
- [ ] Variables visible in UI
- [ ] Real-time updates working
- [ ] Ready for next feature