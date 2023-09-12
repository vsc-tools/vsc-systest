#****************************************************************************
#* test_scalar_fixed_sz_arr.py
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

class TestScalarFixedSzArr(TestBase):

    def test_unconstrained_med(self):

        @vdc.randclass
        class MyC(object):
            a : vdc.rand_list_t[vdc.uint32_t][120]
            b : vdc.rand_list_t[vdc.uint32_t][10]

        self.core_test(MyC, 
            init_count={
                "vsc1": 2000,
                "default": 10000}, 
            incr_count=5000)

    def test_unconstrained_large(self):

        @vdc.randclass
        class MyC(object):
            a : vdc.rand_list_t[vdc.uint32_t][1200]
            b : vdc.rand_list_t[vdc.uint32_t][4000]

        self.core_test(MyC, 
                init_count=500, 
                incr_count=250)

    def test_constrained_indep_med(self):

        @vdc.randclass
        class MyC(object):
            a : vdc.rand_list_t[vdc.uint32_t][100]
            b : vdc.rand_list_t[vdc.uint32_t][200]

            @vdc.constraint
            def ab_c(self):
                with vdc.foreach(self.a, idx=True) as i:
                    self.a[i] == 2
                with vdc.foreach(self.b, idx=True) as i:
                    self.b[i] == 5

        self.core_test(MyC, 
                init_count=500, 
                incr_count=250)

