FROM ubuntu:16.10

MAINTAINER Johannes Doerfert <doerfert@cs.uni-saarland.de>

RUN apt-get update && apt-get upgrade
RUN apt-get install -y build-essential cmake git git-svn kpartx libglib2.0-dev \
    subversion zlib1g-dev flex libfdt1 git libfdt-dev libpixman-1-0 \
    libpixman-1-dev python-virtualenv ninja sed python-dev vim emacs byacc flex\
    groff tclsh

RUN git clone https://github.com/jdoerfert/CGO17_ArtifactEvaluation.git /ae

CMD bash -c "python /ae/scripts/artifact_eval.py; bash"
