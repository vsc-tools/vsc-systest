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
import shutil
import sys
from unittest import TestCase
from vsc_dataclasses.impl.ctor import Ctor
from .sim_runner import SimRunnerMTI, SimRunnerXCM, SimRunnerXsim, SimRunnerVCS

class TestBase(TestCase):

    Runners = {
        "mti" : SimRunnerMTI,
        "vcs" : SimRunnerVCS,
        "xcm" : SimRunnerXCM,
        "xsm" : SimRunnerXsim,
    }

    def setUp(self) -> None:
        self.orig_cwd = os.getcwd()

        if "VSC_SYSTEST_RUNDIR" in os.environ.keys() and os.environ["VSC_SYSTEST_RUNDIR"] != "":
            self.rundir = os.environ["VSC_SYSTEST_RUNDIR"]
        else:
            self.rundir = os.path.join(os.getcwd(), "rundir")

        if not os.path.isdir(self.rundir):
            os.makedirs(self.rundir, exist_ok=True)

        if not os.path.isdir(os.path.join(self.rundir, "results")):
            os.makedirs(os.path.join(self.rundir, "results"), exist_ok=True)

        self.runner_id = "xsm"

        if "VSC_SYSTEST_RUNNER" in os.environ.keys():
            self.runner_id = os.environ["VSC_SYSTEST_RUNNER"]

        if self.runner_id in TestBase.Runners.keys():
            self.runner = TestBase.Runners[self.runner_id]()
        else:
            raise Exception("Runner %s is invalid" % self.runner_id)

        self.testdir = os.path.join(self.rundir, "%s.%s" % (self.runner_id, self.id()))
        if os.path.isdir(self.testdir):
            shutil.rmtree(self.testdir)

        os.makedirs(self.testdir, exist_ok=True)
        os.chdir(self.testdir)


        
        self.runner.initBackend()

        return super().setUp()
    
    def tearDown(self) -> None:
        os.chdir(self.orig_cwd)
        if sys.exc_info() == (None, None, None):
            try:
                shutil.rmtree(self.testdir)
            except Exception as e:
                print("Note: failed to remove directory %s" % self.testdir)

        return super().tearDown()

    def core_test(self, RootC, init_count, incr_count, target_ms=1000):
        # TODO: determine set of classes required and order

        self.runner.setup(RootC, init_count, incr_count, target_ms)
        self.runner.compile()
        self.runner.elaborate()
        count, time_ms = self.runner.run()
        print("%s: count=%d time_ms=%d rand/s=%f" % (self.id(), count, time_ms, time_ms/count))
        with open(os.path.join(self.rundir, "results", "%s.%s.csv" % (self.runner_id, self.id())), "w") as fp:
            fp.write("%s,%s,%d,%d,%f\n" % (self.id(),self.runner_id,count, time_ms, time_ms/count))

