import subprocess
import sys

try:
    print("Checking Node...")
    res1 = subprocess.run('where node', shell=True, capture_output=True, text=True)
    print(res1.stdout, res1.stderr)
    
    print("Checking npm...")
    res2 = subprocess.run('where npm', shell=True, capture_output=True, text=True)
    print(res2.stdout, res2.stderr)
    
    print("Checking npx...")
    res3 = subprocess.run('where npx', shell=True, capture_output=True, text=True)
    print(res3.stdout, res3.stderr)
except Exception as e:
    print(f"Error: {e}")
