# EDUCATIONAL DEMONSTRATION ONLY - NOT FUNCTIONAL MALWARE
# This simulates virus behavior for academic purposes

class EducationalVirusSimulator:
    def __init__(self):
        self.signature = "EDU_VIRUS_SIMULATION_v1.0"
        self.infected_files = []
    
    def simulate_infection(self, target_path):
        """Simulate how a virus might attach to files"""
        print(f"[SIMULATION] Would attempt to infect: {target_path}")
        
        # Simulation of code injection
        simulated_payload = f"\n# {self.signature} - Educational simulation only\n"
        simulated_payload += "# This would be malicious code in a real virus\n"
        
        print(f"[SIMULATION] Would add {len(simulated_payload)} bytes to file")
        self.infected_files.append(target_path)
        return True
    
    def simulate_replication(self):
        """Simulate how a virus might spread"""
        print("[SIMULATION] Virus would now attempt to spread...")
        # This would search for other files in a real virus
        potential_targets = [f"program_{i}.py" for i in range(3)]
        
        for target in potential_targets:
            self.simulate_infection(target)
    
    def display_info(self):
        """Show educational information"""
        print("\n" + "="*50)
        print("EDUCATIONAL VIRUS SIMULATION")
        print("="*50)
        print("This demonstrates how computer viruses work:")
        print("- Self-replication mechanism")
        print("- Code injection techniques")
        print("- Stealth and propagation methods")
        print("\nInfected files (simulated):", self.infected_files)
        print("\nNOTE: Creating actual malware is illegal and unethical")

# Demonstration
if __name__ == "__main__":
    simulator = EducationalVirusSimulator()
    simulator.simulate_infection("test_program.py")
    simulator.simulate_replication()
    simulator.display_info()
