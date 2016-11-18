Optimistic Loop Optimization
============================

This documents describes how to reproduce the evaluation presented in the
*Optimistic Loop Optimization* paper at CGO17.

The full implementation has been made availablable as part of the open source
tool Polly. There are no special repositories or unmerged patches needed. All
it takes to try out the work described in the paper is a recent version of
LLVM, Clang, and Polly.

Note: *Since LLVM and Polly are under constant improvement, the results might
differ between version. However, while the exact numbers might be different we
do not expect the general effects to be. This document was written using the
following versions. Older versions of Polly do not provide the statistics
interface used in this evaluation.*

  Tool   | Version
---------|----------------------
  LLVM:  |
  Clang: |
  Polly: |

### Where to go from here

There are different levels of automation to choose from:

1) The `scripts/artifact_eval.py` is a driver that interactively performs all
steps necessary. It will set up the toolchain, the benchmarks and the test
environment before it will run the tests and aggregate the results. Each step
will be explained to the user and *all* commands that are issued are shown too.

2) The `scripts` folder contains python scripts that interactively perform
different tasks, e.g., the setup of the toolchain. The driver above only uses
them to perform the individual tasks. Thus, they allow to run or repeat tasks
individually.

3) This document explains how to set up the toolchain and the test environment
manually. It also describes the experiments and how to interpret the data.

Docker container
================

We provide a docker container that is described by the *Dockerfile* in the
*docker* directory. It is build on top of a clean Ubuntu and will install all
necessary software automatically. To build it locally run

`docker build -t cgo_ae_17 docker`

it will automatically create ....
Afterwards you can "run" the container to get an interactive bash shell.
This repository will be cloned to `/root/ae/` and an initial, up to date,
toolchain is created in the `/ae/toolchain` folder when the container is build.

We recomend to start by running the interactive `artifact_eval.py` script in the
`/ae/` folder, thus: `cd /ae; python /root/ae/scripts/artifact_eval.py`.


Setup and requirements
----------------------

LLVM, Clang and Polly all provide quick start guides that can be found online
[0-2]. In the following we describe the commands needed to prepare the
toolchain, benchmarks and the testing environment from scratch.

### System requirements [3]
  - at least 25+8=33GB of free space (LLVM/Clang/Polly debug build +
    benchmarks), a release build does require much less space and memory.
  - at least 8GB of main memory, preferably more
  - A C/C++11 enabled compiler e.g., gcc >= 4.8.0 or clang >= 3.1
  - CMake >= 3.4.3
  - GNU Make >= 3.79 (ninja is optional but often faster)
  - A Python2 interpreter >= 2.7
  - The Python2 virtualenv tool
  - zlib >=1.2.3.4
  - Common tools like: git, grep, sed


### Compiler toolchain: LLVM, Clang and Polly

If the system requirements listed above are met, build the compiler toolchain as
described in the Polly documentation online [2]. 

### Benchmarks: LLVM Test Suite, NAS Benchmark Suite, SPEC2000, SPEC2006

The `setup_benchmarks.py` script performs the following steps interactively.

##### LLVM Test Suite

Checkout the LLVM test suite in the folder *test_suite* via:

`git clone http://llvm.org/git/test-suite test_suite`

or

`svn co http://llvm.org/svn/llvm-project/test-suite/trunk test_suite`


##### NAS Benchmark Suite

The serial C implementation of the NAS benchmark suite (NPB3.3-SER-C) can be
found here [4]. However, since a registration is required to download the
benchmark suite, we provide the sources, including a modified configuration
file, to the resource folder (`resources/NPB3.3-SER-C`).


##### SPEC2000 & SPEC2006

SPEC2000 and SPEC2006 have to be acquired separately. Once they are, they should
be placed in a folder which we denote as *${SPEC_SRC}*. This folder should contain
the following structure with the actual benchmarks residing in the
CINT2000/CFP2000/CPU2006 folders:
```
  ${SPEC_SRC}/speccpu2000
  ${SPEC_SRC}/speccpu2000/benchspec
  ${SPEC_SRC}/speccpu2000/benchspec/CINT2000/
  ${SPEC_SRC}/speccpu2000/benchspec/CFP2000/
  ${SPEC_SRC}/speccpu2006
  ${SPEC_SRC}/speccpu2006/benchspec/
  ${SPEC_SRC}/speccpu2006/benchspec/CPU2006/
```
This particular arrangement allows us to run the benchmarks together with
the LLVM test suite using the LNT tool that is introduced in the following.


Note: *Use `docker cp <src_path> <container>:<dst_path>` to copy files/folder
(e.g., SPEC) from the host system to a docker container.*


##### Benchmark Versions

For the benchmarks we used the following versions, though other versions should
produce similar results.

  Benchmark        | Version
  -----------------|------------------------------------------------------------
  NPB              | SNU NPB 1.0.3, based on NPB3.3
  SPEC2000         | 1.3.1  (see "SPEC Fixes" below)
  SPEC2006         | 1.1    (see "SPEC Fixes" below)
  llvm-test-suite  | 19904bd55c45b136559a201e77319937a05348c5 (svn: r286278)


##### SPEC Fixes

The include `#include <cstddef>` is missing in:

`${SPEC_SRC}/speccpu2006/benchspec/CPU2006/447.dealII/src/include/lac/block_vector.h`.

The include `#include <cstring>` is missing in:

`${SPEC_SRC}/speccpu2000/benchspec/CINT2000/252.eon/src/ggRaster.cc`.



### Testing environments: LNT & NPB driver

We use LNT to execute the LLVM test suite as well as SPEC. The installation
of LNT is described online [5]. If `virtualenv` version 2.X is installed, the `setup_lnt.py`
script can be used to set up LNT and a sandbox. The NPB benchmarks are run
"in-place" using the `make suite` command.


### Testing

The `runtests.py` script performs the following steps interactively. 

We have three test drivers that can be executed separatly:

  - *NPB* for the SNU NPB benchmarks.
  - *LNT* for the LLVM test-suite.
  - *LNT* for the SPEC.


We assume the following environment variables are initialized according to
their description. If the provided scripts were used, all configuration values
have been written to the `scripts/config.py`. This file is also read by the
`runtest.py` script.

Variable   | Description
-----------|--------------------------------------------------------------------
SANDBOX    | Path of the python sandbox created during the installation of LNT.
LLVM_OBJ   | Path to the llvm build with polly support.
TEST_SUITE | Path to the LLVM test suite.
SPEC_SRC   | Path to the SPEC benchmarks as described above.
NPB_SRC    | Path to the NPB serial C benchmarks.
JOBS       | Number of jobs to use during evaluation.

##### *NPB* driver
The NPB driver can be run via `make suite` in the NPB source folder. The
compile time options are configured in the `config/make.defs`. The benchmarks
and input sizes are defined in the `config/suite.def`. We recommend size *W*.

##### *LNT* driver

To use the LNT driver we first set up a sandbox environment:

```
source ${SANDBOX}/bin/activate
```

Then we can run the LNT *nt* test driver:

```
  lnt runtest nt --sandbox ${SANDBOX} \
                 --cc=${CLANG} \
                 --cxx=${CLANG}++ \
                 --test-suite=${TEST_SUITE} \
                 --build-threads=${JOBS} \
                 --test-externals=${SPEC_SRC} \
                 --cflag=-O3 \
                 --cflag=-mllvm --cflag=-polly \
                 --cflag=-mllvm --cflag=-polly-run-inliner \
                 --cflag=-mllvm --cflag=-polly-invariant-load-hoisting=true \
                 --cflag=-mllvm --cflag=-polly-unprofitable-scalar-accs=false \
                 --cflag=-mllvm --cflag=-polly-allow-error-blocks=false
```

The option `--only-test=External` can be used to only run SPEC benchmarks.
Without the `--test-externals=${SPEC_SRC}` option only LLVM test suite
benchmarks are run.


### Run options

Option             | Description
-------------------|------------------------------------------------------------
-O3                | Required to run polly.
-mllvm             | Cause clang to pass the following option to llvm.
-polly             | Enable the polly pipeline.
-polly-run-inliner | Run a moderate inliner pass prior to the polly pipeline
-polly-invariant-load-hoisting=true  | Enable invariant load hoisting.
-polly-allow-error-blocks=false      | Disable the speculative expansion of SCoPs that often results in statically infeasible assumptions. Error blocks are a feature that is not yet tuned and often too aggressive.
-polly-unprofitable-scalar-accs=false| Assume scalar accesses in statements are optimize able. This is generally true though the support in Polly was dropped at some point in favor of a replacement mechanism that is still not available. Therefore, Polly currently not assume statements with scalar accesses are optimizeable while they generally are.


Experiments and data collection
-------------------------------


### Statistics and remarks

Statistics are collected if clang is run with `-mllvm -stats`.
A debug build or release build with assertions is needed to do this.
The statistics are be printed to the standard error output or logs depending on
the benchmark. To collect them one can extract the statistics key (SK) from the
error output or logs using `grep` or a similar command. For the SK *"Number of
valid Scops"* the command would be
  `grep "Number of valid Scops"`
applied to the standard error stream or log file. To summarize the outputs of
multiple input files we provide the python script `summarize_stats.py`.
Please note that the script skips lines that are not matched by the
following regular expression `"^[0-9]+ - .*"`.
The last part (after the hyphen) is used as statistics key (SK). Depending on
the way all statistics are summarized it might therefore be required to add the
`--no-filename` option to grep.

The remarks system of LLVM/Clang allows to provide feedback to the user. It is
enabled for a specific pass using `-Rpass-analysis=<passname>` (`<passname>`
should be `polly-scops` or just `polly`). The output always starts with the
filename, line and column number, if available. After the term `remark:` the
actual message is printed.


### Data collection and interpretation

##### Number of loop nests analyzed [#S]

Statically feasible assumptions (a):

The statistics key `"Number of valid Scops"` directly corresponds to this
evaluation category.

Alternatively one could enable the remarks system [see below] and check if
    the following line is in the output:

      remark: SCoP ends here.

Statically infeasible assumptions (b): 

The statistics key `"Number of SCoPs with statically infeasible context"`
directly corresponds to this evaluation category.

Alternatively one could enable the remarks system and check if the
    following line is in the output:

      remark: SCoP ends here but was dismissed.


##### Number of loop nests analyzed without assumptions [#S]

  Run options: `-mllvm -polly-optimizer=none`

  Indirectly derived number. First use the method described above to determine
  the number of *valid SCoPs*. Then disable the optimizer (to prevent early
  exits) and determine the number of SCoPs that *did require versioning*, thus
  assumptions (SK `"Number of SCoPs that required versioning."`). The difference
  is the number of SCoPs valid without assumptions.

``` 
  *#Valid Scops* - *#SCoPs that required versioning.*
```

  Alternatively one could enable the remarks system and check if there are
  no assumption remarks between:
```
    remark: SCoP begins here.
    remark: SCoP ends here.
```


##### Number of executions of optimized loop nests with assumptions [#E]

  Run options: `-mllvm -polly-codegen-emit-rtc-print`

Number of passing runtime checks (a):  Extract lines containing `'__RTC: '`
followed by a non zero number from the error stream (or logs), command:
      `grep -E '__RTC: [1-9]'`

Number of failing runtime checks (b): Extract lines containing `'__RTC: 0'` from
the error stream (or logs), command: `grep '__RTC: 0'`


##### Number of optimized loop nests executed with assumptions [#D]

  Similar to the former one *[#E]* but the result of the grep should be
  uniquely sorted with regards to the function name and region identifiers. As a
  result each executed region is only counted once. Given the grep result from
  *[#E]* one can first drop the runtime check and overflow state result using
    `sed -e 's|__RTC:.*||'`
  and then sort the lines uniquely with
    `sort -u`


##### Number of non-trivial assumptions taken (a)

  Run options: `-mllvm -polly-remarks-minimal=false -Rpass-analysis=polly-scops`

  The assumptions taken are emitted to the standard error stream using the
  remarks system of LLVM/Clang. The assumptions described in the paper have the
  following names in the remarks output:

    Statistics Key    |  Paper Section
    ------------------|:-------------:
    "Invariant load"  |  4.1
    "No-overflows"    |  4.2
    "Finite loop"     |  4.3
    "Inbounds"        |  4.4
    "Delinearization" |  4.5
    "No-aliasing"     |  4.6

  To extract them from the error stream (or logs) one can use a command like:
    `grep 'Invariant load'`

  The option `-polly-remarks-minimal=false` is currently the default. It causes
  *all* taken assumptions to be printed, even if they are already implied or
  trivially fulfilled.


##### Number of non-trivial assumptions taken that were not implied by prior ones (b)

  Run options: `-mllvm -polly-remarks-minimal=true -Rpass-analysis=polly-scops`

  Same as part *(a)* but with remark output limited to a minimum. This
  prevents the output of any already implied or trivial assumption.





# Implementation notes

Polly only has a "in-code" documentation. In addition to actual comments in the
code, function declarations are often well documented. Either check the
declarations in the header files or use the [doxygen documentation
online](http://polly.llvm.org/doxygen/).


## Assumption computation (Section 4)

Assumption computation is spread over multiple functions in `ScopInfo.cpp` and
`SCEVAffinator.cpp`. To identify the functions one can look for calls to
`recordAssumption(...)` as well as `addAssumption(...)`. The difference between
these calls is explained at their declaration in `ScopInfo.h`.



## Assumption simplification (Section 5)

The assumption simplification is partially performed during/after the assumption
computation (e.g., using `isl_set_coalesce`) but also explicitly in the
`Scop::simplifyContexts()` function. The distinction between *assumptions* and
*restrictions* is implemented using the enum `AssumptionSign` in `ScopInfo.h`.
Assumptions and respectively restrictions are collected in the
`Scop::AssumedContext` and `Scop::InvalidContext`. Overapproximations are
performed using the `isl_set_remove_divs` function, e.g., in the
`buildMinMaxAccess` function that is used to derive runtime alias checks.


## Runtime Check Generation (Section 6)

#### Algorithm 1 (Runtime Check Generation)

The overflow checks for addition (and multiplication) are implemented in the
`IslExprBuilder::createBinOp(...)` function [`IslExprBuilder.cpp`]. The
overflow tracking is enabled in the `IslNodeBuilder::createRTC(...)`
function [`IslNodeBuilder.cpp`] with the `ExprBuilder.setTrackOverflow(true)`
call. As described in the paper one can either bail as soon as an overflow
occurred or track that fact and bail in the end. To avoid a complicated
control flow graph the latter solution is implemented. The final overflow
state is queried via `ExprBuilder.getOverflowState()` after the runtime
check generation and combined with the runtime check result.

####  Algorithm 2 (Parameter Generation)

The entry point for the recursive parameter generation is the
`IslNodeBuilder::preloadInvariantLoads()` function [`IslNodeBuilder.cpp`]. It
is called by `CodeGeneration::runOnScop(...)` before a runtime check or the
optimized code version is generated.




[0] http://llvm.org/docs/GettingStarted.html

[1] http://clang.llvm.org/get_started.html

[2] http://polly.llvm.org/get_started.html

[3] http://llvm.org/docs/GettingStarted.html#requirements

[4] http://aces.snu.ac.kr/software/snu-npb/

[5] http://llvm.org/docs/lnt/quickstart.html

