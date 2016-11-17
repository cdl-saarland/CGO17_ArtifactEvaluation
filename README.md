Optimistic Loop Optimization
============================

tl;dr
The *artifact_eval.py* script is a driver that will interactively perform all
steps described in this documents. The commands as well as an
explanation for each step are provided.


Setup and requirements
----------------------

LLVM, Clang and Polly all provide quick start guides that can be found online
[0-2]. If the system requirements listed below are met the automatic script
provided to setup Polly [3] is the simplest way to install the compiler
toolchain. In the following we describe the commands needed to prepare the
benchmarks and the testing environment from scratch.

### System requirements [4]:
  - at least 25+8=33GB of free space (LLVM/Clang/Polly debug build +
    benchmarks), a release build does require much less space and memory.
  - at least 8GB of main memory, preferably more
  - A C/C++11 enabled compiler e.g., gcc >= 4.8.0 or clang >= 3.1
  - CMake >= 3.4.3
  - GNU Make >= 3.79
  - A Python 2 interpreter >= 2.7
  - zlib >=1.2.3.4


### Compiler toolchain: LLVM, Clang and Polly

To setup the compiler toolchain use the *setup_toolchain.py* script or the
"polly.sh" script provided online [3]. Since LLVM and Polly are under constant
improvement, the results might differe between version. However, while the exact
numbers might be different we do not expect the general effects to be.
This document was written using the following versions which are necessary to
collect most information without modifying the source code manually:

  Tool   | Version
---------|----------------------
  LLVM:  |
  Clang: |
  Polly: |


### Benchmarks: LLVM Test Suite, NAS Benchmark Suite, SPEC2000, SPEC2006

The *setup_benchmarks.py* script will perform the following steps interactively.

Checkout the LLVM test suite in the folder *test_suite* via:
```
  git clone http://llvm.org/git/test-suite test_suite
```
or
```
  svn co http://llvm.org/svn/llvm-project/test-suite/trunk test_suite
```


The serial C implementation of the NAS benchmark suite (NPB3.3-SER-C) can be
found here [5]. However, since a registration is required to download the
benchmark suite, we provide the sources, including a modified configuration
file, to the resource folder (*resources/NPB3.3-SER-C*).


SPEC2000 and SPEC2006 have to be acquired separately. Once they are, they should
be placed in a folder which we denote as *${SPEC_SRC}*. This folder should contain
the following directory structure with the actual benchmarks residing in the
CINT/CFP/CPU folders:
```
  ${SPEC_SRC}/speccpu2000
  ${SPEC_SRC}/speccpu2000/benchspec
  ${SPEC_SRC}/speccpu2000/benchspec/CINT2000/
  ${SPEC_SRC}/speccpu2000/benchspec/CFP2000/
  ${SPEC_SRC}/speccpu2006
  ${SPEC_SRC}/speccpu2006/benchspec/
  ${SPEC_SRC}/speccpu2006/benchspec/CPU2006/
```
This particular arrangement will allow us to run the benchmarks together with
the LLVM test suite using the LNT tool that is introduced in the following.


Note: Use `docker cp <src_path> <container>:<dst_path>` to copy files/folder
(e.g., SPEC) from the host system to a docker container.


For the benchmarks we used the following versions, though other versions should
produce similar results.

  Benchmark        | Version
  -----------------|------------------------------------------------------------
  NPB              | SNU NPB 1.0.3, based on NPB3.3
  SPEC2000         | 1.3.1  (see "SPEC Fixes" below)
  SPEC2006         | 1.1    (see "SPEC Fixes" below)
  llvm-test-suite  | 19904bd55c45b136559a201e77319937a05348c5 (svn: r286278)


#### SPEC Fixes

The include `#include <cstddef>` is missing in:

`${SPEC_SRC}/speccpu2006/benchspec/CPU2006/447.dealII/src/include/lac/block_vector.h`.

The include `#include <cstring>` is missing in:

`${SPEC_SRC}/speccpu2000/benchspec/CINT2000/252.eon/src/ggRaster.cc`.



### Testing environments: LNT & NPB driver

We will use LNT to execute the LLVM test suite as well as SPEC. The installation
of LNT is described online [6]. If `virtualenv` version 2.X is installed, the *setup_lnt.py*
script can be used to set up LNT and a sandbox. The NPB benchmarks will be "run
in-place" using the `make suite` command..


### Testing:

The *runtests.py* script performs the following steps interactively. In general
we have three test drivers that can be executed separatly.

  - *NPB* for the SNU NPB benchmarks.
  - *LNT* for the LLVM test-suite.
  - *LNT* for the SPEC.


We will assume the following environment variables are initialized according to
their description. If the provided scripts were used, all configuration values
have been written to the *config.py* file located in the scripts directory. This
file is also read by the *runtest.py* script.

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
compile time options are configured in the *config/make.defs*. The benchmarks
and input sizes are defined in the *config/suite.def*. We recommend size **W**.

##### *LNT* driver

To use the LNT driver we first set up a sandbox environment:

```
source ${SANDBOX}/bin/activate
```

Then we can run the LNT "nt" test driver:

```
  lnt runtest nt --sandbox ${SANDBOX} \
                 --cc ${CLANG} \
                 --cxx ${CLANG}++ \
                 --test-suite ${TEST_SUITE} \
                 --build-threads ${JOBS} \
                 --test-externals ${SPEC_SRC} \
                 --cflag=-O3 \
                 --mllvm=-polly \
                 --mllvm=-polly-run-inliner \
                 --mllvm=-polly-invariant-load-hoisting=true \
                 --mllvm=-polly-unprofitable-scalar-accs=false \
                 --mllvm=-polly-allow-error-blocks=false
```

### Run options:

Option             | Description
-------------------|------------------------------------------------------------
-O3                |is required as polly does not run otherwise and some test do
                    not specify an optimization level or use a different one.
-mllvm             |will cause clang to pass the following option to llvm
-polly             |will enable the polly pipeline
-polly-run-inliner |will run a moderate inliner pass prior to the polly pipeline
-polly-invariant-load-hoisting=true  |Enable invariant load hoisting.
-polly-allow-error-blocks=false      |Disable the speculative expansion of SCoPs
                                      that often results in statically
                                      infeasible assumptions. Error blocks are a
                                      new feature that is not yet tuned and
                                      often too aggressive.
-polly-unprofitable-scalar-accs=false|Assume scalar accesses in statements are
                                      optimize able. This is generally true
                                      though the support in Polly was dropped at
                                      some point in favor of a replacement
                                      mechanism that is still not available.
                                      Therefore, Polly will currently not assume
                                      statements with scalar accesses are
                                      optimizeable while they generally are.



Experiments and data collection
-------------------------------


### Statistics and remarks:

Statistics are collected if clang is run with `-mllvm -stats`.
A debug build or release build with assertions is needed to do this.
The statistics will be printed to the standard error output or logs depending on
the benchmark. To collect them one can extract the statistics key (SK) from the
error output or logs using `grep` or a similar command. For the SK *"Number of
valid Scops"* the command would be
  `grep "Number of valid Scops"`
applied to the standard error stream or log file. To summarize the outputs of
multiple input files we provide the python script *summarize_stats.py*. It will
open all paths provided as arguments and summarize the numbers for the same SK.
A summarized statistic is printed on the standard output. Please note that the
script will skip lines that are not matched by the following regular expression:
  `"^[0-9]+ - .*"`
The last part (after the hyphen) is used as statistics key (SK). Depending on
the way all statistics are summarized it might therefor be required to add the
"--no-filename" option to grep.

The remarks system of clang/llvm allows to provide feedback to the user. It is
enabled for a specific pass using `-Rpass-analysis=<passname>` (<passname> should
be "polly-scops" for all experiments). The output always starts with the
filename, line and column number (if available) then the term "remark:" and the
actual message.


### Data collection and interpretation:

##### Number of loop nests analyzed [with assumptions, #S]:

* (a) feasible assumptions:
... SK `"Number of valid Scops"`

... Alternatively one could enable the remarks system [see below] and check if
    the following line is in the output:
    `remark: SCoP ends here.`

* (b) statically infeasible assumptions:
... SK `"Number of SCoPs with statically infeasible context"`

... Alternatively one could enable the remarks system and check if the
    following line is in the output:
      `remark: SCoP ends here but was dismissed.`


##### Number of loop nests analyzed without assumptions [without assumptions #S]:

  Run options: `-mllvm -polly-optimizer=none`

  Indirectly derived number. If the SCoP was valid and there is no optimizer
  running we will for sure generate code for it (no early exit). In the code
  generation we check if the runtime check condition is constant, thus if
  versioning would be needed. If not the SCoP does not require any assumptions.

  SK `"Number of valid Scops"` - SK `"Number of SCoPs required versioning."`

  Alternatively one could enable the remarks system and check if there are
  no assumption remarks between:
```
    remark: SCoP begins here.
    remark: SCoP ends here.
```


##### Number of executions of optimized loop nests [with assumptions #E]:

  Run options: `-mllvm -polly-codegen-emit-rtc-print`

  Numbers collected from the error stream (or logs) of the test cases.

*   (a) passing runtime checks:
... Extract lines containing `'__RTC: '` followed by a non zero number from the
    error stream (or logs), command:
      `grep -E '__RTC: [1-9]'`

*   (b) failing runtime checks:
... Extract lines containing `'__RTC: 0'` from the error stream (or logs),
    command:
      `grep '__RTC: 0'`


##### Number of optimized loop nests executed [with assumptions #D]:

  Similar to the former one (#E) but the result of the grep should be uniquely
  sorted with regards to the function name and region identifiers of the loop
  nest. Given the grep result from (#E) one can first drop the runtime check and
  overflow state result using:
    `sed -e 's|__RTC:.*||'`
  And then sort the lines uniquely using:
    `sort -u`


##### Number of non-trivial assumptions taken (a):

  Run options: `-mllvm -polly-remarks-minimal=false -Rpass-analysis=polly-scops`

  The assumptions taken are emitted to the standard error stream using the
  remarks system of clang/llvm. The assumptions evaluated here have the
  following names in the remarks output:

    Statistics Key    |  Paper Section
    ------------------|:-------------:
    "Invariant load"  |  4.1
    "No-overflows"    |  4.2
    "Finite loop"     |  4.3
    "Inbounds"        |  4.4
    "Delinearization" |  4.5
    "No-aliasing"     |  4.6

  To extract the first from the error stream (or logs) one can use the command:
    `grep 'Invariant load'`


##### Number of non-trivial assumptions taken that were not implied by propr ones (b):

  Run options: `-mllvm -polly-remarks-minimal=true -Rpass-analysis=polly-scops`

  Same as part (a) but with minimal remarks turned on. This will prevent the
  output of any already implied assumption.





Implementation notes:
--------------------

### Runtime Check Generation (Section 6)

#### Algorithm 1:

    The overflow checks for addition (and multiplication) are implemented in the
    `IslExprBuilder::createBinOp(...)` function [`IslExprBuilder.cpp`]. The
    overflow tracking is enabled in the `IslNodeBuilder::createRTC(...)`
    function [`IslNodeBuilder.cpp`] with the `ExprBuilder.setTrackOverflow(true)`
    call. As described in the paper one can either bail as soon as an overflow
    occurred or tack that fact and bail in the end. To avoid a complicated
    control flow graph the latter solution is implemented. The final overflow
    state is queried via `ExprBuilder.getOverflowState()` after the runtime
    check generation and combined with the runtime check result.

####  Algorithm 2:

    The parameter generation is implemented in the IslNodeBuilder


### Assumption computation


### Assumption simplification




[0] http://llvm.org/docs/GettingStarted.html

[1] http://clang.llvm.org/get_started.html

[2] http://polly.llvm.org/get_started.html

[3] http://polly.llvm.org/polly.sh

[4] http://llvm.org/docs/GettingStarted.html#requirements

[5] http://aces.snu.ac.kr/software/snu-npb/

[6] http://llvm.org/docs/lnt/quickstart.html

