#!/usr/bin/python2.4
import os

def getUptime():
    # second number is amount of time system has been idle since reboot.
    return float(open('/proc/uptime').read().strip().split()[0])

def getLoadAverage():
    # The fourth number is the number of running processes / total number of 
    # processes.
    # The fifth number is the highest PID used.
    data = open('/proc/loadavg').read().strip().split()[0:3]
    return tuple(float(x) for x in data)

def getCpuInfo():
    f = open("/proc/cpuinfo")
    parts = f.read().strip().split("\n\n")
    f.close()
    cpus = []
    for p in parts:
        lines = p.strip().split("\n")
        lines = [ l.split(":", 1) for l in lines ]
        cpuDict = dict( (key.strip(), val.strip()) for (key, val) in lines )
        cpus.append(CPUInfo(cpuDict["cpu MHz"], cpuDict["model name"]))
    return cpus

#def getStatInfo():
#    Get information about disk I/O, niced processes, etc.
#    open('/proc/stat') # http://www.linuxhowtos.org/System/procstat.htm

def getMountInfo():
    txt = os.popen('/bin/df -TP').read()
    lines = txt.split('\n')[1:-1]
    mounts = {}
    for cols in (x.split() for x in lines if x):
        device, type, blocks, used, avail, capacity, mount = cols
        blocks, used, avail = int(blocks), int(used), int(avail)
        if device == 'none':
            device = None
        mounts[mount] = Partition(device, type, blocks, used, avail)
    return mounts

def getMemInfo():
    f = open("/proc/meminfo")
    lines = f.read().strip().split("\n")
    f.close()
    lines = [ l.split(None, 1) for l in lines ]
    memDict = dict( (key, val.strip().split()[0]) for (key, val) in lines )
    totalMemory = int(memDict["MemTotal:"])
    freeMemory = int(memDict["MemFree:"])
    totalSwap = int(memDict["SwapTotal:"])
    freeSwap = int(memDict["SwapFree:"])
    return (freeMemory, totalMemory), (freeSwap, totalSwap)

class CPUInfo(object):
    def __init__(self, freq, model):
        self.freq = freq
        self.model = model

class Partition(object):
    def __init__(self, device, type, blocks, used, avail):
        self.device = device
        self.type = type
        self.blocks = blocks
        self.used = used
        self.avail = avail

    def __repr__(self):
        return "Partition(device=%r, type=%r, blocks=%r, used=%r, avail=%r)" \
                 % (self.device, self.type, self.blocks, self.used, self.avail)

    def __str__(self):
        return "%sK  (%sK free)" % (self.blocks, self.avail)

class MachineInformation(object):
    def __init__(self):
        self.hostname = os.uname()[2]
        self.cpus = getCpuInfo()
        self.update()

    def update(self):
        self.mounts = getMountInfo()
        self.meminfo = getMemInfo()
        self.loadavg = getLoadAverage()
        self.uptime = getUptime()

    def __str__(self):
        l = []
        l.append('Machine: %s' % self.hostname)
        l.append('CPUs: %s' % (len(self.cpus)))
        for idx, cpu in enumerate(self.cpus):
            l.append('  %s: %sMhz %s' % (idx, cpu.freq, cpu.model))
        l.append('Memory: %sK (%sK Free)' % self.meminfo[0])
        l.append('Swap: %sK (%sK Free)' % self.meminfo[1])
        l.append('')
        l.append('Load Average: %s (now) %s (5m) %s (15m)' % self.loadavg)
        l.append('Uptime: %ss' % self.uptime)
        l.append('Mounts:')
        l.extend(self.formatMountInfo())
        return '\n'.join(l)


    def formatMountInfo(self):
        l = []
        for mount, part in sorted(self.mounts.iteritems()):
            l.append("%-20s%s" % (mount + ':', part))
        return l

if __name__ == "__main__":
    print MachineInformation()
