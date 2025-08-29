# Simple Counter Demo

A basic demonstration of shared memory integration with real-time variable monitoring.

## Features

- Simple counter that increments every second
- Real-time monitoring via shared memory
- Bidirectional communication (read/write variables)

## Monitored Variables

- `counter` (int) - Main counter value
- `test` (int) - Test variable for modifications

## Build & Run

```bash
mkdir build && cd build
cmake .. && make
./counter
```

## Testing Shared Memory

While the program runs, you can monitor and modify variables through the Kit Manager's shared memory interface.