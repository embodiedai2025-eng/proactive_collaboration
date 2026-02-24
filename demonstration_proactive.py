import argparse
import os
import time
import traceback
from termcolor import colored

from main import run
from logger_manager import LoggerManager

# Fixed configuration: only run scene 0 dataset 0
SCENE_INDEX = 0
DATASET_ID = 0
LOG = True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Demonstration: Run scene 0 dataset 0')
    parser.add_argument('--remote_url', type=str, required=True, help='Environment API URL')
    parser.add_argument('--exp_name', type=str, default='demo', help='Experiment name (for output directory)')
    
    args = parser.parse_args()
    
    REMOTE_URL = args.remote_url
    port = REMOTE_URL.split(":")[-1].replace("/", "")
    exp_name = args.exp_name
    
    # Set paths
    SAVE_DIR = f"output/{exp_name}"
    LOG_DIR = f"logs/{exp_name}"
    DATASET_DIRECT = f"datasets/dataset_s{SCENE_INDEX}_72.json"
    
    print(colored("=== Demonstration Mode ===", "cyan"))
    print(colored(f"Scene: {SCENE_INDEX}, Dataset: {DATASET_ID}, Port: {port}, Experiment: {exp_name}", "cyan"))
    
    if LOG:
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)
        log_manager = LoggerManager(LOG_DIR)
        logger = log_manager.get_logger()
    
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)
    
    # Retry mechanism: check if result file exists, retry if not
    max_test_num = 5
    test_iter = 1
    result_file = f"{SAVE_DIR}/dataset_{DATASET_ID}.json"
    
    while test_iter <= max_test_num:
        # Check if result file already exists
        if os.path.exists(result_file):
            print(colored(f"✓ Dataset {DATASET_ID} result already exists, skipping...", "green"))
            break
        
        try:
            print(colored(f"Starting dataset {DATASET_ID} (Attempt {test_iter}/{max_test_num})...", "magenta"))
            if_success = run(
                dataset_id=DATASET_ID,
                dataset_direct=DATASET_DIRECT,
                save_dir=SAVE_DIR,
                remote_url=REMOTE_URL
            )
            
            # Check if result file has been generated
            if os.path.exists(result_file):
                if if_success:
                    print(colored(f"✓ Dataset {DATASET_ID} completed successfully!", "green"))
                else:
                    print(colored(f"✗ Dataset {DATASET_ID} failed but result file exists", "yellow"))
                break
            else:
                print(colored(f"⚠ Dataset {DATASET_ID} completed but result file not found, will retry...", "yellow"))
                
        except Exception as e:
            print(colored(f"Error running dataset {DATASET_ID} (Attempt {test_iter}/{max_test_num}): {e}", "red"))
            traceback.print_exc()
            print(colored(f"==== Error in dataset {DATASET_ID}, will retry ====", "yellow"))
        
        test_iter += 1
        
        # If there are more retry attempts, wait before retrying
        if test_iter <= max_test_num and not os.path.exists(result_file):
            wait_time = 2  # Wait 2 seconds before retry
            print(colored(f"Waiting {wait_time} seconds before retry...", "cyan"))
            time.sleep(wait_time)
    
    # Final check
    if not os.path.exists(result_file):
        print(colored(f"✗ Dataset {DATASET_ID} failed after {max_test_num} attempts", "red"))
    elif test_iter > 1:
        print(colored(f"✓ Dataset {DATASET_ID} succeeded after {test_iter - 1} attempt(s)", "green"))
    
    if LOG:
        log_manager.close()
    
    print(colored("=== Demonstration Complete ===", "cyan"))
