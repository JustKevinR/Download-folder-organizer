# 📂 **Automatic File Organizer**

This script automatically organizes files in your **Downloads** folder into categorized subfolders based on their file types (e.g., Audio, Video, Images, Docs, Executables, Archives).

---

## 🚀 **Setup Guide**

### 1️⃣ **Update Directory Paths**

- Open the script and **replace `USERNAME`** with your actual PC username in the following paths:

```python
sourceDir = 'C:/Users/USERNAME/Downloads'
imageDestDir = 'C:/Users/USERNAME/Downloads/Images'
audioDestDir = 'C:/Users/USERNAME/Downloads/Audio'
videoDestDir = 'C:/Users/USERNAME/Downloads/Video'
docDestDir = 'C:/Users/USERNAME/Downloads/Docs'
exeDestDir = 'C:/Users/USERNAME/Downloads/Executables'
archiveDestDir = 'C:/Users/USERNAME/Downloads/Archives'
```

---

### 2️⃣ **Create Required Folders**

Ensure these folders exist in your `Downloads` directory:

- 📁 `Audio`  
- 📁 `Video`  
- 📁 `Docs`  
- 📁 `Images`  
- 📁 `Executables`  
- 📁 `Archives`

If they don't exist, create them manually.

---

### 3️⃣ **Install Dependencies**

Make sure Python is installed. Then, open **Command Prompt** or **Terminal** and run:

```cmd
pip install watchdog pystray pillow
```

---

### 4️⃣ **Convert Script to `.exe`**

Install the `auto-py-to-exe` tool:

```cmd
python -m pip install auto-py-to-exe
```

Run the tool:

```cmd
python -m auto_py_to_exe
```

1. Select your Python script (`.py`) in the **Script Location** field.  
2. Choose **"Onefile"** option.  
3. Select **"Window Based (hide the console)"**.  
4. Click **"Convert .py to .exe"**.

This will generate an `.exe` file in the output folder.

---

### 5️⃣ **Add to Startup**

1. Press `Win + R` to open the **Run** dialog.  
2. Type: `shell:startup` and press **Enter**.  
3. Copy the `.exe` file shortcut and paste it into the **Startup** folder.

Now, the program will run automatically every time your PC starts.

---

## ✅ **How to Use**

1. Place files in the `Downloads` folder.  
2. The program will automatically sort them into their respective folders.  
3. To stop the program, use the **System Tray Icon** and click **"Exit"**.

---

## 🛠️ **Troubleshooting**

- If files are not moving, check the paths in the script.  
- Make sure required folders exist in `Downloads`.  
- Verify dependencies are installed with `pip list`.

---
