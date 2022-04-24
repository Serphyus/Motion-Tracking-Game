import os
import subprocess
from pathlib import Path
from rich.console import Console
from typing import Sequence


def map_files(prefix: str) -> list:
    paths = []
    for sub in os.listdir(prefix):
        curr_path = Path(prefix, sub)
        if curr_path.is_dir():
            paths += map_files(curr_path)
        elif curr_path.is_file():
            paths.append(curr_path)
        else:
            raise OSError('unable to identify path')
    return paths


def menu(title: str, options: Sequence[Path]) -> Sequence[Path]:
    print(f'\n%s\n%s\n' % (title, ('-'*len(title))))

    for index, path in enumerate(options + ['Run all tests']):
        print(' %i) %s' % (index+1, path))

    choice = -1
    while True:
        user_input = input('\nchoice: ')
        
        if user_input.isdigit():
            choice = int(user_input)
            if choice in range(1, len(options)+1):
                return [options[choice-1]]
            elif choice == len(options)+1:
                return options
        
        print('\x1b[2A\x1b[0J', end='')


def run_test(script_path: Path, cwd: Path) -> subprocess.CompletedProcess:
    process_env = os.environ.copy()
    process_env['PYTHONPATH'] = str(cwd)
    
    process = subprocess.run(
        'python %s %s' % (script_path, cwd),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        env=process_env
    )

    return process


def main(abs_path: Path):
    console = Console(log_time_format='[%H:%M:%S.%f]')

    source_path = Path(abs_path.parent, 'src')

    test_scripts = []
    for path in map_files(Path(abs_path, 'scripts')):
        test_scripts.append(path.relative_to(abs_path))

    looped = True
    while looped:
        try:
            console.clear()
            chosen_scripts = menu('Testing Scripts', test_scripts)
            console.clear()
            
            no_errors = True
            for script in chosen_scripts:
                with console.status('[bold green]Running test scripts...') as status:
                    console.log('Running Test -> %s' % script.name)
                    process = run_test(Path(abs_path, script), source_path)

                    if process.returncode != 0 or process.stderr != b'':
                        no_errors = False
                        status.stop()
                        print(process.stderr.decode())
                        break
            
            if no_errors:
                console.log('All tests were successful')
            else:
                console.log('[bold red]Errors occured when running tests')

            input('\n[press enter to return]')
        
        except KeyboardInterrupt:
            looped = False


if __name__ == '__main__':
    main(Path(__file__).resolve().parent)