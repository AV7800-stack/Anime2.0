import os
import sys
import subprocess

def main():
    # Define the path to the actual application directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    app_dir = os.path.join(base_dir, 'anime-video-generator')
    run_script = os.path.join(app_dir, 'run.py')

    if not os.path.exists(run_script):
        print(f"Error: Could not find the run script at {run_script}", file=sys.stderr)
        sys.exit(1)

    print(f"Starting Anime 2.0 Video Generator...")
    print(f"Working directory: {app_dir}")
    
    # Run the actual application script, changing the working directory to the app folder
    try:
        subprocess.run([sys.executable, "run.py"], cwd=app_dir, check=True)
    except KeyboardInterrupt:
        print("\nApplication stopped by user.")
    except subprocess.CalledProcessError as e:
        print(f"\nApplication exited with error code {e.returncode}", file=sys.stderr)
        sys.exit(e.returncode)
    except Exception as e:
        print(f"\nAn error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
