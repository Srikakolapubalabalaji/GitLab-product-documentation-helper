import os
import sys
import ctypes

# Ensure torch DLL directory is registered on Windows to prevent WinError 1114
if os.name == "nt":
    os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")
    os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
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

# Package app


