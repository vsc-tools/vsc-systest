#****************************************************************************
#* __main__.py
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
import argparse
import os
import shutil
import subprocess
import sys

target_cmd_m = {
    "mti": "vlog",
    "vcs": "vcs",
    "vsc1": None,
    "xsm": "xsim",
    "xcm": "xmvlog"
}

def get_avail():
    avail_targets = []
    for targ in sorted(target_cmd_m.keys()):
        cmd = target_cmd_m[targ]

        if cmd is None:
            avail_targets.append(targ)
        else:
            if shutil.which(cmd) is not None:
                avail_targets.append(targ)
    return avail_targets

def cmd_probe(args):
    for targ in sorted(target_cmd_m.keys()):
        cmd = target_cmd_m[targ]

        if cmd is None:
            print("%s - enabled (default)" % targ)
        else:
            path = shutil.which(cmd)
            if path is None:
                print("%s - disabled (%s not found)" % (targ, cmd))
            else:
                print("%s - enabled (%s found @ %s)" % (targ, cmd, path))
    pass

def cmd_run(args):
    targets = []
    script_dir = os.path.dirname(os.path.abspath(__file__))
    vsc_systest_dir = os.path.abspath(script_dir + "../../..")

    print("vsc_systest_dir=%s" % vsc_systest_dir)

    avail = get_avail()

    if args.include is not None:
        for i in args.include:
            if i in avail:
                targets.append(i)
    else:
        targets.extend(avail)
    
    if args.exclude is not None:
        for e in args.exclude:
            if e in targets:
                targets.remove(e)
    
    if args.outdir is not None:
        rundir = args.outdir
    else:
        rundir = os.path.join(os.getcwd(), "rundir")

    if os.path.isdir(rundir):
        print("Note: rundir exists (%s)" % rundir)
    else:
        print("Note: creating rundir (%s)" % rundir)
    
    env = os.environ.copy()
    env["VSC_SYSTEST_RUNDIR"] = rundir
    env["PYTHONPATH"] = os.path.join(vsc_systest_dir, "tests")

    for t in targets:
        print("Note: running tests for target %s" % t)

        env["VSC_SYSTEST_RUNNER"] = t

        cmd = [
            sys.executable,
            "-m",
            "unittest"
        ]

        subprocess.run(
            cmd,
            cwd=os.path.join(vsc_systest_dir, "tests"),
            env=env
        )

    print("Targets: %s" % str(targets))
    
    pass

def getparser():
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers()
    subparser.required = True

    probe_parser = subparser.add_parser("probe")
    probe_parser.set_defaults(func=cmd_probe)

    run_parser = subparser.add_parser("run")
    run_parser.add_argument("-i", "--include", action="append",
                            choices=sorted(target_cmd_m.keys()),
                help="Specify target to include in the list to run")
    run_parser.add_argument("-e", "--exclude", action="append",
                            choices=sorted(target_cmd_m.keys()),
                help="Specify target to exclude from the list to run")
    run_parser.add_argument("-o", "--outdir",
                help="Location where output is stored (rundir)")
    run_parser.set_defaults(func=cmd_run)
    
    return parser

def main():
    parser = getparser()

    args = parser.parse_args()

    args.func(args)

if __name__ == "__main__":
    main()


