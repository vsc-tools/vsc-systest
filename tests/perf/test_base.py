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
import logging
import os
import shutil
import sys
from unittest import TestCase
from vsc_dataclasses.impl.ctor import Ctor
from .sim_runner_mti import SimRunnerMTI
from .runner_null import RunnerNull
from .sim_runner_vcs import SimRunnerVCS
from .runner_vsc_1 import RunnerVsc1
from .runner_vsc_api import RunnerVscApi
from .sim_runner_xcm import SimRunnerXCM
from .sim_runner_xsim import SimRunnerXsim

class TestBase(TestCase):

    Runners = {
        "mti"  : SimRunnerMTI,
        "null" : RunnerNull,
        "vcs"  : SimRunnerVCS,
        "vsc1" : RunnerVsc1,
        "vsc-api" : RunnerVscApi,
        "xcm"  : SimRunnerXCM,
        "xsm"  : SimRunnerXsim,
    }

    def setUp(self) -> None:
        self.orig_cwd = os.getcwd()

        if "LOGLEVEL" in os.environ.keys() and os.environ["LOGLEVEL"] != "":
            LOGLEVEL = os.environ["LOGLEVEL"].upper()
            logging.basicConfig(level=LOGLEVEL)

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
#        if sys.exc_info() == (None, None, None):
#            try:
#                shutil.rmtree(self.testdir)
#            except Exception as e:
#                print("Note: failed to remove directory %s" % self.testdir)

        return super().tearDown()

    def core_test(self, 
                  RootC, 
                  init_count, 
                  incr_count, 
                  target_ms=1000,
                  include=None,
                  exclude=None
                  ):
        # TODO: determine set of classes required and order

        is_controlled = include is not None or exclude is not None
        is_included = include is not None and self.runner_id in include
        is_excluded = exclude is not None and self.runner_id in exclude

        if not is_controlled or (is_included and not is_excluded):
            if isinstance(init_count, dict):
                if self.runner_id in init_count.keys():
                    init_count_p = init_count[self.runner_id]
                elif "default" in init_count.keys():
                    init_count_p = init_count["default"]
                else:
                    raise Exception("No runner-specific or default setting")
            else:
                init_count_p = init_count
        
            if isinstance(incr_count, dict):
                if self.runner_id in incr_count.keys():
                    incr_count_p = incr_count[self.runner_id]
                elif "default" in incr_count.keys():
                    incr_count_p = incr_count["default"]
                elif None in incr_count.keys():
                    incr_count_p = incr_count[None]
                else:
                    raise Exception("No runner-specific or default setting")
            else:
                incr_count_p = incr_count

            self.runner.setup(
                RootC, 
                init_count_p, 
                incr_count_p, 
                target_ms)
            self.runner.compile()
            self.runner.elaborate()
            count, time_ms = self.runner.run()
            print("%s: count=%d time_ms=%d ms/rand=%f" % (self.id(), count, time_ms, time_ms/count))
            with open(os.path.join(self.rundir, "results", "%s.%s.csv" % (self.runner_id, self.id())), "w") as fp:
                fp.write("%s,%s,%d,%d,%f\n" % (self.id(),self.runner_id,count, time_ms, time_ms/count))
        else:
            print("%s: SKIP" % (self.id(),))
#            with open(os.path.join(self.rundir, "results", "%s.%s.csv" % (self.runner_id, self.id())), "w") as fp:
#                fp.write("%s,%s,%d,%d,%f\n" % (self.id(),self.runner_id,0,0,0))


