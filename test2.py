import re
import subprocess


def get_appPackagename(path):
    """
    :param path: 包的绝对路径，反编译包得到包的包名
    :return:
    """
    cmd = "aapt dump badging %s" % path
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         stdin=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    match = re.compile("package: name='(\S+)' versionCode='(\d+)' versionName='(\S+)'").match(output.decode())
    if not match:
        return "获取不到包名,请检查apk路径是否有中文"
    appPackage = match.group(1)
    return appPackage

a = get_appPackagename(r"D:\PRODUCT\GAME\0804test\4\app-release-20230810-1.apk")
print(a)