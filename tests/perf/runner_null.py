#****************************************************************************
#* runner_null.py
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
from vsc_dataclasses.impl.generators.vsc_data_model_cpp_gen import VscDataModelCppGen
from vsc_dataclasses.impl.generators.vsc_1_data_model_py_gen import Vsc1DataModelPyGen

class RunnerNull(Runner):

    def setup(self, RootC, init_count, incr_count, target_ms):
        super().setup(RootC, init_count, incr_count, target_ms)

        print("SV Class:\n%s" % SystemVerilogClassGen().generate(self.cls))
        print("C++ Class:\n%s" % VscDataModelCppGen().generate(self.cls))
        print("Vsc1 Class:\n%s" % Vsc1DataModelPyGen().generate(self.cls))

    def run(self) -> (int, int):
        return (1,1)

