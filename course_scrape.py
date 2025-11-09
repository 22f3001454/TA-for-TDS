import os
import subprocess
import shutil

# ---------------------- CONFIG -----------------------
REPO_URL = "https://github.com/sanand0/tools-in-data-science-public.git"
CLONE_DIR = "downloaded_repo"

EXTENSIONS = {
    "markdown": (".md",),
    "images": (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg"),
    "data": (".csv", ".xlsx", ".xls", ".json"),
    "html": (".html",),
    "python": (".py",)
}

EXPORT_DIRS = {
    "images": "extracted_images",
    "python": "extracted_python",
    "html": "extracted_html"
}
# -----------------------------------------------------

def clone_repo():
    if os.path.exists(CLONE_DIR):
        print(f"Removing existing folder: {CLONE_DIR}")
        shutil.rmtree(CLONE_DIR)
    print(f"Cloning repo: {REPO_URL}")
    subprocess.run(["git", "clone", REPO_URL, CLONE_DIR], check=True)

def collect_files():
    file_map = {key: [] for key in EXTENSIONS}
    for root, _, files in os.walk(CLONE_DIR):
        for file in files:
            filepath = os.path.join(root, file)
            for key, exts in EXTENSIONS.items():
                if file.lower().endswith(exts):
                    file_map[key].append(filepath)
    return file_map

def save_summary(file_map):
    with open("summary_of_files.txt", "w", encoding='utf-8') as f:
        for category, paths in file_map.items():
            f.write(f"\n📁 {category.upper()} FILES:\n")
            for path in paths:
                f.write(f"{path}\n")

def export_files(file_map):
    for category, export_dir in EXPORT_DIRS.items():
        os.makedirs(export_dir, exist_ok=True)
        for src in file_map.get(category, []):
            try:
                shutil.copy(src, export_dir)
            except Exception as e:
                print(f" Failed to copy {src}: {e}")

def main():
    clone_repo()
    file_map = collect_files()
    save_summary(file_map)
    export_files(file_map)
    print("\n✅ Done! Files collected and summary saved to 'summary_of_files.txt'")
    print("   Extracted images, HTML, and Python files saved in separate folders.")

if __name__ == "__main__":
    main()
