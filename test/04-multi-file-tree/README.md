# Test 04: Multi-file Project (Tree Structure Format)

## Purpose
Same multi-file functionality as Test 03 but using tree structure format, with enhanced features to demonstrate format equivalence.

## What This Tests
- Complex tree structure conversion
- Nested folder handling in tree format
- Enhanced C++ features (private members, constructors, exceptions)
- Advanced logging with timestamps
- Same compilation result as flat format

## Project Structure (Tree Format)
```javascript
[{
  type: "folder", 
  name: "src",
  items: [
    {type: "file", name: "main.cpp", content: "..."},
    {
      type: "folder",
      name: "math", 
      items: [
        {type: "file", name: "calculator.h", content: "..."},
        {type: "file", name: "calculator.cpp", content: "..."}
      ]
    },
    {
      type: "folder", 
      name: "utils",
      items: [
        {type: "file", name: "logger.h", content: "..."},
        {type: "file", name: "logger.cpp", content: "..."}
      ]
    }
  ]
}]
```

## Enhanced Features vs Test 03
- **Constructor**: Calculator tracks operation count
- **Private Members**: operationCount field
- **Exception Handling**: Division by zero protection
- **Timestamps**: Logger includes current time
- **Additional Methods**: divide() and getOperationCount()

## Learning Objectives
- Master tree structure format for complex projects
- See tree→flat conversion with nested directories
- Compare performance with Test 03
- Understand format independence

## Format Conversion Result
Tree structure converts to:
```
main.cpp
math/calculator.h
math/calculator.cpp  
utils/logger.h
utils/logger.cpp
```

## Run Test
```bash
cd 04-multi-file-tree  
node test.js
```

## Expected Output
```
[INFO] HH:MM:SS - Tree structure multi-file project starting
25 + 17 = 42
6 × 8 = 48  
[INFO] HH:MM:SS - Tree structure project completed successfully
```

## Success Criteria
- Tree structure detected and converted
- All nested folders preserved as paths
- Same build performance as Test 03
- Enhanced C++ features work correctly
- Timestamps appear in logs

## Comparison with Test 03
| Aspect | Test 03 (Flat) | Test 04 (Tree) |
|--------|----------------|----------------|
| Format | Key-value pairs | Nested objects |
| Conversion | None needed | Auto-converted |
| File Paths | Pre-flattened | Generated from tree |
| Result | Identical binaries | Identical binaries |