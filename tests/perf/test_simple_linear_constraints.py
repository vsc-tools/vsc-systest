#****************************************************************************
#* test_simple_linear_constraints.py
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
import vsc_dataclasses as vdc
from .test_base import TestBase

class TestSimpleLinearConstraints(TestBase):

    def test_32bit_2var_ule(self):
        @vdc.randclass
        class MyC(object):
            a : vdc.rand_uint32_t
            b : vdc.rand_uint32_t

            @vdc.constraint
            def ab_c(self):
                self.a < self.b

        self.core_test(MyC, init_count=10000, incr_count=5000)

    def test_32bit_4var_alleq(self):
        @vdc.randclass
        class MyC(object):
            a : vdc.rand_uint32_t
            b : vdc.rand_uint32_t
            c : vdc.rand_uint32_t
            d : vdc.rand_uint32_t

            @vdc.constraint
            def ab_c(self):
                self.a == self.b
                self.a == self.c
                self.b == self.c

        self.core_test(MyC, init_count=10000, incr_count=5000)

    def test_32bit_4var_noteq(self):
        @vdc.randclass
        class MyC(object):
            a : vdc.rand_uint32_t
            b : vdc.rand_uint32_t
            c : vdc.rand_uint32_t
            d : vdc.rand_uint32_t

            @vdc.constraint
            def ab_c(self):
                self.a != self.b
                self.a != self.c
                self.b != self.c

        self.core_test(MyC, init_count=10000, incr_count=5000)