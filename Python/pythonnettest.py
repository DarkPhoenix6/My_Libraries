import sys

import clr

clr.AddReference('System.Reflection')
from System.Reflection import Assembly

dll1 = Assembly.LoadFile('C:\\Users\\Chris\\AppData\Local\Programs\Python\Python36\Lib\site-packages\Python.Runtime.dll')
from System import String
