#****************************************************************************
#* sim_runner_xsim.py
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
import subprocess
from .sim_runner import SimRunner

class SimRunnerXsim(SimRunner):

    def compile(self):
        cmd = [
            "xvlog",
            "-sv",
        ]
        cmd.extend(self.sources)

        result = None
        with open("xvlog.log", "w") as fp:
            result = subprocess.run(
                cmd,
                stderr=subprocess.STDOUT,
                stdout=fp
            )
        
        if result.returncode != 0:
            raise Exception("Compile failed")
    
    def elaborate(self):
        cmd = ['xelab', self.top]

        result = None
        with open("xelab.log", "w") as fp:
            result = subprocess.run(
                cmd,
                stderr=subprocess.STDOUT,
                stdout=fp
            )
        
        if result.returncode != 0:
            raise Exception("Elab failed")
    
    def run(self) -> (int, int):
        cmd = ['xsim', '--runall', self.top]

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
    
    def getAnalysisPkg(self):
        return '''
package analysis_pkg;
  typedef struct {
    longint tv_sec;
    longint tv_usec;
  } timeval_s;

  import "DPI-C" context function int gettimeofday(output timeval_s tv, input chandle r);

  function automatic longint unsigned gettime_ms();
    automatic timeval_s tv;
    longint unsigned ret;

    if (gettimeofday(tv, null) != 0) begin
        $display("Error: gettimeofday failed");
    end
    ret = tv.tv_sec;
    ret *= 1000;
    ret += tv.tv_usec / 1000;

    return ret;
  endfunction
endpackage'''


