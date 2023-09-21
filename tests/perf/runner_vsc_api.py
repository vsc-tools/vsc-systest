#****************************************************************************
#* runner_vsc_api.py
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
import ivpm
import os
import subprocess
from .runner import Runner
from vsc_dataclasses.impl.generators.vsc_data_model_cpp_gen import VscDataModelCppGen

class RunnerVscApi(Runner):

    def setup(self, RootC, init_count, incr_count, target_ms):
        super().setup(RootC, init_count, incr_count, target_ms)

        header='''
#include <stdio.h>
#include <stdint.h>
#include <sys/time.h>
#include "dmgr/FactoryExt.h"
#include "vsc/dm/FactoryExt.h"
#include "vsc/dm/impl/ModelBuildContext.h"
#include "vsc/solvers/FactoryExt.h"
'''
        define="void declare_cls(vsc::dm::IContext *ctxt) {\n"
        define += "\n"
        define += VscDataModelCppGen("    ").generate(self.cls)

        define += "}\n\n"

        driver="int main() {\n"
        driver += '''
    dmgr::IFactory *dmgr_f = dmgr_getFactory();
    vsc::dm::IFactory *vsc_dm_f = vsc_dm_getFactory();
    vsc_dm_f->init(dmgr_f->getDebugMgr());
    vsc::dm::IContextUP ctxt(vsc_dm_f->mkContext());

    declare_cls(ctxt.get());

    vsc::dm::IDataTypeStruct *c = ctxt->findDataTypeStruct("{0}");
    vsc::dm::ModelBuildContext build_ctxt(ctxt.get());
    vsc::dm::IModelFieldUP root(c->mkRootField(
        &build_ctxt,
        "root", 
        false));

    vsc::solvers::IFactory *solvers_f = vsc_solvers_getFactory();
    solvers_f->init(dmgr_f->getDebugMgr());

    vsc::solvers::IRandStateUP randstate(solvers_f->mkRandState("0"));
    vsc::solvers::ICompoundSolverUP solver(solvers_f->mkCompoundSolver());
    vsc::solvers::RefPathSet target_fields, fixed_fields, include_constraints, exclude_constraints;
    vsc::solvers::SolveFlags flags = vsc::solvers::SolveFlags::NoFlags;

    uint32_t count = {1};
    uint32_t incr_count = {2};
    uint32_t total_count = 0;
    uint32_t target_ms = {3};
    uint64_t tstart = 0;
    uint64_t tend = 0;
'''.format(self.clsname, init_count, incr_count, target_ms)
        driver += r'''
    struct timeval tv;
    gettimeofday(&tv, 0);
    tstart = 1000*tv.tv_sec;
    tstart += tv.tv_usec / 1000;
    tend = tstart;



    while ((tend-tstart) < target_ms) {
        for (uint32_t i=0; i<count; i++) {
            solver->randomize(
                randstate.get(),
                root.get(),
                target_fields,
                fixed_fields,
                include_constraints,
                exclude_constraints,
                flags);
        }

        total_count += count;
        count = incr_count;

        gettimeofday(&tv, 0);
        tend = 1000*tv.tv_sec;
        tend += tv.tv_usec / 1000;
    }

    fprintf(stdout, "STATS: rand=%d time_ms=%lld\n", total_count, (tend-tstart));
'''
        driver += "}\n"
        
        with open("main.cpp", "w") as fp:
            fp.write(header)
            fp.write(define)
            fp.write(driver)
        
    def compile(self):
        cmd = [
            "g++",
            "-g",
            "-o",
            "runner",
            "main.cpp"
        ]
        vsc_solvers_pkg = ivpm.get_pkg_info("vsc_solvers")
        cmd.extend(ivpm.PkgCompileFlags().flags(vsc_solvers_pkg))
        cmd.append("-lpthread")

        with open("compile.log", "w") as fp:
            result = subprocess.run(
                cmd,
                stderr=subprocess.STDOUT,
                stdout=fp
            )

        if result.returncode != 0:
            raise Exception("Compilation failed")

    def run(self) -> (int, int):
        env = os.environ.copy()
        libpath = os.environ["LD_LIBRARY_PATH"].split(":") if "LD_LIBRARY_PATH" in os.environ.keys() else []

        vsc_solvers_pkg = ivpm.get_pkg_info("vsc_solvers")
        for d in ivpm.PkgCompileFlags().ldirs(vsc_solvers_pkg):
            libpath.insert(0, d)
        
        env["LD_LIBRARY_PATH"] = ":".join(libpath)

        cmd = [
            "./runner"
        ]

        print("LD_LIBRARY_PATH=%s" % env["LD_LIBRARY_PATH"])

        with open("run.log", "w") as fp:
            result = subprocess.run(
                cmd,
                env=env,
                stderr=subprocess.STDOUT,
                stdout=fp)

        if result.returncode != 0:
            raise Exception("Run failed")

        return self.parseRunLog("run.log")

