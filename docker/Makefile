VERSION=0.7.8-ubuntu

all: build

clean:
	if [ -d cador-build ]; then rm -rf cador-build; fi


build: build-cmd

build-cmd: clean
	mkdir cador-build
	cp -r ../cador cador-build
	cp ../setup.py ../requirements.txt ../test_requirements.txt cador-build
	docker build -t  cador:$(VERSION) .
