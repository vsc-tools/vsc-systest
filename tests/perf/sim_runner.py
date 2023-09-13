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
from .runner import Runner
from vsc_dataclasses.impl.generators.system_verilog_class_gen import SystemVerilogClassGen

class SimRunner(Runner):

    def __init__(self):
        super().__init__()
        self.top = "top"

    def setup(self, RootC, init_count, incr_count, target_ms):
        super().setup(RootC, init_count, incr_count, target_ms)

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
    







