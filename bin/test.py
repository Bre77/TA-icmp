import os, sys
print(sys.path[0])
print(os.path.join(sys.path[0],".."))
print(os.path.join(sys.path[0],"..","local/targets.csv"))
print(os.path.join(sys.path[0],"..","../TA-icmp/local/targets.csv"))
print()
print(os.path.join(os.path.dirname(os.path.abspath(__file__))))
print(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","local/targets.csv"))