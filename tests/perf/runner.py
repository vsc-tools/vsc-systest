#****************************************************************************
#* runner.py
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
from vsc_dataclasses.impl.ctor import Ctor
from vsc_dataclasses.impl.pyctxt.context import Context

class Runner(object):

    def __init__(self):
        self.sources = []
        self.RootC = None
        self.clsname = None
        self.cls = None
        self.init_count = -1
        self.incr_count = -1
        self.target_ms = -1

    def initBackend(self): 
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

    def compile(self):
        pass

    def elaborate(self):
        pass
    
    def run(self) -> (int,int):
        raise NotImplementedError("%s does not implement run" % str(self))
    
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

