# Smart File Organizer (AutoSort)

![Python Version](https://img.shields.io/badge/python-3.x-blue.svg)
![Platform](https://img.shields.io/badge/platform-windows-lightgrey)
![Status](https://img.shields.io/badge/status-active-success.svg)

---

**Official Website:** [Visit AutoSort Online](https://oussamale.github.io/AutoSort-Site/)

---

**Smart File Organizer** is a background file management utility featuring a modern graphical user interface (GUI). It runs transparently in the background, watching a designated folder (e.g., Download directory), and dynamically categorizes moving or incoming files into neatly organized subdirectories.

With an aesthetic Light Creamy Theme, real-time activity logging, and duplicate resolution logic, it turns digital clutter into perfect organization.

---

## Key Features

- **Real-Time Monitoring:** Employs `watchdog` to actively monitor and organize files the second they finish downloading or enter the directory.
- **Retroactive Cleanup:** Got a folder with 500+ files already? Use the "Organize Existing Files" feature to process pre-existing clutter in one click.
- **Beautiful Aesthetic GUI:** Features a customized "Light Creamy" modern theme, providing an interface that is easy on the eyes with contextual interactive status updates.
- **Smart Duplicate Management:** Automatically handles identically named files by gracefully appending numerical sequences (e.g., `file (1).pdf`) instead of being overwritten.
- **Safe Processing:** Ignores active temporary files (`.crdownload`, `.part`, etc.) preventing broken partial downloads.
- **Deeply Configurable:** Effortlessly tweak watched categories, extensions, and logic via a simple JSON configuration document.

---

## Project Structure

The project has been carefully modularized for maintainability and scale:

```text
AutoSort/
│
├── core/
│   ├── __init__.py
│   ├── config.py         # JSON config loader and manager
│   └── organizer.py      # Core classification and watchdog logic
│
├── gui/
│   ├── __init__.py
│   └── app.py            # The Tkinter GUI application & styling
│
├── utils/
│   ├── __init__.py
│   └── file_utils.py     # Helper functions (e.g. resolve duplicates)
│
├── config.json           # Stores folder targets, rules, and extensions
├── main.py               # The main entry point to run the app
└── README.md             # You are here!
```

---

## Getting Started

### Prerequisites

You will need Python 3 installed on your machine.
Ensure you have installed the required dependencies.

```bash
pip install watchdog
```
*(Note: `tkinter` comes pre-installed with standard Python distributions on Windows)*

### Installation

1. **Clone or Download** the repository to your local machine.
2. Navigate to the `AutoSort` directory:
   ```bash
   cd path/to/AutoSort
   ```

### Execution

Launch the application simply by executing `main.py`:

```bash
python main.py
```

---

## Usage

1. **Select a Directory:** Upon launching, if a directory is not already configured, click the **Browse** button to select the target folder you want to keep organized (e.g., `C:\Users\username\Downloads`).
2. **Start Watching:** Click **Start Watching**. The app will immediately begin routing new files based on their extensions to categorical subdirectories.
3. **Organize Existing Files:** Click this if the selected folder is already messy. The app will comb through all existing files and route them chronologically.
4. **Stop Operations:** Click **Stop All** to safely kill the watchdog observer. 
5. **Activity Logs:** Refer to the "Activity Log" pane at the bottom to see exactly where and when your files were routed in real-time.

---

## Configuration (`config.json`)

All magic happens inside `config.json`. You can easily add, remove, or edit file extensions and their parent directories. 

Here is an example snippet of how easy it is to tweak:

```json
{
    "watch_directory": "C:/Users/.../Downloads",
    "handle_duplicates": true,
    "categories": {
        "Images": [".jpg", ".jpeg", ".png", ".gif"],
        "Documents": {
            "PDF": [".pdf"],
            "Word": [".docx", ".doc"]
        },
        "Code": [".py", ".html", ".css", ".js"]
    }
}
```

* **`watch_directory`**: Auto-saved from the GUI, but can be manually defined.
* **`handle_duplicates`**: If true, prevents files from being overwritten.
* **`categories`**: Defines the parent folders and matching extensions. You can create sub-folders (like `Documents/PDF`) by using nested dictionaries!

---

## License


This project is open source and available under the [MIT License](LICENSE).

