import os
import subprocess
from pathlib import Path
from typing import Sequence
from contextlib import suppress


class Loader:
    def __init__(self, msg: str) -> None:
        self._msg = msg
        
        self._symbols = "-\\|/"
        self._current = 0
    

    def update(self) -> None:
        symbol = self._symbols[self._current]
        print("\r \033[33m[%s]\033[0m %s" % (symbol, self._msg), end="")
        self._current = (self._current + 1) % (len(self._symbols) - 1)


    def success(self) -> None:
        print("\r \033[32m[+]\033[0m")


    def warning(self) -> None:
        print("\r \033[33m[!]\033[0m")

    
    def error(self) -> None:
        print("\r \033[31m[!]\033[0m")


    def __enter__(self) -> object:
        return self
    

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        pass


def map_files(prefix: str) -> list:
    paths = []
    for sub in os.listdir(prefix):
        curr_path = Path(prefix, sub)
        if curr_path.is_dir():
            paths += map_files(curr_path)
        elif curr_path.is_file():
            paths.append(curr_path)
        else:
            raise OSError("unable to identify path")
    return paths


def menu(title: str, options: Sequence[Path]) -> Sequence[Path]:
    print(f"\n%s\n%s\n" % (title, ("-"*len(title))))

    for index, path in enumerate(options + ["Run all tests"]):
        print(" %i) %s" % (index+1, path))

    while True:
        user_input = input("\nchoice: ")
        
        if user_input.isdigit():
            choice = int(user_input)
            if choice in range(1, len(options)+1):
                return [options[choice-1]]
            elif choice == len(options)+1:
                return options
        
        print("\x1b[2A\x1b[0J", end="")


def run_test(script_path: Path, cwd: Path) -> subprocess.Popen:
    process_env = os.environ.copy()
    process_env["PYTHONPATH"] = str(cwd)
    
    process = subprocess.Popen(
        "python %s %s" % (script_path, cwd),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        env=process_env
    )

    return process


def clear_screen() -> None:
    print("\x1b[H\x1b[2J\x1b[3J", end="")


def main(abs_path: Path):
    source_path = Path(abs_path.parent, "src")

    test_scripts = []
    for path in map_files(Path(abs_path, "scripts")):
        test_scripts.append(path.relative_to(abs_path))

    looped = True
    while looped:
        try:
            clear_screen()
            chosen_scripts = menu("Testing Scripts", test_scripts)
            
            clear_screen()
            print("\n Running Test Scripts")
            print(" --------------------")
            for script in chosen_scripts:
                process = run_test(Path(abs_path, script), source_path)
                
                with Loader("Running Test -> %s" % script.name) as load:
                    while process.poll() is None:
                        load.update()
                        with suppress(subprocess.TimeoutExpired):
                            process.wait(0.25)
                
                    if process.returncode != 0:
                        load.error()
                    elif process.stderr.read() != b"":
                        load.warning()
                    else:
                        load.success()
            
            input("\n[press enter to return]")
        
        except KeyboardInterrupt:
            looped = False


if __name__ == "__main__":
    main(Path(__file__).resolve().parent)