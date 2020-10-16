from cx_Freeze import setup, Executable
import os

CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
DRIVER_PATH = os.path.join("driver")
include_files = [DRIVER_PATH]

#if platform.system() == "Linux":
#      include_files.append((os.path.join(CURRENT_PATH, "lib", "libpython3.5m.so.1.0"), "libpython3.5m.so.1.0"))

executable_list = [
    Executable(os.path.join(CURRENT_PATH, "reserve", "runner", "xticket", "gang_dong.py")),
    Executable(os.path.join(CURRENT_PATH, "reserve", "runner", "xticket", "joong_rang.py")),
    Executable(os.path.join(CURRENT_PATH, "reserve", "runner", "interpark", "gong_reung.py")),
    Executable(os.path.join(CURRENT_PATH, "reserve", "runner", "interpark", "so_pung.py"))
]

buildOptions = dict(include_files=include_files,
                    packages=["sys"])

app_name = "reserve_comping"

setup(name=app_name,
      version="1.0",
      description=app_name.replace("_", " "),
      author="rozig",
      options=dict(build_exe=buildOptions),
      executables=executable_list)
