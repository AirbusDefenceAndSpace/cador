FROM ubuntu:18.04

ARG ENV

RUN apt-get update --fix-missing && apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        curl \
        pkg-config \
        openjdk-8-jre-headless \
	    python3-dev \
	    python3-pip \
        && \
    apt-get clean

#RUN apt-get install software-properties-common && \
#    apt-add-repository ppa:jonathonf/python-3.6 && \
#    apt-get update && \
#    apt-get install python3.6 && \
#    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.5 1 && \
#    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.6 2

RUN pip3 install --upgrade pip
RUN pip3 install setuptools wheel
#RUN pip3 install requests-async==0.5.0
RUN pip3 install sanic-openapi==0.4.0

RUN export CLOUD_SDK_REPO="cloud-sdk-$(lsb_release -c -s)" && \
    echo "deb http://packages.cloud.google.com/apt $CLOUD_SDK_REPO main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list

RUN mkdir /tmp/cador
COPY cador-build /tmp/cador

RUN cd /tmp && cd cador && python3 setup.py bdist_wheel &&  python3 setup.py sdist \
	&& pip3 install dist/*cador*whl && cd /tmp && rm -rf cador

CMD python3 -c
