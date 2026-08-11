import os
import sys

# Ensure torch DLL directory is registered on Windows to prevent WinError 1114
if os.name == "nt":
    os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")
    os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
    try:
        import site
        for site_path in site.getsitepackages():
            torch_lib = os.path.join(site_path, "torch", "lib")
            if os.path.exists(torch_lib):
                os.add_dll_directory(torch_lib)
    except Exception:
        pass

# Package root


