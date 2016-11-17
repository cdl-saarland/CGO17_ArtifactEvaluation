FROM ubuntu:16.10

MAINTAINER Johannes Doerfert <doerfert@cs.uni-saarland.de>

RUN apt-get update && apt-get upgrade && apt-get install -y build-essential \
    cmake git git-svn kpartx libglib2.0-dev subversion zlib1g-dev flex libfdt1 \
    git libfdt-dev libpixman-1-0 libpixman-1-dev python-virtualenv ninja
RUN git clone https://github.com/jdoerfert/CGO17_ArtifactEvaluation.git ~/ae && \
    cd ~/; python ./ae/scripts/setup_toolchain.py < ./ae/scripts/use_defaults

CMD echo "Copy the SPEC{2000,2006} benchmarks into the docker image. \
This can be done using 'docker cp <src_path> <container>:<dst_path>' \
\n\nTo start automatic evaluation run: \
  python ~/ae/scripts/artifact_eval.py < ~/ae/scripts/use_defaults \
Alternatively, to start interactive set up and evaluation use: \
  python ~/ae/scripts/artifact_eval.py \
Finally, you can follow the guide in '~/ae/README.md' and/or execute \
the scripts in '~/ae/scripts/' manually."; /bin/bash
