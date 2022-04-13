import os
import shutil
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

from src.console import Console


def exec_cmd(command: str) -> subprocess.CompletedProcess:
    # instead of using subprocess.Popen we use the high-level
    # function subprocess.run to avoid the pyinstaller freezing
    # due to stdin errors.

    process = subprocess.run(
        command,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
    )

    return process


def check_dependencies() -> None:
    # loops through each environment path and
    # checks if it has an {env}/g++.exe file
    dependencies = ['pyinstaller.exe', 'g++.exe']

    # split environment paths into an array of paths
    paths = os.environ['PATH'].split(';')

    # check if each dependency exists as a
    # file at the end of any environment path
    for dependency in dependencies:
        if not any(Path(env, dependency).is_file() for env in paths):
            Console.error_msg('unable to locate dependency: %s' % dependency)
            exit()


def compile_dll(
        source_path: Path,
        output_path: Path,
        work_path: Path
    ) -> None:

    # compiles the cpp to an object file and then create a
    # shared library including all the library dependencies
    
    object_path = Path(work_path, 'CompiledObj.o')

    commands = [
        f'g++ -c {source_path} -o {object_path}',
        f'g++ -shared {object_path} -o {output_path} -lstrmiids -lole32 -loleaut32'
    ]

    Console.debug_msg('compiling %s -> %s' % (source_path.name, output_path.name))
    for com in commands:
        process = exec_cmd(com)
        
        if process.stderr != b'':
            Console.error_msg('unable to compile %s' % source_path.name)
            exit()


def compile_src(
        src_path: Path,
        dist_path: Path,
        work_path: Path
    ) -> None:

    # compiles the main file of the source code into multiple files
    # to avoid the extra 10-20 seconds it will take to unpack itself
    # when containing the large modules we will use

    Console.debug_msg('compiling %s -> %s.exe' % (src_path.name, src_path.stem))

    command = 'pyinstaller "%s" --clean --noconsole --workpath "%s" --specpath "%s" --distpath "%s"'
    process = exec_cmd(command % (src_path, work_path, work_path, dist_path))

    if process.returncode != 0:
        Console.error_msg('unable to compile %s' % src_path.name)
        exit()


def create_shortcut(
        bin_path: Path,
        link_path: Path,
        work_path: Path
    ) -> None:
    
    # creates and executes a VB script to create
    # a shortcut to the main.exe executable file
    
    vb_script = f"""
    Set oWS = WScript.CreateObject("WScript.Shell") 
    sLinkFile = "{link_path}"
    Set oLink = oWS.CreateShortcut(sLinkFile)
    oLink.TargetPath = "{bin_path}"
    oLink.Save
    """

    script_path = Path(work_path, 'CreateShortcut.vbs')

    with open(script_path, 'w') as file:
        file.write(vb_script)

    exec_cmd('cscript %s' % script_path)


def copy_files(src_path: Path, dst_path: Path, relative: Path) -> None:
    try:
        Console.debug_msg('copying game files %s -> %s' % (src_path.relative_to(relative), dst_path.relative_to(relative)))
        if src_path.is_dir():
            shutil.copytree(src_path, dst_path)
        elif src_path.is_file():
            shutil.copy(src_path, dst_path)
        else:
            Console.error_msg('unable to locate %s' % src_path)
            exit()
    except OSError:
        Console.error_msg('unable to copy files')
        exit()


def compile_game(abs_path: Path):
    # with Console._handler.status('[green]Compiling game source...'):
    # checks that all dependencies are installed
    Console.debug_msg(f'checking game dependencies')
    check_dependencies()

    # set build path for containing the compiled game
    build_path = Path(abs_path, 'build')
    
    # remove old build folder and create new
    if build_path.is_dir():
        shutil.rmtree(build_path)
    build_path.mkdir()
    
    # create temporary directory path for storing build files
    tmp_dir = TemporaryDirectory()
    tmp_path = Path(tmp_dir.name)

    # compile the CaptureLib.cpp to a shared dll library
    compile_dll(
        source_path=Path(abs_path, 'src', 'capture', 'CaptureLib.cpp'),
        output_path=Path(build_path, 'CaptureLib.dll'),
        work_path=tmp_path
    )

    # compile the main.py to main.exe
    compile_src(
        src_path=Path(abs_path, 'src', 'main.py'),
        dist_path=build_path,
        work_path=tmp_path
    )

    # rename the output folder of the
    # main.py from main to to bin
    os.rename(
        Path(build_path, 'main'),
        Path(build_path, 'bin')
    )

    # copy all necessary game files to build folder
    copy_files(Path(abs_path, 'config'), Path(build_path, 'config'), abs_path)
    copy_files(Path(abs_path, 'assets'), Path(build_path, 'assets'), abs_path)

    # create windows shortcut
    Console.debug_msg('creating shortcut for main.exe executable')
    create_shortcut(
        bin_path=Path(build_path, 'bin', 'main.exe'),
        link_path=Path(build_path, 'main.lnk'),
        work_path=tmp_path
    )

    Console.debug_msg('finished building game -> ./%s' % build_path.name)


if __name__ == '__main__':
    compile_game(Path(__file__).resolve().parent)