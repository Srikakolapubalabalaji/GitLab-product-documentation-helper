import sys
from pathlib import Path

# Add project root directory to sys.path
import os
import ctypes

# Fix Windows PyTorch / OpenMP DLL initialization issue (WinError 1114)
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

if os.name == "nt":
    torch_lib = os.path.join(sys.prefix, "Lib", "site-packages", "torch", "lib")
    if os.path.exists(torch_lib):
        try:
            os.add_dll_directory(torch_lib)
            c10_path = os.path.join(torch_lib, "c10.dll")
            torch_cpu_path = os.path.join(torch_lib, "torch_cpu.dll")
            if os.path.exists(c10_path):
                ctypes.CDLL(c10_path)
            if os.path.exists(torch_cpu_path):
                ctypes.CDLL(torch_cpu_path)
        except Exception:
            pass

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))


import uvicorn

if __name__ == "__main__":
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=False)
