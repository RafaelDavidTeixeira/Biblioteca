import sys, os, tkinter as tk
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.license import generate_license_key, get_machine_id, LICENSE_SECRET

# Output debug info to files
with open(os.path.join(os.path.dirname(sys.executable), 'lic_debug.txt'), 'w') as f:
    f.write(f"SECRET={repr(LICENSE_SECRET)}\n")
    f.write(f"MACHINE_ID={get_machine_id()}\n")
    key = generate_license_key(get_machine_id(), 'Test', 365)
    f.write(f"KEY={key}\n")
    f.write(f"EXE_DIR={os.path.dirname(sys.executable)}\n")
    f.write(f"__file__={__file__}\n")

# Still show the GUI
root = tk.Tk()
root.title("Debug License")
tk.Label(root, text=f"Secret: {LICENSE_SECRET.decode()}").pack(pady=5)
tk.Label(root, text=f"Machine ID: {get_machine_id()}").pack(pady=5)
tk.Label(root, text=f"Key: {key}").pack(pady=5)
tk.Button(root, text="OK", command=root.destroy).pack(pady=10)
root.mainloop()
