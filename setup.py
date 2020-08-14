from cx_Freeze import setup, Executable
import os
#import platform

CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
include_files = [(os.path.join(CURRENT_PATH, "chromedriver.exe"), "chromedriver.exe")]
#if platform.system() == "Linux":
#      include_files.append((os.path.join(CURRENT_PATH, "lib", "libpython3.5m.so.1.0"), "libpython3.5m.so.1.0"))

buildOptions = dict(include_files=include_files,
                    packages=["sys"])

app_name = "reserve_comping"

setup(name=app_name,
      version="1.0",
      description=app_name.replace("_", " "),
      author="rozig",
      options=dict(build_exe=buildOptions),
      executables=[Executable("gang_dong.py"), Executable("joong_rang.py"), Executable("gong_reung.py"),
                   Executable("so_pung.py")])
