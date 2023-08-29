#****************************************************************************
#* sim_runner.py
#*
#* Copyright 2022 Matthew Ballance and Contributors
#*
#* Licensed under the Apache License, Version 2.0 (the "License"); you may 
#* not use this file except in compliance with the License.  
#* You may obtain a copy of the License at:
#*
#*   http://www.apache.org/licenses/LICENSE-2.0
#*
#* Unless required by applicable law or agreed to in writing, software 
#* distributed under the License is distributed on an "AS IS" BASIS, 
#* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  
#* See the License for the specific language governing permissions and 
#* limitations under the License.
#*
#* Created on:
#*     Author: 
#*
#****************************************************************************
import os
import subprocess

class SimRunner(object):

    def __init__(self):
        pass

    def compile(self, srcs : list):
        raise NotImplementedError("%s does not implement compile" % str(self))
    
    def elaborate(self, top):
        raise NotImplementedError("%s does not implement elaborate" % str(self))
    
    def run(self, top) -> (int,int):
        raise NotImplementedError("%s does not implement run" % str(self))
    
    def parseRunLog(self, file) -> (int,int):
        count=-1
        time_ms=-1        
        with open(file, "r") as fp:
            for line in fp.readlines():
                if line.find("STATS:") != -1:
                    elems = line.split()
                    count = int(elems[1][elems[1].find('=')+1:])
                    time_ms = int(elems[2][elems[2].find('=')+1:])
                    break
        if count == -1 or time_ms == -1:
            raise Exception("Parsing failed")
        
        return (count, time_ms)

class SimRunnerMTI(SimRunner):

    def compile(self, srcs : list):
        if not os.path.isdir("work"):
            cmd = ["vlib", "work"]
            result = None
            with open("vlib.log", "w") as fp:
                result = subprocess.run(
                    cmd,
                    stderr=subprocess.STDOUT,
                    stdout=fp
                )
        
            if result.returncode != 0:
                raise Exception("Compile failed")
    
        cmd = [
            "vlog",
            "-sv",
        ]
        cmd.extend(srcs)

        result = None
        with open("vlog.log", "w") as fp:
            result = subprocess.run(
                cmd,
                stderr=subprocess.STDOUT,
                stdout=fp
            )
        
        if result.returncode != 0:
            raise Exception("Compile failed")
    
    def elaborate(self, top):
        cmd = [
            "vopt",
            "-o",
            "%s_opt" % top,
            top
        ]

        result = None
        with open("vopt.log", "w") as fp:
            result = subprocess.run(
                cmd,
                stderr=subprocess.STDOUT,
                stdout=fp
            )
        
        if result.returncode != 0:
            raise Exception("Elaborate failed")
    
    def run(self, top) -> (int, int):
        cmd = [
            "vsim",
            "-batch",
            "-do",
            "run -a; quit -f",
            "%s_opt" % top
        ]

        result = None
        with open("vsim.log", "w") as fp:
            result = subprocess.run(
                cmd,
                stderr=subprocess.STDOUT,
                stdout=fp
            )
        
        if result.returncode != 0:
            raise Exception("Run failed")
        
        return self.parseRunLog("vsim.log")
    
class SimRunnerVCS(SimRunner):

    def compile(self, srcs : list):
        cmd = [
            "vcs",
            "-sverilog",
        ]
        cmd.extend(srcs)

        result = None
        with open("vcs.log", "w") as fp:
            result = subprocess.run(
                cmd,
                stderr=subprocess.STDOUT,
                stdout=fp
            )
        
        if result.returncode != 0:
            raise Exception("Compile failed")
    
    def elaborate(self, top):
        pass
    
    def run(self, top) -> (int, int):
        cmd = ['./simv']

        result = None
        with open("simv.log", "w") as fp:
            result = subprocess.run(
                cmd,
                stderr=subprocess.STDOUT,
                stdout=fp
            )
        
        if result.returncode != 0:
            raise Exception("Run failed")
        
        return self.parseRunLog("simv.log")

class SimRunnerXCM(SimRunner):

    def compile(self, srcs : list):
        cmd = [
            "xmvlog",
            "-sv",
        ]
        cmd.extend(srcs)

        result = None
        with open("xmvlog.log", "w") as fp:
            result = subprocess.run(
                cmd,
                stderr=subprocess.STDOUT,
                stdout=fp
            )
        
        if result.returncode != 0:
            raise Exception("Compile failed")
    
    def elaborate(self, top):
        cmd = ['xmelab', top]

        result = None
        with open("xmelab.log", "w") as fp:
            result = subprocess.run(
                cmd,
                stderr=subprocess.STDOUT,
                stdout=fp
            )
        
        if result.returncode != 0:
            raise Exception("Elab failed")



    
    def run(self, top) -> (int, int):
        cmd = ['xmsim', top]

        result = None
        with open("xmsim.log", "w") as fp:
            result = subprocess.run(
                cmd,
                stderr=subprocess.STDOUT,
                stdout=fp
            )
        
        if result.returncode != 0:
            raise Exception("Run failed")
        
        return self.parseRunLog("xmsim.log")

class SimRunnerXsim(SimRunner):

    def compile(self, srcs : list):
        cmd = [
            "xvlog",
            "-sv",
        ]
        cmd.extend(srcs)

        result = None
        with open("xvlog.log", "w") as fp:
            result = subprocess.run(
                cmd,
                stderr=subprocess.STDOUT,
                stdout=fp
            )
        
        if result.returncode != 0:
            raise Exception("Compile failed")
    
    def elaborate(self, top):
        cmd = ['xelab', top]

        result = None
        with open("xelab.log", "w") as fp:
            result = subprocess.run(
                cmd,
                stderr=subprocess.STDOUT,
                stdout=fp
            )
        
        if result.returncode != 0:
            raise Exception("Elab failed")



    
    def run(self, top) -> (int, int):
        cmd = ['xsim', '--runall', top]

        result = None
        with open("xsim.log", "w") as fp:
            result = subprocess.run(
                cmd,
                stderr=subprocess.STDOUT,
                stdout=fp
            )
        
        if result.returncode != 0:
            raise Exception("Run failed")
        
        return self.parseRunLog("xsim.log")



