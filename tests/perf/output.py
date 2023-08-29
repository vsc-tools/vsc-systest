#****************************************************************************
#* output.py
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
import io

class Output(object):

    def __init__(self, fp=None):
        if fp is not None:
            self._out = fp
        else:
            self._out = io.StringIO()
        self._ind = ""
        pass

    def getvalue(self):
        if isinstance(self._out, io.StringIO):
            return self._out.getvalue()
        else:
            raise Exception("Output doesn't support getvalue")

    def println(self, val):
        self._out.write(self._ind)
        self._out.write(val)
        self._out.write("\n")
    
    def inc_indent(self):
        self._ind += "    "
    
    def dec_indent(self):
        if len(self._ind) > 4:
            self._ind = self._ind[4:]
        else:
            self._ind = ""




