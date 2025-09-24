# Copyright (c) 2025 Eclipse Foundation.
# 
# This program and the accompanying materials are made available under the
# terms of the MIT License which is available at
# https://opensource.org/licenses/MIT.
#
# SPDX-License-Identifier: MIT

import signal
import subprocess
from pathlib import Path
from kuksa_client.grpc.aio import VSSClient
from kuksa_client.grpc import VSSClient as KClient
from kuksa_client.grpc import Datapoint
from kuksa_client.grpc import VSSClientError
from kuksa_client.grpc import MetadataField
from kuksa_client.grpc import EntryType
import socketio
import asyncio
from subpiper import subpiper
import time
import os
import sys
import json
from json_array_patch import apply_global_patch

# Apply global JSON patch for array serialization
apply_global_patch()

# Import optional dependencies with proper error handling
try:
    from vehicle_model_manager import generate_vehicle_model, revert_vehicle_model
    VEHICLE_MODEL_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Vehicle model manager not available: {e}")
    VEHICLE_MODEL_AVAILABLE = False
    # Provide dummy functions
    def generate_vehicle_model(*args, **kwargs):
        raise NotImplementedError("Vehicle model manager not available")
    def revert_vehicle_model(*args, **kwargs):
        raise NotImplementedError("Vehicle model manager not available")

try:
    import pkg_manager
    PKG_MANAGER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Package manager not available: {e}")
    PKG_MANAGER_AVAILABLE = False
    # Provide dummy pkg_manager
    class DummyPkgManager:
        @staticmethod
        def listPkg():
            return {"error": "Package manager not available"}
        @staticmethod
        async def installPkg(packages):
            return "Package manager not available"
    pkg_manager = DummyPkgManager()

# Import C++ memory monitoring functionality
try:
    from project_utils import ProjectUtils
    import cpp_memory_debugger as cpp_debugger_util
    CPP_MEMORY_AVAILABLE = True
    print("✓ C++ memory monitoring functionality loaded")
except ImportError as e:
    print(f"Warning: C++ memory monitoring not available: {e}")
    CPP_MEMORY_AVAILABLE = False

BORKER_IP = '127.0.0.1'
BROKER_PORT = 55555

DEFAULT_KIT_SERVER = 'https://kit.digitalauto.tech'
DEFAULT_RUNTIME_NAME = 'TriCPP'
DEFAULT_RUNTIME_PREFIX = 'Runtime-'

TIME_TO_KEEP_SUBSCRIBER_ALIVE = 60
TIME_TO_KEEP_RUNNER_ALIVE = 3*60

# C++ process tracking
cpp_processes = {}  # {from_id: [process_info_dict]}
monitoring_tasks = {}  # {from_id: asyncio.Task} - Store monitoring tasks for cleanup

lsOfRunner = []

lsOfApiSubscriber = {}

sio = socketio.AsyncClient()

client = VSSClient(BORKER_IP, BROKER_PORT)

# Resolve mock signals file relative to repository root to remain deployable
REPO_ROOT = Path(__file__).resolve().parent.parent
mock_signal_path = REPO_ROOT / "mock" / "signals.json"

# Keep a reference to the main event loop for thread-safe callbacks
main_loop = None

def is_process_running_nix(process_name):
    """Check if a process with the given name is running on Linux/macOS."""
    try:
        # Using pgrep (more direct)
        process = subprocess.Popen(['pgrep', '-x', process_name], stdout=subprocess.PIPE)
        output, error = process.communicate()
        return len(output) > 0
    except FileNotFoundError:
        # pgrep might not be available, try ps
        process = subprocess.Popen(['ps', '-ax', '-o', 'comm'], stdout=subprocess.PIPE)
        output, error = process.communicate()
        return process_name.lower().encode() in output.lower()

async def send_app_run_reply(master_id, is_done, retcode, content):
    await sio.emit("messageToKit-kitReply", {
        "kit_id": CLIENT_ID,
        "request_from": master_id,
        "cmd": "run_python_app",
        "data": "",
        "isDone": is_done,
        "result": content,
        "code": retcode
    })

async def send_app_deploy_reply(master_id, content, is_finish, cmd="deploy-request"):
    await sio.emit("messageToKit-kitReply", {
        "token": "12a-124-45634-12345-1swer",
        "request_from": master_id,
        "cmd": cmd,
        "data": "",
        "result": content,
        "is_finish": is_finish
    })

async def send_reply(master_id, content, is_error=False, is_done=False, retcode=0, cmd="run_python_app"):
    """General reply function for C++ operations"""
    message_payload = {
        "kit_id": CLIENT_ID,
        "request_from": master_id,
        "cmd": cmd,
        "data": content,
        "isError": is_error,
        "isDone": is_done,
        "result": content,
        "code": retcode
    }
    
    await sio.emit("messageToKit-kitReply", message_payload)

async def stop_client_processes(from_id):
    """Stop all C++ processes belonging to a specific client"""
    if from_id in cpp_processes:
        print(f"Stopping all C++ processes for client {from_id}", flush=True)
        
        for process_info in cpp_processes[from_id]:
            try:
                if "proc" in process_info and process_info["proc"] is not None:
                    proc = process_info["proc"]
                    pid = process_info.get("pid")
                    
                    print(f"Terminating C++ process PID {pid} for client {from_id}", flush=True)
                    proc.terminate()
                    
                    # Wait for graceful termination
                    try:
                        await asyncio.wait_for(proc.wait(), timeout=5.0)
                        print(f"C++ process PID {pid} terminated gracefully", flush=True)
                    except asyncio.TimeoutExpired:
                        print(f"C++ process PID {pid} didn't terminate gracefully, killing it", flush=True)
                        proc.kill()
                        
            except Exception as e:
                print(f"Error stopping C++ process: {str(e)}", flush=True)
        
        # Clear the client's process list
        del cpp_processes[from_id]
        print(f"Cleared all C++ processes for client {from_id}", flush=True)
        
        # Cancel monitoring task if it exists
        if from_id in monitoring_tasks:
            task = monitoring_tasks[from_id]
            if not task.done():
                print(f"Cancelling monitoring task for client {from_id}")
                task.cancel()
            del monitoring_tasks[from_id]
        
        # Clean up memory monitor
        if CPP_MEMORY_AVAILABLE:
            cpp_debugger_util.cleanup_memory_monitor()
        
        return True
    else:
        print(f"No C++ processes found for client {from_id}", flush=True)
        return False

def _schedule_callback(coro):
    """Dispatch coroutine onto the main event loop from worker threads."""
    if main_loop and main_loop.is_running():
        asyncio.run_coroutine_threadsafe(coro, main_loop)
    else:
        # Fallback for early boot where loop is not yet ready
        asyncio.run(coro)


def process_done(master_id: str, retcode: int):
    _schedule_callback(send_app_run_reply(master_id, True, retcode, ""))


def my_stdout_callback(master_id: str, line: str):
    _schedule_callback(send_app_run_reply(master_id, False, 0, line + '\r\n'))


def my_stderr_callback(master_id: str, line: str):
    _schedule_callback(send_app_run_reply(master_id, False, 0, line + '\r\n'))


@sio.event
async def connect():
    print('Connected to Kit Server ',flush=True)
    await sio.emit("register_kit", {
        "kit_id": CLIENT_ID,
        "name": CLIENT_ID
    })

def wait_for_databroker_ready(max_attempts=10, sleep_time=0.5):
    for attempt in range(max_attempts):
        try:
            with KClient(BORKER_IP, BROKER_PORT) as temp_client:
                # Test connection by fetching server info or metadata
                temp_client.get_server_info()
            print("Databroker is ready.")
            return True
        except VSSClientError as e:
            if "Connection refused" in str(e):
                print(f"Databroker not ready yet (attempt {attempt + 1}/{max_attempts}). Retrying...")
                time.sleep(sleep_time)
            else:
                raise
    raise Exception("Databroker failed to become ready after retries.")

@sio.event
async def messageToKit(data):
    print(f"SYNCER: Command '{data.get('cmd', 'UNKNOWN')}' received", flush=True)
    if data["cmd"] in ("deploy_request", "deploy-request"):
        print("Receive deploy_request...")
        request_from = data["request_from"]
        
        # your code to run app
        await send_app_deploy_reply(request_from, "Receive deploy request \r\n", False, data["cmd"])
        await asyncio.sleep(1)
        writeCodeToFile(data["code"], filename="main.py")
        await send_app_deploy_reply(request_from, "Check syntax.... \r\n", False, data["cmd"])
        # your_code_to_check_velocitas_code(data["code"])
        await asyncio.sleep(3)
        await send_app_deploy_reply(request_from, "Build docker image \r\n", False, data["cmd"])
        # your_code_to_build_docker(data["code"])
        await asyncio.sleep(3)
        await send_app_deploy_reply(request_from, "Send to HW kit \r\n", False, data["cmd"])
        # your_code...()
        await asyncio.sleep(3)
        await send_app_deploy_reply(request_from, "Run docker on HW kit \r\n", False, data["cmd"])
        # your_code...()
        await asyncio.sleep(3)
        await send_app_deploy_reply(request_from, "Deploy done! \r\n", True, data["cmd"])
        return 0
    
    if data["cmd"] == "subscribe_apis":
        if data["apis"] is not None:
            apis = data["apis"]
            master_id=data["request_from"]
            lsOfApiSubscriber[master_id] = {
                "from": time.time(),
                "apis": apis
            }

            if isinstance(apis,list) and len(apis)>0:
                appendMockSignal(apis)
            
            await sio.emit("messageToKit-kitReply", {
                "kit_id": CLIENT_ID,
                "request_from": data["request_from"],
                "cmd": "subscribe_apis",
                "result": "Successful"
            })
        return 0
    
    if data["cmd"] == "unsubscribe_apis":
        master_id=data["request_from"]
        del lsOfApiSubscriber[master_id]
        await sio.emit("messageToKit-kitReply", {
            "kit_id": CLIENT_ID,
            "request_from": data["request_from"],
            "cmd": "unsubscribe_apis",
            "result": "Successful"
        })
        return 0
    
    if data["cmd"] == "list_mock_signal":
        mock_signal = listMockSignal()
        await sio.emit("messageToKit-kitReply", {
            "kit_id": CLIENT_ID,
            "request_from": data["request_from"],
            "cmd": "list_mock_signal",
            "data": mock_signal,
            "result": "Successful"
        })
        return 0
    
    if data["cmd"] == "set_mock_signals":
        modifyMockSignal(data["data"])
        mock_signal = listMockSignal()
        # print("After modifying:")
        # print(mock_signal)
        restartMockProvider()
        await sio.emit("messageToKit-kitReply", {
            "kit_id": CLIENT_ID,
            "request_from": data["request_from"],
            "cmd": "set_mock_signals",
            "data": mock_signal,
            "result": "Successful"
        })
        return 0
    
    if data["cmd"] == "write_signals_value":
        writeSignalsValue(data["data"])
        # mock_signal = listMockSignal()
        mock_signal = {}
        await sio.emit("messageToKit-kitReply", {
            "kit_id": CLIENT_ID,
            "request_from": data["request_from"],
            "cmd": "write_signals_value",
            "data": mock_signal,
            "result": "Successful"
        })
        return 0
    
    if data["cmd"] == "reset_signals_value":
        with open(mock_signal_path) as f:
            signal_list = json.load(f)
        writeSignalsValue(str(signal_list))
        mock_signal = listMockSignal()
        await sio.emit("messageToKit-kitReply", {
            "kit_id": CLIENT_ID,
            "request_from": data["request_from"],
            "cmd": "reset_signals_value",
            "data": mock_signal,
            "result": "Successful"
        })
        return 0
    
    if data["cmd"] == "generate_vehicle_model":
        if not VEHICLE_MODEL_AVAILABLE:
            await sio.emit("messageToKit-kitReply", {
                "kit_id": CLIENT_ID,
                "request_from": data["request_from"],
                "cmd": "generate_vehicle_model",
                "result": "Error: Vehicle model manager not available"
            })
            return 0
            
        print("receive reauest generate_vehicle_model")
        # print(data["data"])
        # print type of data["data"]
        # print(type(data["data"]))

        try:
            await sio.emit("messageToKit-kitReply", {
                "kit_id": CLIENT_ID,
                "request_from": data["request_from"],
                "cmd": "revert_vehicle_model",
                "result": "Start to rebuild vehicle model...\r\n"
            })
            stopMockService()
            generate_vehicle_model(json.dumps(data["data"]))
            
            time.sleep(0.5)
            # Check is databroker app running or not
            if is_process_running_nix("databroker"):
                print("databroker is running")
            else:
                print("databroker is not running")
                raise Exception("Databroker is not running")
            
            # Wait until databroker is fully ready (port is listening)
            wait_for_databroker_ready()
            
            modifyMockSignal([""])
            time.sleep(0.5)
            startMockService()
            await sio.emit("messageToKit-kitReply", {
                "kit_id": CLIENT_ID,
                "request_from": data["request_from"],
                "cmd": "generate_vehicle_model",
                "result": "Generate new model Successful"
            })
            return 0
        except Exception as e:
            # print("generate_vehicle_model Error: ", str(e))
            
            await sio.emit("messageToKit-kitReply", {
                "kit_id": CLIENT_ID,
                "request_from": data["request_from"],
                "cmd": "generate_vehicle_model",
                "result": "Error: generate_vehicle_model Failed: " + str(e) + "\r\nRevert back to default model" 
            })
            if VEHICLE_MODEL_AVAILABLE:
                revert_vehicle_model()
            return 0

    if data["cmd"] == "revert_vehicle_model":
        if not VEHICLE_MODEL_AVAILABLE:
            await sio.emit("messageToKit-kitReply", {
                "kit_id": CLIENT_ID,
                "request_from": data["request_from"],
                "cmd": "revert_vehicle_model",
                "result": "Error: Vehicle model manager not available"
            })
            return 0
            
        await sio.emit("messageToKit-kitReply", {
            "kit_id": CLIENT_ID,
            "request_from": data["request_from"],
            "cmd": "revert_vehicle_model",
            "result": "Start to revert to default vehicle model...\r\n"
        })
        stopMockService()
        revert_vehicle_model()
        time.sleep(0.5)
        startMockService()
        await sio.emit("messageToKit-kitReply", {
            "kit_id": CLIENT_ID,
            "request_from": data["request_from"],
            "cmd": "revert_vehicle_model",
            "result": "Revert to default Vehicle Model Successful\r\n"
        })
        return 0  
    
    if data["cmd"] == "list_python_packages":
        if not PKG_MANAGER_AVAILABLE:
            await sio.emit("messageToKit-kitReply", {
                "kit_id": CLIENT_ID,
                "request_from": data["request_from"],
                "cmd": "list_python_packages",
                "data": {"error": "Package manager not available"},
                "result": "Error: Package manager not available"
            })
            return 0
            
        pkgs = pkg_manager.listPkg()
        # print(pkgs,flush=True)
        await sio.emit("messageToKit-kitReply", {
            "kit_id": CLIENT_ID,
            "request_from": data["request_from"],
            "cmd": "list_python_packages",
            "data": pkgs,
            "result": "Successful"
        })
        return 0
        
    if data["cmd"] == "install_python_packages":
        if not PKG_MANAGER_AVAILABLE:
            await sio.emit("messageToKit-kitReply", {
                "kit_id": CLIENT_ID,
                "request_from": data["request_from"],
                "cmd": "install_python_packages",
                "result": "Error: Package manager not available",
                "data": "Package manager not available"
            })
            return 0
            
        msg = data["data"]
        await sio.emit("messageToKit-kitReply", {
            "kit_id": CLIENT_ID,
            "request_from": data["request_from"],
            "cmd": "install_python_packages",
            "result": "Installing",
            "data": f"Installing packages: {msg}\n"
        })
        # print(msg,flush=True)
        response = await pkg_manager.installPkg(data["data"])
        # await asyncio.sleep(1)
        await sio.emit("messageToKit-kitReply", {
            "kit_id": CLIENT_ID,
            "request_from": data["request_from"],
            "cmd": "install_python_packages",
            "result": "Successful",
            "data": str(response)
        }) 

        return 0  

    # Handle C++ application commands (multiple possible command names)
    if data["cmd"] in ("run_cpp_app", "compile_cpp_app", "build_cpp_app") and CPP_MEMORY_AVAILABLE:
        print(f"Processing C++ command '{data['cmd']}' with CPP_MEMORY_AVAILABLE={CPP_MEMORY_AVAILABLE}", flush=True)
        from_id = data["request_from"]
        
        # Check if data.code exists and is valid JSON (C++ projects)
        if "data" in data and "code" in data["data"]:
            try:
                # Validate JSON format
                code_data = data["data"]["code"]
                json.loads(code_data)  # This will raise an error if invalid JSON


                # Initialize ProjectUtils
                project_utils = ProjectUtils()

                # Clean up app directory
                print("Cleaning up app directory...", flush=True)
                cleanup_success = project_utils.empty_app_directory()
                if cleanup_success:
                    print("App directory cleaned successfully", flush=True)
                    await send_reply(from_id, "App directory cleaned successfully\r\n", is_done=False, retcode=0)
                else:
                    print("Failed to clean app directory", flush=True)
                    await send_reply(from_id, "Failed to clean app directory\r\n", is_error=True, retcode=1)
                    return 0

                # Create content in app based on payload data.code
                await send_reply(from_id, "Creating C++ project content...\r\n", is_done=False, retcode=0)
                try:
                    app_path = project_utils.save_from_payload(data)
                    print("C++ project content created successfully", flush=True)
                except Exception as e:
                    print(f"Failed to create C++ project content: {str(e)}", flush=True)
                    await send_reply(from_id, f"Failed to create C++ project content: {str(e)}", is_error=True, retcode=1)
                    return 0
                await send_reply(from_id, "C++ project content created successfully\r\n", is_done=False, retcode=0)

                # Compile C++ project
                compile_ok, compile_msg = await cpp_debugger_util.compile_cpp()
                print(f"Compiling C++ project...\r\n{compile_msg}", flush=True)
                await send_reply(from_id, f"Compiling C++ project...\r\n{compile_msg}\r\n", is_done=False, retcode=0)
                if not compile_ok:
                    await send_reply(from_id, "C++ compilation failed", is_error=True, is_done=True, retcode=1)
                    return 0
                
                print("Starting C++ memory monitoring approach")
                await send_reply(from_id, "Starting high-performance memory monitoring...\r\n", is_done=False, retcode=0)
                
                # Start memory monitoring (replaces traditional run_binary)
                binary_path, pid, run_msg = await cpp_debugger_util.run_binary()
                await send_reply(from_id, f"Binary ready: {run_msg}\r\n", is_done=False, retcode=0)
                
                if binary_path is not None:
                    # Track memory monitoring for this client
                    if from_id not in cpp_processes:
                        cpp_processes[from_id] = []
                    
                    cpp_processes[from_id].append({
                        "binary_path": binary_path,
                        "type": "cpp_memory",
                        "monitor_active": True,
                        "start_time": time.time()
                    })
                    
                    print(f"Prepared C++ memory monitoring for binary {binary_path} for client {from_id}", flush=True)
                    
                    # Get watch_vars from data if present
                    watch_vars = data["data"].get("watch_vars", "")
                    
                    # NO HARDCODED FALLBACK - Use automatic detection in cpp_memory_debugger
                    if not watch_vars or not watch_vars.strip():
                        watch_vars = ""  # Empty string triggers automatic detection
                        print(f"No watch variables specified, automatic detection will be used", flush=True)
                    else:
                        print(f"Watch vars from frontend: {watch_vars}", flush=True)
                    
                    # Start monitoring regardless of watch_vars (empty triggers auto-detection)
                    if watch_vars is not None:
                        if watch_vars.strip():
                            print(f"Starting C++ memory monitoring task for variables: {watch_vars}")
                            await send_reply(from_id, f"Monitoring variables: {watch_vars}\r\n", is_done=False, retcode=0, cmd=data["cmd"])
                        else:
                            print("Starting C++ memory monitoring with automatic variable detection")
                            await send_reply(from_id, "Starting automatic variable detection and monitoring...\r\n", is_done=False, retcode=0, cmd=data["cmd"])
                        
                        # Create completion callback to remove from running list
                        def cpp_completion_callback(kit_id):
                            """Remove C++ app from running list when monitoring completes"""
                            for runner in list(lsOfRunner):  # Use list() to avoid modification during iteration
                                if runner.get("request_from") == kit_id and runner.get("type") == "cpp_app":
                                    lsOfRunner.remove(runner)
                                    print(f"✅ Removed C++ app from running list for kit {kit_id}")
                                    break
                        
                        # Create a wrapper to pass send_reply function for stdout forwarding
                        async def send_stdout_reply(content, is_error=False):
                            """Forward stdout/stderr to Kit server"""
                            # Ensure content has \r\n ending for proper formatting
                            if not content.endswith('\r\n'):
                                content = content + '\r\n'
                            await send_reply(from_id, content, is_error=is_error, is_done=False, retcode=0, cmd=data["cmd"])
                            # Small delay to prevent message flooding
                            await asyncio.sleep(0.001)
                        
                        
                        # Start the enhanced memory monitoring task with stdout forwarding and completion callback
                        task = asyncio.create_task(cpp_debugger_util.periodic_memory_var_report(
                            sio, from_id, watch_vars, send_reply_func=send_stdout_reply, completion_callback=cpp_completion_callback))
                        monitoring_tasks[from_id] = task
                        
                        # Add C++ process to lsOfRunner to show "stop" button in kit server
                        app_name = data["data"].get("name", "C++ Application")
                        lsOfRunner.append({
                            "appName": f"{app_name} (C++)",
                            "runner": task,  # Use the monitoring task as the runner
                            "request_from": from_id,
                            "from": time.time(),
                            "type": "cpp_app"  # Mark as C++ app for identification
                        })
                        
                        print(f"C++ memory monitoring started for client {from_id}")
                        print(f"Added C++ app '{app_name}' to running processes list")
                        
                        # Don't send completion immediately - let the monitoring task handle completion
                        print(f"C++ memory monitoring task started for {from_id} via command {data['cmd']}")
                        return 0
                    else:
                        print("No watch variables specified - running without monitoring")
                        await send_reply(from_id, "No variables to monitor specified\r\n", is_done=True, retcode=0, cmd=data["cmd"])
                        return 0
                else:
                    print("✗ Failed to prepare binary for C++ monitoring", flush=True)
                    await send_reply(from_id, "Failed to prepare binary for monitoring", is_error=True, is_done=True, retcode=1, cmd=data["cmd"])
                    return 0

            except json.JSONDecodeError as e:
                print(f"Invalid JSON in C++ code data: {str(e)}", flush=True)
                await send_reply(from_id, f"Invalid JSON format in C++ project: {str(e)}", is_error=True, retcode=1, cmd=data["cmd"])
                return 0
            except Exception as e:
                print(f"Error processing C++ project data: {str(e)}", flush=True)
                await send_reply(from_id, f"Error processing C++ project data: {str(e)}", is_error=True, retcode=1, cmd=data["cmd"])
                return 0
        else:
            await send_reply(from_id, "Missing code data for C++ project", is_error=True, retcode=1, cmd=data["cmd"])
            return 0
    
    elif data["cmd"] in ("run_cpp_app", "compile_cpp_app", "build_cpp_app"):
        print(f"C++ command '{data['cmd']}' received but CPP_MEMORY_AVAILABLE={CPP_MEMORY_AVAILABLE}", flush=True)
        # C++ not available
        await sio.emit("messageToKit-kitReply", {
            "kit_id": CLIENT_ID,
            "request_from": data["request_from"],
            "cmd": data["cmd"],
            "result": "Error: C++ memory monitoring not available",
            "data": ""
        })
        return 0
            
    if data["cmd"] == "run_python_app":
        # Original Python app execution - unchanged behavior
        # check do we have data["data"]["code"]
        if "code" not in data["data"]:
            await sio.emit("messageToKit-kitReply", {
                "kit_id": CLIENT_ID,
                "request_from": data["request_from"],
                "cmd": "run_python_app",
                "result": "Error: Missing code",
                "data": ""
            })
            return 1
        appName = "App name"
        if "name" in data["data"]:
            appName = data["data"]["name"]
        
        writeCodeToFile(data["data"]["code"], filename="main.py")
        try:
            usedAPIs = data["usedAPIs"]
            if isinstance(usedAPIs,list) and len(usedAPIs)>0:
                appendMockSignal(usedAPIs)
        except Exception as e:
            print("Fail to appendMockSignal for usedAPIs")
            print(str(e))

        proc = subpiper(
            master_id=data["request_from"],
            cmd='python -u main.py',
            stdout_callback=my_stdout_callback,
            stderr_callback=my_stderr_callback,
            finished_callback=process_done
        )
        lsOfRunner.append({
            "appName": appName,
            "runner": proc,
            "request_from": data["request_from"],
            "from": time.time()
        })
        return 0
    
    if data["cmd"] == "run_bin_app":
        if "data" not in data:
            await sio.emit("messageToKit-kitReply", {
                "kit_id": CLIENT_ID,
                "request_from": data["request_from"],
                "cmd": "run_bin_app",
                "result": "Error: Missing app name",
                "data": ""
            }) 
            return 1
        app_name = data["data"]
        if os.path.isfile(f'/home/dev/output/{app_name}'):
            try:
                usedAPIs = data["usedAPIs"]
                if isinstance(usedAPIs,list) and len(usedAPIs)>0:
                    appendMockSignal(usedAPIs)
            except Exception as e:
                print("Fail to appendMockSignal for usedAPIs")
                print(str(e))
                
            await asyncio.sleep(0.5)
            proc = subpiper(
                master_id=data["request_from"],
                cmd=f'/home/dev/output/{app_name}',
                stdout_callback=my_stdout_callback,
                stderr_callback=my_stderr_callback,
                finished_callback=process_done
            )
            lsOfRunner.append({
                "appName": app_name,
                "runner": proc,
                "request_from": data["request_from"],
                "from": time.time()
            })
        else:
            await sio.emit("messageToKit-kitReply", {
                "kit_id": CLIENT_ID,
                "request_from": data["request_from"],
                "cmd": "run_bin_app",
                "result": "Failed: Rust app not found",
                "data": ""
            }) 
        return 0
    
    elif data["cmd"] in ("stop_python_app", "stop_cpp_app"):
        from_id = data["request_from"]
        
        # Stop C++ processes if any
        cpp_stopped = False
        if CPP_MEMORY_AVAILABLE and from_id in cpp_processes:
            cpp_stopped = await stop_client_processes(from_id)
            if cpp_stopped:
                await send_reply(from_id, "C++ processes stopped successfully\r\n", is_done=True, retcode=0)
        
        # Stop Python processes and C++ tasks
        python_stopped = False
        for runner in list(lsOfRunner):  # Use list() to avoid modification during iteration
            if runner["request_from"] == from_id:
                proc = runner["runner"]
                runner_type = runner.get("type", "python")
                
                if proc is not None:
                    try:
                        if runner_type == "cpp_app":
                            # For C++ apps, cancel the async task
                            print(f"Cancelling C++ monitoring task for {from_id}")
                            if hasattr(proc, 'cancel'):
                                proc.cancel()  # Cancel the asyncio Task
                            await send_reply(from_id, "C++ application stopped\r\n", is_done=True, retcode=0)
                        else:
                            # For Python apps, kill the process
                            if hasattr(proc, 'kill'):
                                proc.kill()
                            else:
                                print(f"Process {proc} doesn't have kill method")
                        
                        lsOfRunner.remove(runner)
                        python_stopped = True
                        print(f"✅ Stopped {runner_type} app for client {from_id}")
                        
                    except Exception as e:
                        print(f"Error stopping {runner_type} app: {str(e)}")
                        await sio.emit("messageToKit-kitReply", {
                            "kit_id": CLIENT_ID,
                            "request_from": data["request_from"],
                            "cmd": data["cmd"],
                            "result": str(e)
                        })
        
        if not cpp_stopped and not python_stopped:
            await send_reply(from_id, "No processes found to stop\r\n", is_done=True, retcode=0)
        
        return 0
    
    elif data["cmd"] == "trace_vars" and CPP_MEMORY_AVAILABLE:
        print(f"🔥 SYNCER: trace_vars command received")
        request_from = data["request_from"]
        
        try:
            # Start C++ memory monitoring with trace_vars
            await cpp_debugger_util.start_cpp_trace_vars_monitoring(
                data, request_from, sio
            )
            
            await sio.emit("messageToKit-kitReply", {
                "kit_id": CLIENT_ID,
                "request_from": request_from,
                "cmd": "trace_vars",
                "result": "trace_vars monitoring started successfully",
                "isDone": False,
                "code": 0
            })
            
        except Exception as e:
            print(f"🔥 trace_vars error: {e}")
            import traceback
            traceback.print_exc()
            
            await sio.emit("messageToKit-kitReply", {
                "kit_id": CLIENT_ID,
                "request_from": request_from,
                "cmd": "trace_vars",
                "result": f"trace_vars failed: {str(e)}",
                "isDone": True,
                "code": 1
            })
        
        return 0
    
    elif data["cmd"] == "trace_vars":
        # trace_vars requested but CPP memory monitoring not available
        await sio.emit("messageToKit-kitReply", {
            "kit_id": CLIENT_ID,
            "request_from": data["request_from"],
            "cmd": "trace_vars",
            "result": "Error: C++ memory monitoring not available",
            "isDone": True,
            "code": 1
        })
        return 0
    
    elif data["cmd"] == "get-runtime-info":
        await sio.emit("messageToKit-kitReply", {
            "kit_id": CLIENT_ID,
            "request_from": data["request_from"],
            "cmd": "get-runtime-info",
            "data": {
                "lsOfRunner": convertLsOfRunnerToJson(lsOfRunner),
                "lsOfApiSubscriber": lsOfApiSubscriber
            }
            
        })
        return 0
    
    print(f"WARNING: Unhandled command '{data.get('cmd', 'UNKNOWN')}' - syncer did nothing!", flush=True)
    return 1

def convertLsOfRunnerToJson(lsOfRunner):
    result = []
    for runner in lsOfRunner:
        result.append({
            "appName": runner["appName"],
            "request_from": runner["request_from"],
            "from": runner["from"]
        })
    return result

def writeCodeToFile(code, filename="main.py"):
    f = open(filename, "w+")
    f.write(code)
    f.close()

def listMockSignal():
    if os.path.exists(mock_signal_path):
        with open(mock_signal_path,'r') as file:
            mock_signal_array = json.load(file)
            return mock_signal_array
    else:
        print("No signals found.",flush=True)

def stopMockService():
    pid_file = "/home/dev/mockprovider.pid"
    if os.path.exists(pid_file):
        with open(pid_file, "r") as f:
            pid = int(f.read().strip())

        try:
            os.kill(pid, signal.SIGKILL)
            print(f"mockprovider with PID {pid} has been killed.", flush=True)
        except ProcessLookupError:
            print(f"No process found with PID {pid}.", flush=True)
            pass
    else:
        print(f"mockprovider pid file at '{pid_file}' does not exist.", flush=True)

def startMockService():
    try:
        print("Starting mock provider...", flush=True)
        subprocess.Popen(["python", "/home/dev/ws/mock/mockprovider.py"])
        print("mock provider started.", flush=True)
    except Exception as e:
        print(f"Error starting mock provider: {e}", flush=True)
        return 1

def restartMockProvider():
    stopMockService()
    time.sleep(0.5)
    startMockService()

def appendMockSignal(signals):
    if signals is None or len(signals) <=0:
        return 0
    
    # Skip KUKSA operations if not available
    try:
        hasNew = False
        with KClient(BORKER_IP, BROKER_PORT) as kclient:
            with open(mock_signal_path,'r+') as f:
                content = f.read()
                # print(f"mock file content")
                if len(content) == 0 :
                    content = "[]"
                # print(content)
                cur_mocks = json.loads(content)
                cur_mock_names = []
                for cur_mock in cur_mocks:
                    cur_mock_names.append(cur_mock["signal"])
                # print("cur_mock_names", cur_mock_names)
                for run_signal in signals:
                    if run_signal not in cur_mock_names:
                        try: 
                            if kclient.get_metadata([run_signal, ]) is not None:
                                hasNew = True
                                print(f">>> Append new mock signal {run_signal}")
                                cur_mock_names.append(run_signal)
                                cur_mocks.append({
                                    "signal":  run_signal,
                                    "value": "0"
                                })
                        except Exception as e:
                            print(e,flush=True)
                        
                if hasNew:
                    f.seek(0)
                    json.dump(cur_mocks,f,indent=4)
                    f.truncate()

        if hasNew:
            restartMockProvider()
            
    except Exception as e:
        print(f"KUKSA mock signal operation failed: {e}")
        # Continue without KUKSA functionality
        
    return 0

def modifyMockSignal(input_str):
    with open(mock_signal_path,'w') as file:
        json_string = json.dumps(input_str)
        input_signals = json.loads(json_string)
        final_signals = []
        with KClient(BORKER_IP, BROKER_PORT) as kclient:
            for signal in input_signals:
                try: 
                    if kclient.get_metadata([signal['signal'], ]) is not None:
                        final_signals.append(signal)
                except Exception as e:
                    print(e,flush=True)
        
        file.seek(0)
        json.dump(final_signals,file,indent=4)
        file.truncate()
        return 0

def writeSignalsValue(input_str):
    json_str = json.dumps(input_str)
    signal_values = json.loads(json_str)
    with KClient(BORKER_IP, BROKER_PORT) as kclient:
        for path,value in signal_values.items():
            try:
                meta_data = kclient.get_metadata([path], MetadataField.ENTRY_TYPE)
                entry_type = meta_data[path].entry_type
                if entry_type == EntryType.ACTUATOR:
                    try:
                        target_value = {path: Datapoint(value)}
                        kclient.set_target_values(target_value)
                        # print(target_value,flush=True)
                    except Exception as e:
                        print("Error occured when writing target values: " + str(e),flush=True)
                elif entry_type == EntryType.SENSOR:
                    try:
                        current_value = {path: Datapoint(value)}
                        kclient.set_current_values(current_value)
                        # print(current_value, flush=True)
                    except Exception as e:
                        print("Error occured when writing current values: " + str(e), flush=True)
                else:
                    print("The signal path provided was not actuator or sensor", flush=True)
            except Exception as e:
                print("Error occured when writing signal values: " + str(e),flush=True)

async def start_socketio(SERVER):
    print("Connecting to Kit Server: " + SERVER, flush=True)
    await sio.connect(SERVER)
    await sio.wait()


'''
    Faster ticker: 0.3 seconds sleep
        - Report API value back to client
'''
async def ticker_fast():
    while True:
        await asyncio.sleep(0.3)
        # count number of child in lsOfApiSubscriber

        if len(lsOfApiSubscriber) <= 0:
            continue
        if not client.connected:
            try:
                await client.connect()
                print("Kuksa connected", client.connected)
            except Exception as e:
                # Kuksa not available, skip this iteration
                continue

        try:
            for client_id in lsOfApiSubscriber:
                apis = lsOfApiSubscriber[client_id]["apis"]
                if len(apis) > 0:
                    # print(f"read apis {apis}")
                    # start_time = time.time()
                    current_values_dict = {}
                    for api in apis:
                        try:
                            current_values = await client.get_current_values([api])
                            current_values_dict.update(current_values)
                        except Exception as e:
                            # print("get_current_values Error: ", str(e))
                            pass
                    result = {}
                    for api in current_values_dict:
                        if current_values_dict[api] is not None:
                            value = current_values_dict[api].value
                            # Convert array types to list for JSON serialization
                            if hasattr(value, 'values') and hasattr(value.values, '__iter__'):
                                result[api] = list(value.values)
                            elif hasattr(value, 'tolist'):
                                result[api] = value.tolist()
                            else:
                                result[api] = value
                        else:
                            result[api] = None
                    # elapsed_time = time.time() - start_time
                    # print(f"Execution time of one subscriber read: {elapsed_time:.6f} seconds")
                    await sio.emit("messageToKit-kitReply", {
                        "kit_id": CLIENT_ID,
                        "request_from": client_id,
                        "cmd":"apis-value",
                        "result": result
                    })
        except VSSClientError as vssErr:
            print("Error Code:" , str(vssErr),flush=True)
        except Exception as e:
            # pass
            print("Error:" , str(e),flush=True)

'''
    One second ticker
        - Handle old subscriber remove
        - Stop long runner
'''
async def ticker():
    # Don't require Kuksa to be connected
    print("Ticker started, Kuksa connected:", client.connected if hasattr(client, 'connected') else False)
    while True:
        await asyncio.sleep(1)

        # remove old subscriber
        if len(list(lsOfApiSubscriber.keys())) > 0:
            for client_id in list(lsOfApiSubscriber.keys()):
                subscriber = lsOfApiSubscriber[client_id]
                timePass = time.time() - subscriber["from"]
                if timePass > TIME_TO_KEEP_SUBSCRIBER_ALIVE:
                    del lsOfApiSubscriber[client_id]


        # remove old subscriber
        if len(lsOfRunner) > 0:
            for runner in lsOfRunner:
                timePass = time.time() - runner["from"]
                if timePass > TIME_TO_KEEP_RUNNER_ALIVE:
                    try:
                        runner["runner"].kill()
                        lsOfRunner.remove(runner)
                    except Exception as e:
                        print(str(e))

'''
    5 second ticker: 5 seconds sleep
        - Report API value back to client
'''
async def ticker_5s():
    lastLstRunString = ""
    lastNoApiSubscriber = 0
    while True:
        await asyncio.sleep(1)
        noSubscriber = len(list(lsOfApiSubscriber.keys()))
        if noSubscriber <= 0:
            continue
        try:
            lstRunString = json.dumps(convertLsOfRunnerToJson(lsOfRunner))
            if lastLstRunString != lstRunString or lastNoApiSubscriber != noSubscriber:
                lastLstRunString = lstRunString
                lastNoApiSubscriber = noSubscriber

                await sio.emit("report-runtime-state", {
                    "kit_id": CLIENT_ID,
                    "data": {
                        "noOfRunner": len(lsOfRunner),
                        "noOfApiSubscriber": noSubscriber,
                    }
                })

                for client_sid in lsOfApiSubscriber:
                    # Convert lsOfApiSubscriber to JSON-safe format
                    safe_api_subscriber = {}
                    for key, val in lsOfApiSubscriber.items():
                        safe_api_subscriber[key] = {
                            "apis": val.get("apis", []),
                            "keep_alive": val.get("keep_alive", 0)
                        }
                    await sio.emit("messageToKit-kitReply", {
                            "kit_id": CLIENT_ID,
                            "request_from": client_sid,
                            "cmd":"report-runtime-state",
                            "data": {
                                "lsOfRunner": convertLsOfRunnerToJson(lsOfRunner),
                                "lsOfApiSubscriber": safe_api_subscriber
                            }
                        })
        except Exception as e:
            print("Error: ", str(e))

async def main():
    global main_loop
    main_loop = asyncio.get_running_loop()
    SERVER = os.getenv('SYNCER_SERVER_URL', DEFAULT_KIT_SERVER) + ""
    global CLIENT_ID
    runtime_prefix = os.getenv('RUNTIME_PREFIX', DEFAULT_RUNTIME_PREFIX)
    runtime_name = os.getenv('RUNTIME_NAME', DEFAULT_RUNTIME_NAME)
    CLIENT_ID = runtime_prefix + runtime_name
    print("RunTime display name: " + CLIENT_ID, flush=True)

    # Try to connect to Kuksa but don't fail if it's not available
    try:
        await client.connect()
        print("Connected to Kuksa databroker", flush=True)
    except Exception as e:
        print(f"Warning: Could not connect to Kuksa databroker: {e}", flush=True)
        print("Continuing without Kuksa connection - some features may be limited", flush=True)
    
    await asyncio.gather(start_socketio(SERVER), ticker(), ticker_fast(), ticker_5s())

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()
