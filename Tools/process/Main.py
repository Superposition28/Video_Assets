import os
import subprocess
import sys
import configparser
import platform
from pathlib import Path

# --- Configuration ---
global MOV_SOURCE_DIR, MOV_TARGET_DIR
CONFIG_FILE_PATH = r"Vidconf.ini"
# --- End Configuration ---

def read_config(file_path: str) -> str:
    """Reads and displays the contents of a configuration file."""
    config = configparser.ConfigParser()

    configPath = Path(__file__).resolve().parent / "..\\..\\" / file_path
    print(f"Config file path: {configPath}")
    config.read(configPath)

    print(f"Config file contents: {config.sections()}")

    global MOV_SOURCE_DIR, MOV_TARGET_DIR

    MOV_SOURCE_DIR = config.get('Directories', 'MOV_SOURCE_DIR')
    MOV_TARGET_DIR = config.get('Directories', 'MOV_TARGET_DIR')

    ffmpeg_path = config.get('Tools', 'ffmpeg_path')

    return ffmpeg_path


def main():
    """Main script logic."""
    # Get FFmpeg path
    ffmpeg_path = read_config(CONFIG_FILE_PATH)

    global MOV_SOURCE_DIR, MOV_TARGET_DIR

    if not os.path.isdir(MOV_SOURCE_DIR):
        print(f"Error: Source directory not found: {MOV_SOURCE_DIR}", file=sys.stderr)
        sys.exit(1)


    # Ensure ffmpeg path exists or is in PATH
    try:
        # Check if it's an absolute/relative path first
        if os.path.sep in ffmpeg_path and not os.path.exists(ffmpeg_path):
            raise FileNotFoundError
        # If not a path with separator, try running `ffmpeg -version` to check if it's in PATH
        elif os.path.sep not in ffmpeg_path:
            subprocess.run([ffmpeg_path, "-version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Using FFmpeg found at: {ffmpeg_path}")
    except (FileNotFoundError, subprocess.CalledProcessError, OSError) as e:
        print(f"Error: FFmpeg executable not found or not runnable at: {ffmpeg_path}. Error: {e}", file=sys.stderr)
        sys.exit(1)


    # Find all .vp6 files recursively
    vp6_files = []
    for root, _, files in os.walk(MOV_SOURCE_DIR):
        for file in files:
            if file.lower().endswith(".vp6"):
                vp6_files.append(os.path.join(root, file))

    if not vp6_files:
        print("No .vp6 files found in source directory.")
        return

    # Iterate through each .vp6 file
    for file_path in vp6_files:
        try:
            # Calculate relative path
            mov_relative_path = os.path.relpath(file_path, MOV_SOURCE_DIR)
            mov_target_path = os.path.join(MOV_TARGET_DIR, mov_relative_path)

            # Ensure target directory exists
            target_directory = os.path.dirname(mov_target_path)
            if not os.path.exists(target_directory):
                print(f"Creating directory: {target_directory}")
                os.makedirs(target_directory, exist_ok=True)

            # Set target filename with .ogv extension
            base, _ = os.path.splitext(mov_target_path)
            ogv_file = base + ".ogv"

            # Check if output file already exists
            if os.path.exists(ogv_file):
                print(f"Skipping conversion for '{file_path}' as '{ogv_file}' already exists.")
                continue

            # Print conversion message
            print(f"Converting '{file_path}' to '{ogv_file}'")

            # Run ffmpeg command
            cmd = [
                ffmpeg_path,
                "-y",  # Overwrite output files without asking
                "-i", file_path,
                "-c:v", "libtheora",
                "-q:v", "7",
                "-c:a", "libvorbis",
                "-q:a", "5",
                ogv_file
            ]
            # Use shell=True on Windows if ffmpeg_path might contain spaces and isn't quoted
            use_shell = platform.system() == "Windows"
            # Run the command and let its output go directly to the console
            result = subprocess.run(cmd, check=False, shell=use_shell) # Removed capture_output=True, text=True

            if result.returncode == 0:
                print(f"Conversion completed: {ogv_file}")
            else:
                # Error message is printed, FFmpeg's own error output would have already been printed to stderr
                print(f"Error converting '{file_path}' to '{ogv_file}'. FFmpeg returned error code {result.returncode}.", file=sys.stderr)
                # Decide if you want to exit on first error or continue
                sys.exit(1) # Uncomment to exit on first error

        except Exception as e:
            print(f"An unexpected error occurred processing '{file_path}': {e}", file=sys.stderr)
            # Decide if you want to exit on first error or continue
            sys.exit(1) # Uncomment to exit on first error

if __name__ == "__main__":
    main()
    print("Script finished.")
