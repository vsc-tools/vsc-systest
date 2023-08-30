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
from vsc_dataclasses.impl.ctor import Ctor
from vsc_dataclasses.impl.pyctxt.context import Context
from vsc_dataclasses.impl.generators.system_verilog_class_gen import SystemVerilogClassGen

class SimRunner(object):

    def __init__(self):
        self.sources = []
        self.top = "top"
        self.RootC = None
        self.clsname = None
        self.cls = None
        self.init_count = -1
        self.incr_count = -1
        self.target_ms = -1
        pass

    def initBackend(self):
        # Select the 'dummy' backend
        Ctor.init(Context())

    def setup(self, RootC, init_count, incr_count, target_ms):
        self.RootC = RootC
        self.init_count = init_count
        self.incr_count = incr_count
        self.target_ms  = target_ms
        self.cls = Ctor.inst().ctxt().findDataTypeStruct(RootC.__qualname__)
        if self.cls is None:
            raise Exception("Failed to find class %s" % RootC.__qualname__)
        self.clsname = RootC.__qualname__.split('.')[-1]

        analysis_pkg = self.getAnalysisPkg()

        cls_pkg = '''
package cls_pkg;
{0}
endpackage
  '''.format(SystemVerilogClassGen().generate(self.cls))

        driver='''
module top;
  import analysis_pkg::*;
  import cls_pkg::*;

  initial begin
    automatic longint tstart, tend;
    automatic {0} c = new();
    int init_count = {1};
    int target_ms = {3};
    int incr = {2};
    int total_count = 0;
    int count = init_count;

    tstart = gettime_ms();
    do begin
        repeat (count) begin
            void'(c.randomize());
        end
        total_count += count;
    
        tend = gettime_ms();
        count = incr;
    end while ((tend-tstart) < target_ms);

    $display("STATS: rand=%0d time_ms=%0d", total_count, (tend-tstart));
  end
endmodule'''.format(self.clsname, init_count, incr_count, target_ms)

        with open("top.sv", "w") as fp:
            fp.write(analysis_pkg)
            fp.write(cls_pkg)
            fp.write(driver)
        
        self.sources.append("top.sv")

    def compile(self):
        raise NotImplementedError("%s does not implement compile" % str(self))
    
    def elaborate(self):
        raise NotImplementedError("%s does not implement elaborate" % str(self))
    
    def run(self) -> (int,int):
        raise NotImplementedError("%s does not implement run" % str(self))
    

    def getAnalysisPkg(self):
        return '''
package analysis_pkg;
  typedef struct {
    int tv_sec;
    int tv_usec;
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
    
    def parseRunLog(self, file) -> (int,int):
        count=-1
        time_ms=-1        
        with open(file, "r") as fp:
            for line in fp.readlines():
                if line.find("STATS:") != -1:
                    elems = line[line.find("STATS:"):].split()
                    count = int(elems[1][elems[1].find('=')+1:])
                    time_ms = int(elems[2][elems[2].find('=')+1:])
                    break
        if count == -1 or time_ms == -1:
            raise Exception("Parsing failed")
        
        return (count, time_ms)

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

class SimRunnerNull(SimRunner):

    def setup(self, RootC, init_count, incr_count, target_ms):
        self.RootC = RootC
        self.init_count = init_count
        self.incr_count = incr_count
        self.target_ms  = target_ms
        self.cls = Ctor.inst().ctxt().findDataTypeStruct(RootC.__qualname__)
        if self.cls is None:
            raise Exception("Failed to find class %s" % RootC.__qualname__)
        self.clsname = RootC.__qualname__.split('.')[-1]

        print("Class:\n%s" % SystemVerilogClassGen().generate(self.cls))

    def compile(self):
        pass
    
    def elaborate(self):
        pass
    
    def run(self) -> (int, int):
        return (1,1)

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

class SimRunnerXCM(SimRunner):

    def compile(self):
        cmd = [
            "xmvlog",
            "-sv",
        ]
        cmd.extend(self.sources)

        result = None
        with open("xmvlog.log", "w") as fp:
            result = subprocess.run(
                cmd,
                stderr=subprocess.STDOUT,
                stdout=fp
            )
        
        if result.returncode != 0:
            raise Exception("Compile failed")
    
    def elaborate(self):
        cmd = ['xmelab', self.top]

        result = None
        with open("xmelab.log", "w") as fp:
            result = subprocess.run(
                cmd,
                stderr=subprocess.STDOUT,
                stdout=fp
            )
        
        if result.returncode != 0:
            raise Exception("Elab failed")



    
    def run(self) -> (int, int):
        cmd = ['xmsim', self.top]

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



