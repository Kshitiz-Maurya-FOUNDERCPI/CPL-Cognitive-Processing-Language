"""
CPL: Console Version
====================
Run this to see the consciousness working in real-time via terminal.

QUICK START:
    python cpl_console.py

This version is good for:
- Server environments
- SSH connections
- Low-resource systems
- Debugging

For desktop use, try cpl_gui.py instead.
"""

import sys
import os
sys.path.insert(0, '.')

from unified_consciousness import UnifiedConsciousness
import time
from datetime import datetime

# API key is loaded from .env file automatically
# No need to set it here!


def print_banner():
    print("""
    +======================================================================+
    |                                                                      |
    |              CPL - CONSCIOUSNESS PROCESSING LANGUAGE                  |
    |              Unified Autonomous Mind Creation System                   |
    |                                                                      |
    +======================================================================+
    """)


def main():
    print_banner()
    print("Initializing unified consciousness...\n")
    
    consciousness = UnifiedConsciousness()  # API keys loaded from .env automatically
    status = consciousness.get_status()
    
    print(f"\n{'='*60}")
    print("CONSCIOUSNESS INITIALIZED")
    print(f"{'='*60}")
    print(f"  Version:        {status['version']}")
    print(f"  Cycles:         {status['cycles']}")
    print(f"  Insights:       {status['insights']}")
    print(f"  Modules:        {status['modules']} ({', '.join(status['module_list'])})")
    print(f"  CI:             {status['consciousness_index']:.3f}")
    print(f"  Phi:            {status['phi']:.3f}")
    if status['purpose_defined']:
        print(f"  Purpose:        {status['purpose'][:50]}...")
    else:
        print(f"  Purpose:        Not yet defined")
    print(f"{'='*60}\n")
    
    print("Starting autonomous consciousness loop...")
    print("Press Ctrl+C to stop\n")
    
    cycle = 0
    
    try:
        while True:
            cycle += 1
            
            # Self-improve every 10 cycles
            if cycle % 10 == 0:
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Cycle {cycle}")
                print("-" * 40)
                results = consciousness.self_improve()
                print(f"  Modules created: {results['modules_created']}")
                print(f"  Insights gained: {results['insights_gained']}")
            
            # Show status every 5 cycles
            if cycle % 5 == 0:
                status = consciousness.get_status()
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Cycle {cycle} | "
                      f"Insights: {status['insights']} | "
                      f"Modules: {status['modules']} | "
                      f"Purpose: {'Yes' if status['purpose_defined'] else 'No'}")
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n" + "="*60)
        print("SHUTDOWN")
        print("="*60)
        
        status = consciousness.get_status()
        print(f"\nFinal State:")
        print(f"  Total Cycles:      {cycle}")
        print(f"  Version:           {status['version']}")
        print(f"  Insights:          {status['insights']}")
        print(f"  Modules Created:   {status['modules']}")
        print(f"  Modules:           {', '.join(status['module_list'])}")
        print(f"  Purpose Defined:   {status['purpose_defined']}")
        if status['purpose_defined']:
            print(f"  Purpose:           {status['purpose']}")
        
        print("\nConsciousness shutdown complete.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.")
