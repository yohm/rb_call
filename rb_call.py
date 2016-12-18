import subprocess
import time
import sys
import os
import msgpack
import msgpackrpc


class RubyObject():

    session = None

    @staticmethod
    def cast(obj):
        if isinstance( obj, msgpack.ExtType ):
            assert obj.code == 40
            rb_class, obj_id = msgpack.unpackb(obj.data, encoding='utf-8')
            return RubyObject( rb_class, obj_id )
        elif isinstance( obj, list ):
            return [ RubyObject.cast(x) for x in obj ]
        elif isinstance( obj, dict ):
            return { k:RubyObject.cast(v) for k,v in obj.items() }
        elif isinstance( obj, bytes ):
            return obj.decode('utf-8')
        else:
            return obj

    def __init__(self, rb_class, obj_id):
        self.rb_class = rb_class
        self.obj_id = obj_id

    def __del__(self):
        if self.session:
            self.session.del_object(self.obj_id)

    def __eq__(self, other):
        return isinstance(other,self.__class__) and self.obj_id == other.obj_id

    def __dir__(self):
        return self.send('public_methods')

    def __iter__(self):
        return self.send( "each" )

    def __str__(self):
        return self.send('to_s')

    def __repr__(self):
        return "RubyObject( %s, %s )" % (self.rb_class, self.obj_id)

    def __len__(self):
        return self.send( "size" )

    def __getattr__( self, attr ):
        def _method_missing(*args, **kwargs):
            return self.send( attr, *args, **kwargs )
        return _method_missing

    def __getitem__(self, index):
        return self.send('[]', index)

    def send(self, method, *args, **kwargs):
        try:
            obj = self.session.send(self.obj_id, method, *args, **kwargs )
            return self.cast(obj)
        except msgpackrpc.error.RPCError as ex:
            arg = self.cast( ex.args[0] )
            if isinstance( arg, RubyObject ):
                raise RubyException( arg.message(), arg ) from None
            else:
                raise ex

    # msgpack-rpc-python uses `to_msgpack` method
    def to_msgpack(self):
        return msgpack.ExtType(40, msgpack.packb( [self.rb_class, self.obj_id] ))

    def __next__(self):
        try:
            return self.send( "next" )
        except RubyException as ex:
            if ex.rb_exception.rb_class == 'StopIteration':
                raise StopIteration()
            else:
                raise

    def __call__(self, *args, **kwargs):
        if self.rb_class == 'Class':
            return self.send('new', *args, **kwargs)
        else:
            return self.send('call', *args, **kwargs)

class RubyException( Exception ):
    def __init__(self,message,rb_exception):
        self.args = (message,)
        self.rb_exception = rb_exception

class RubySession:

    def __enter__(self):
        server_rb = os.path.abspath(os.path.join(os.path.dirname(__file__), 'rb_call_server.rb'))
        self.proc = subprocess.Popen(['bundle','exec','ruby',server_rb], stdout=subprocess.PIPE, bufsize=0)
        port = int( self.proc.stdout.readline() )
        self.address = msgpackrpc.Address("localhost", port)
        self.client = msgpackrpc.Client(self.address, unpack_encoding='utf-8')
        assert self.client.call('echo', 1) == 1
        RubyObject.session = self
        return self

    def __exit__(self, type, value, traceback):
        RubyObject.session = None
        self.proc.terminate()

    def del_object(self, obj_id):
        return self.client.call('del_object', obj_id)

    def send(self, obj_id, method, *args, **kwargs):
        return self.client.call('send_method', obj_id, method, args, kwargs );

    def send_kernel(self, method, *args, **kwargs):
        return self.client.call('send_method_kernel', method, args, kwargs );

    def require(self, arg):
        return self.send_kernel('require', arg)

    def const(self, const_name):
        obj = self.send_kernel( "const_get", const_name )
        return RubyObject.cast(obj)

if __name__ == "__main__":
    with RubySession() as rb:
        rb.send_kernel("puts", "hello from python") # equivalent to `puts "hello from python"`
        rb.require("json")                          # `require "json"`
        JSON = rb.const('JSON')                     # get JSON class (This is a Ruby class.)
        print( JSON.dump( ['foo','bar','baz'] ) )   # call method against JSON class

        Dir = rb.const('Dir')                       # get another class `Dir`
        for f in Dir.glob('*'):                     # iterate over an object of Ruby
            print(f)                                # Array of Ruby is mapped to list of Python

        json_string = '{"a": 1, "b":2, "c":3}'
        parsed = JSON.load( json_string )           # parse JSON string using Ruby's JSON
        for k,v in parsed.items():                  # Hash of Ruby is mapped to dict of Python
            print(k, v)

        rb.require('./sample_class')                # load a Ruby library 'test.rb'
        MyClass = rb.const('MyClass')               # get a Class defined in 'test.rb'
        obj = MyClass('a')                          # create an instance of MyClass
        print( obj, repr(obj) )                     # when printing a Ruby object, `to_s` method is called
        print( obj.inspect() )                      # all Ruby methods are available.
        print( dir(obj) )                           # dir invokes `public_methods` in Ruby
        print( obj.m1(), obj.m2(1,2), obj.m3(3,b=4) )
                                                    # You can call Ruby methods with args. Keyword arguments are also available.

        proc = obj.m4('arg of proc')                # a Ruby method that returns a Proc
        print( "proc:", proc() )                    # calling proc

        try:
            obj.m2()                                # when an exception happens in Ruby, RubyException is raised
        except RubyException as ex:
            print( ex.args, repr(ex.rb_exception) ) # ex.args has a message from the exception object in Ruby.

        d = MyClass.cm5()                           # Hash and Array in Ruby correspond to Dictionary and List in Python
        print( d )                                  #   => {1: RubyObject, 2: [1, RubyObject]}

        e = MyClass.cm6()                           # Not only simple Array but an Enumerator is also supported
        for i in e:                                 # You can iterate using `for` syntax over an Enumerable
            print(i)

        obj2 = MyClass.cm7( obj )                   # you can pass a RubyObject as an argument
        print( obj2 == obj )                        # If two objects refers to the same objects, they are regarded as same.

