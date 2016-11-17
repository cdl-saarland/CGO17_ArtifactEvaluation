FROM ubuntu:16.10

MAINTAINER Johannes Doerfert <doerfert@cs.uni-saarland.de>

RUN apt-get update
RUN apt-get upgrade
RUN apt-get install -y build-essential cmake git git-svn kpartx libglib2.0-dev
RUN apt-get install -y patch quilt subversion zlib1g-dev flex libfdt1
RUN apt-get install -y git libfdt-dev libpixman-1-0 libpixman-1-dev
RUN apt-get install -y python python-virtualenv ninja

RUN git clone https://github.com/jdoerfert/CGO17_ArtifactEvaluation.git ae
RUN git -C ae pull --rebase origin master
RUN python ae/scripts/artifact_eval.py < ae/scripts/use_defaults
