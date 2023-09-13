#****************************************************************************
#* sim_runner_mti.py
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
import sys
from .sim_runner import SimRunner

class SimRunnerMTI(SimRunner):

    def compile(self):
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
        cmd.extend(self.sources)

        result = None
        with open("vlog.log", "w") as fp:
            result = subprocess.run(
                cmd,
                stderr=subprocess.STDOUT,
                stdout=fp
            )
        
        if result.returncode != 0:
            raise Exception("Compile failed")
    
    def elaborate(self):
        cmd = [
            "vopt",
            "-o",
            "%s_opt" % self.top,
            self.top
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
    
    def run(self) -> (int, int):
        cmd = [
            "vsim",
            "-batch",
            "-do",
            "run -a; quit -f",
            "%s_opt" % self.top
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


