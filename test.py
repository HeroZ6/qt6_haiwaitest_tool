import subprocess

# 替换为你的 APK 文件路径、应用包名和设备的序列号（可以通过 adb devices 命令获取）
apk_path = r"D:\PRODUCT\fileManager\file2\test\0828\2\duplicated-app.apk"
package_name = "com.yanshou.apk"
device_serial = "R68T404SMAR"

# 安装应用并传送 .debug 文件
adb_install_cmd = f"adb -s {device_serial} install -r {apk_path}"
adb_push_cmd = f"adb -s {device_serial} push path/to/your/debug/file /sdcard/android/data/{package_name}/.debug"

# 运行 ADB 命令
try:
    subprocess.run(adb_install_cmd, shell=True, check=True)
    subprocess.run(adb_push_cmd, shell=True, check=True)
    print("App installed and .debug file pushed to the app's root directory.")
except subprocess.CalledProcessError:
    print("An error occurred while installing the app or pushing the .debug file.")
