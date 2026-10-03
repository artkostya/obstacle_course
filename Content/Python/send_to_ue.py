# TODO: remote connection to UE does not work on macOS, will figurate out problem.
import os
import sys
import time

UE_PYTHON_API_PATH = (
    r"/Users/Shared/Epic Games/UE_5.4/Engine/Plugins/Experimental/"
    r"PythonScriptPlugin/Content/Python"
)
sys.path.append(UE_PYTHON_API_PATH)

import remote_execution


def run_script_in_ue(script_path):
    if not os.path.exists(script_path):
        print(f"Error: file {script_path} is not found.")
        return

    with open(script_path, "r", encoding="utf-8") as f:
        code_to_run = f.read()

    # HACK
    remote_execution.DEFAULT_MULTICAST_GROUP_ENDPOINT = ('239.0.0.1', 9999)
    remote_execution.DEFAULT_COMMAND_ENDPOINT = ('127.0.0.1', 9998)

    # Initialize remote control
    remote_exec = remote_execution.RemoteExecution()
    remote_exec.start()

    # CRITICAL FOR  MACOS: take socket 1.5 seconds to collect answers from network
    print("Search running Unreal Engine in network...")
    time.sleep(1.5)

    if remote_exec.remote_nodes:
        target_node = remote_exec.remote_nodes[0]
        print(f"Nodes to connection did found success: {target_node.get('node_name', 'Unknown')}")
    else:
        print("Network blocked autosearch. Try to make direct connection...")

        # Default configuration for Unreal Engine Remote Execution
        target_node = {
            'node_id': '00000000-0000-0000-0000-000000000000',
            'node_name': 'Mac_Local_Fallback',
            'command_port': 9998, # Standard port for commands in UE 5.4.4
            'unattended': False
        }

    try:
        # Open connection
        opened = remote_exec.open_command_connection(target_node)
        if not opened:
            raise ConnectionError("Opening of command port is failed. Check Project Settings в UE!")

        # Run code
        result = remote_exec.run_command(code_to_run, exec_mode="ExecuteStatement")

        # Print logs from output of Unreal Engine to PyCharm console
        if result and result.get("output"):
            for log in result["output"]:
                print(f"[UE Log]: {log.get('output')}")
        else:
            print("[Success]: Code was sent, but UE did not return logs.")

    except Exception as e:
        print(f"Running of commands is failed in UE: {e}")
        print("\nMake sure you have project open in Unreal Editor and option is enabled:")
        print("Project Settings -> Plugins -> Python -> Enable Remote Execution")
    finally:
        remote_exec.stop()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        full_script_path = " ".join(sys.argv[1:])
        full_script_path = full_script_path.strip('"\'')

        run_script_in_ue(full_script_path)
    else:
        print("Pass path to file for running in Unreal Engine.")
