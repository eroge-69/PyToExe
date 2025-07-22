import subprocess
import time
import logging
from concurrent.futures import ThreadPoolExecutor

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

def stress_test_echo_command_executer(i):
    subprocess.run(["cmd", "/c", f"echo Cynet360-test {i}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)

class EchoCommandTester:
    def expect_for_output_in_log(self, expected_output):
        # Stub for matching expected log output.
        # In real test, you'd check actual logs or mock log capturing
        logging.info(f"Simulated check for: {expected_output}")

    def test_ph_stress(self):
        MAX_COMMANDS = 100

        # Run echo commands in parallel
        with ThreadPoolExecutor(max_workers=5) as executor:
            executor.map(stress_test_echo_command_executer, range(1, MAX_COMMANDS))

        # Validate expected outputs
        for i in range(1, MAX_COMMANDS):
            expected_output = {
                'Rule Name (ETW Alert Id)': ['Process Monitoring - Cynet Test'],
                'CommandLine': [f'cmd /c "echo Cynet360-test {i}"']
            }

            logging.info("Searching for")
            logging.info(expected_output)
            self.expect_for_output_in_log(expected_output)

if __name__ == "__main__":
    tester = EchoCommandTester()
    tester.test_ph_stress()