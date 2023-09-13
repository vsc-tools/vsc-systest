#****************************************************************************
#* sim_runner_vcs.py
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

from .sim_runner import SimRunner

class SimRunnerVCS(SimRunner):

    def compile(self):
        cmd = [
            "vcs",
            "-sverilog",
        ]
        cmd.extend(self.sources)

        result = None
        with open("vcs.log", "w") as fp:
            result = subprocess.run(
                cmd,
                stderr=subprocess.STDOUT,
                stdout=fp
            )
        
        if result.returncode != 0:
            raise Exception("Compile failed")
    
    def elaborate(self):
        pass
    
    def run(self) -> (int, int):
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


