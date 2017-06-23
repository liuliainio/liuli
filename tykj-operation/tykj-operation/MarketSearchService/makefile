
dep-test:
	./release/deploy.sh dep ct-crawler-test ' '
dep:
	./release/deploy.sh dep ct-crawler2 ' '

install-deps:install-thrift
	sudo apt-get install python python-pip python-mysqldb

install-thrift:
	test -d tmp || mkdir -p tmp
	sudo apt-get install libboost-dev libboost-test-dev libboost-program-options-dev libevent-dev automake libtool flex bison pkg-config g++ libssl-dev 
	cd tmp &&\
		curl http://mirror.bit.edu.cn/apache/thrift/0.9.0/thrift-0.9.0.tar.gz | tar zx  &&\
		cd thrift-0.9.0/ &&\
		./configure &&\
		make &&\
		sudo make install
