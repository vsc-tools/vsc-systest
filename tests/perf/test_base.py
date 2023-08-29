#****************************************************************************
#* test_base.py
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
from unittest import TestCase
from vsc_dataclasses.impl.generators.system_verilog_class_gen import SystemVerilogClassGen
from vsc_dataclasses.impl.pyctxt.context import Context
from vsc_dataclasses.impl.ctor import Ctor
from .sim_runner import SimRunnerMTI, SimRunnerXCM, SimRunnerXsim, SimRunnerVCS

class TestBase(TestCase):

    Runners = {
        "mti" : SimRunnerMTI,
        "vcs" : SimRunnerVCS,
        "xcm" : SimRunnerXCM,
        "xsim" : SimRunnerXsim,
    }

    def setUp(self) -> None:
        self.orig_cwd = os.getcwd()
        self.testdir = "rundir"
        if not os.path.isdir(self.testdir):
            os.makedirs(self.testdir)
        os.chdir(self.testdir)

        # Select the 'dummy' backend
        Ctor.init(Context())

        runner = "xsim"

        if "VSC_SYSTEST_RUNNER" in os.environ.keys():
            runner = os.environ["VSC_SYSTEST_RUNNER"]

        if runner in TestBase.Runners.keys():
            self.runner = TestBase.Runners[runner]()
        else:
            raise Exception("Runner %s is invalid" % runner)

        return super().setUp()
    
    def tearDown(self) -> None:
        os.chdir(self.orig_cwd)
        return super().tearDown()

    def runTest(self, RootC, init_count, incr_count, target_ms=2000):
        # TODO: determine set of classes required and order

        cls = Ctor.inst().ctxt().findDataTypeStruct(RootC.__qualname__)
        self.assertIsNotNone(cls)
        clsname = RootC.__qualname__.split('.')[-1]

        analysis_pkg='''
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

        cls_pkg = '''
package cls_pkg;
{0}
endpackage
  '''.format(SystemVerilogClassGen().generate(cls))

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
endmodule'''.format(clsname, init_count, incr_count, target_ms)

        with open("top.sv", "w") as fp:
            fp.write(analysis_pkg)
            fp.write(cls_pkg)
            fp.write(driver)
        
        self.runner.compile(["top.sv"])
        self.runner.elaborate("top")
        count, time_ms = self.runner.run("top")
        print("Results: count=%d time_ms=%d ; %f ms/item" % (count, time_ms, time_ms/count))

