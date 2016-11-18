FROM ubuntu:16.10

MAINTAINER Johannes Doerfert <doerfert@cs.uni-saarland.de>

RUN apt-get update && apt-get upgrade && apt-get install -y build-essential \
    cmake git git-svn kpartx libglib2.0-dev subversion zlib1g-dev flex libfdt1 \
    git libfdt-dev libpixman-1-0 libpixman-1-dev python-virtualenv ninja sed
    python-dev vim emacs
RUN git clone https://github.com/jdoerfert/CGO17_ArtifactEvaluation.git ~/ae && \
    cd ~/; python ./ae/scripts/setup_toolchain.py < ./ae/scripts/use_defaults

CMD python ~/ae/scripts/welcome.py; /bin/bash
