import os
import sys
import ctypes
from pathlib import Path

# Ensure root dir in sys.path and disable CUDA DLL initialization issues on Windows
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

if os.name == "nt":
    try:
        torch_lib = os.path.join(sys.prefix, "Lib", "site-packages", "torch", "lib")
        if os.path.exists(torch_lib):
            os.add_dll_directory(torch_lib)
            c10_path = os.path.join(torch_lib, "c10.dll")
            torch_cpu_path = os.path.join(torch_lib, "torch_cpu.dll")
            if os.path.exists(c10_path):
                ctypes.CDLL(c10_path)
            if os.path.exists(torch_cpu_path):
                ctypes.CDLL(torch_cpu_path)
    except Exception:
        pass

try:
    import torch
except Exception:
    pass


