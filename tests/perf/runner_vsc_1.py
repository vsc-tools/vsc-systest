#****************************************************************************
#* runner_vsc_1.py
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
import sys
import subprocess
from vsc_dataclasses.impl.generators.vsc_1_data_model_py_gen import Vsc1DataModelPyGen
from .runner import Runner

class RunnerVsc1(Runner):

    def setup(self, RootC, init_count, incr_count, target_ms):
        super().setup(RootC, init_count, incr_count, target_ms)
        driver='''
def main():
    c = {0}()

    count = {1}
    incr = {2}
    target_ms = {3}
    total_count = 0

    tstart = round(time.time() * 1000)

    while True:
        for _ in range(count):
            c.randomize()
        total_count += count
        tend = round(time.time() * 1000)

        if (tend-tstart) >= target_ms:
            break

        count = incr

    print("STATS: rand=%0d time_ms=%0d" % (total_count, (tend-tstart)));

if __name__ == "__main__":
    main()
'''.format(self.clsname, init_count, incr_count, target_ms)

        with open("test.py", "w") as fp:
            fp.write("import os\n")
            fp.write("import sys\n")
            fp.write("import time\n")
            fp.write("import vsc\n")
            fp.write("\n")
            fp.write(Vsc1DataModelPyGen().generate(self.cls))
            fp.write("\n")
            fp.write(driver)
            fp.write("\n")

    def run(self) -> (int, int):
        cmd = [
            sys.executable,
            "test.py"
        ]

        result = None
        with open("python.log", "w") as fp:
            result = subprocess.run(
                cmd,
                stderr=subprocess.STDOUT,
                stdout=fp
            )
        
        if result.returncode != 0:
            raise Exception("Run failed")
        
        return self.parseRunLog("python.log")

