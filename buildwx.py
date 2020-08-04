import argparse
import os
from pathlib import Path
import subprocess


def system_call_echo(command):
    global _Execute
    print(f"calling [[[{command}]]]")
    if _Execute:
        subprocess.run(command)


vs2019_build_vars_script = "C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\Community\\VC\\Auxiliary\\Build\\vcvarsall.bat"
vs2017_build_vars_script = "C:\\Program Files (x86)\\Microsoft Visual Studio\\2017\\Community\\VC\\Auxiliary\\Build\\vcvarsall.bat"


wx_solution_path = "\\build\\msw\\"
wx_2019_solution = "wx_vc16.sln"
wx_2017_solution = "wx_vc15.sln"
# (directory, configuration, platform)
wx_tuples = [
    (plat, conf)
    for plat in ["Win32", "x64"]  # ["Win32", "x64"]
    for conf in ['"DLL Debug"', '"DLL Release"']  # ['"DLL Debug"', '"DLL Release"']
]


def build_filename(string):
    return "".join(c if c.isalnum() else "_" for c in string)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="build wxwidgets under all dll configurations on windows"
    )
    parser.add_argument(
        "source",
        type=Path,
        help="place where git repo was cloned into (with --recurse)",
    )
    parser.add_argument(
        "install",
        type=Path,
        help="place where lib will get copied to once built "
        "(under a folder that represents the checked out git obj a folder called 2017 or 2019 depending on which msbuild it is built with)",
    )
    parser.add_argument(
        "--VS2017",
        "--vc15",
        action="store_const",
        const=True,
        default=False,
        help="build with VS2017",
    )
    parser.add_argument(
        "--VS2019",
        "--vc16",
        action="store_const",
        const=True,
        default=False,
        help="build with VS2019",
    )
    parser.add_argument(
        "--custom-msbuild-arguments",
        "-m",
        default="-v:q",
        help="Custom arguments passed to msbuild.exe "
        "- sets verbosity to quiet by default.",
    )
    parser.add_argument(
        "--git-obj", "-b", default="", help="the git obj to checkout before building"
    )
    # dry run actually controlls _Execute, so default to True
    parser.add_argument(
        "--dry-run",
        "-d",
        action="store_const",
        const=False,
        default=True,
        help="don't actually execute commands, just print them.",
    )
    args = parser.parse_args()
    buildWithVS2017 = args.VS2017
    buildWithVS2019 = args.VS2019
    msargs = args.custom_msbuild_arguments
    wx_source_base = str(args.source)
    wx_install_base = str(args.install)
    git_obj = args.git_obj
    _Execute = args.dry_run
    if not buildWithVS2017 and not buildWithVS2019:
        raise argparse.ArgumentTypeError(
            "nothing to build. Must use at least one of --VS2017 and --VS2019"
        )
    elif not git_obj.strip() == "":
        print(
            f"running [[[git]]] with args [[[checkout]]] [[[{git_obj}]]] "
            f"in dir [[[{wx_source_base}]]]"
        )
        os.chdir(wx_source_base)
        subprocess.check_output(["git", "checkout", f"{git_obj}"])
    if buildWithVS2017:
        big_fat_command = f'"{vs2017_build_vars_script}" x86 & '
        big_fat_command += " & ".join(
            f'msbuild.exe {msargs} "{wx_source_base}{wx_solution_path}'
            f'{wx_2017_solution}" /p:Configuration={conf} /p:Platform={plat}'
            for plat, conf in wx_tuples
        )
        system_call_echo(big_fat_command)
        system_call_echo(
            f'xcopy /E /I /Y "{wx_source_base}\\lib" "{wx_install_base}\\{git_obj}\\2017\\lib"'
        )
        system_call_echo(
            f'xcopy /E /I /Y "{wx_source_base}\\src" "{wx_install_base}\\{git_obj}\\2017\\src"'
        )
        system_call_echo(
            f'xcopy /E /I /Y "{wx_source_base}\\include" "{wx_install_base}\\{git_obj}\\2017\\include"'
        )
    if buildWithVS2019:
        big_fat_command = f'"{vs2019_build_vars_script}" x86 & '
        big_fat_command += " & ".join(
            f'msbuild.exe {msargs} "{wx_source_base}{wx_solution_path}'
            f'{wx_2019_solution}" /p:Configuration={conf} /p:Platform={plat}'
            for plat, conf in wx_tuples
        )
        system_call_echo(big_fat_command)
        system_call_echo(
            f'xcopy /E /I /Y "{wx_source_base}\\lib" "{wx_install_base}\\{build_filename(git_obj)}\\2019\\lib"'
        )
        system_call_echo(
            f'xcopy /E /I /Y "{wx_source_base}\\src" "{wx_install_base}\\{build_filename(git_obj)}\\2019\\src"'
        )
        system_call_echo(
            f'xcopy /E /I /Y "{wx_source_base}\\include" "{wx_install_base}\\{build_filename(git_obj)}\\2019\\include"'
        )

