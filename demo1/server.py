from twisted.internet.defer import inlineCallbacks
from twisted.logger import Logger

from autobahn.twisted.util import sleep
from autobahn.twisted.wamp import ApplicationSession
from autobahn.wamp.exception import ApplicationError



class AppSession(ApplicationSession):

    log = Logger()

    @inlineCallbacks
    def onJoin(self, details):

        ## SUBSCRIBE to a topic and receive events
        ##
        def onTempChaged(msg):
            self.log.info("client event for 'onTempChaged' received: {msg}", msg=msg)

        sub = yield self.subscribe(onTempChaged, u'com.kx.onTempChaged')
        self.log.info("Server: subscribed to topic 'onTempChaged'")


        ## REGISTER a procedure for remote calling
        ##
        def s_add2(x, y):
            self.log.info("Server: add2() called with {x} and {y}", x=x, y=y)
            return x + y

        reg = yield self.register(s_add2, u'com.kx.s_add2')
        self.log.info("Server: procedure add2() registered")


        ## PUBLISH and CALL every second .. forever
        ##
        counter = 0
        while True:

            ## PUBLISH an event
            ##
            yield self.publish(u'com.kx.oncounter', counter)
            self.log.info("Server: published to 'oncounter' with counter {counter}",
                          counter=counter)
            counter += 1


            ## CALL a remote procedure
            ##
            try:
                res = yield self.call(u'com.kx.c_mul2', counter, 3)
                self.log.info("Server: mul2() called with result: {result}",
                              result=res)
            except ApplicationError as e:
                ## ignore errors due to the frontend not yet having
                ## registered the procedure we would like to call
                if e.error != u'wamp.error.no_such_procedure':
                    raise e


            yield sleep(120)