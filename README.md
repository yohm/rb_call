# RbCall

[![Build Status](https://travis-ci.org/yohm/rb_call.svg?branch=master)](https://travis-ci.org/yohm/rb_call)

## What's this

A library to call Ruby methods from a Python script.
You can combine a Python script and Ruby libraries.

## Getting Started

Use Ruby 2.x.

Install the dependent gems as following.

```
gem install bundler
bundle
```

Use Python 3 and then install `msgpack-rpc-python` package.

```
pip install msgpack-rpc-python
```

Execute a sample script as follows.

```
python rb_call.py
```

## Usage

A sample code is the following.
Call `RubySession()` to invoke a Ruby process. The following sample demonstrate how to use RubySession object.

```py3
rb = RubySession()                            # Launch a Ruby process
rb.send_kernel("puts", "hello from python")   # equivalent to `puts "hello from python"`
rb.require("json")                            # `require "json"`
JSON = rb.const('JSON')                       # get JSON class (This is a Ruby class.)
print( JSON.dump( ['foo','bar','baz'] ) )     # call method against JSON class

Dir = rb.const('Dir')                         # get another class `Dir`
for f in Dir.glob('*'):                       # iterate over an object of Ruby
    print(f)                                  # Array of Ruby is mapped to list of Python

json_string = '{"a": 1, "b":2, "c":3}'
parsed = JSON.load( json_string )             # parse JSON string using Ruby's JSON
for k,v in parsed.items():                    # Hash of Ruby is mapped to dict of Python
    print(k, v)

rb.require('./sample_class')                  # load a Ruby library 'test.rb'
MyClass = rb.const('MyClass')                 # get a Class defined in 'test.rb'
obj = MyClass('a')                            # create an instance of MyClass
print( obj, repr(obj) )                       # when printing a Ruby object, `to_s` method is called
print( obj.inspect() )                        # all Ruby methods are available.
print( dir(obj) )                             # dir invokes `public_methods` in Ruby
print( obj.m1(), obj.m2(1,2), obj.m3(3,b=4) ) # You can call Ruby methods with args. Keyword arguments are also available.

proc = obj.m4('arg of proc')                  # a Ruby method that returns a Proc
print( "proc:", proc() )                      # calling proc

try:
    obj.m2()                                  # when an exception happens in Ruby, RubyException is raised
except RubyException as ex:
    print( ex.args, repr(ex.rb_exception) )   # ex.args has a message from the exception object in Ruby.

d = MyClass.cm5()                             # Hash and Array in Ruby correspond to Dictionary and List in Python
print( d )                                    #   => {1: RubyObject, 2: [1, RubyObject]}

e = MyClass.cm6()                             # Not only simple Array but an Enumerator is also supported
for i in e:                                   # You can iterate using `for` syntax over an Enumerable
    print(i)

obj2 = MyClass.cm7( obj )                     # you can pass a RubyObject as an argument
print( obj2 == obj )                          # If two objects refers to the same objects, they are regarded as same.
```

The code corresponds to the following Ruby code.

```rb
puts "hello from python"                  #    rb.send_kernel("puts", "hello from python")
require "json"                            #    rb.require("json")
                                          #    JSON = rb.const('JSON')
puts JSON.dump( ['foo','bar','baz'] )     #    print( JSON.dump( ['foo','bar','baz'] ) )
                                          #    Dir = rb.const('Dir')
Dir.glob('*').each do |f|                 #    for f in Dir.glob('*'):
  puts f                                  #        print(f)
end                                       #
json_string = '{"a": 1, "b":2, "c":3}'    #    json_string = '{"a": 1, "b":2, "c":3}'
parsed = JSON.load( json_string )         #    parsed = JSON.load( json_string )
parsed.each do |k,v|                      #    for k,v in parsed.items():
  puts(k,v)                               #        print(k, v)
end                                       #
require './sample_class'                  #    rb.require('./sample_class')
                                          #    MyClass = rb.const('MyClass')
obj = MyClass.new('a')                    #    obj = MyClass('a')
puts obj                                  #    print( obj, repr(obj) )
puts obj.inspect                          #    print( obj.inspect() )
p obj.public_methods                      #    print( dir(obj) )
puts obj.m1, obj.m2(1,2), obj.m3(3,b:4)   #    print( obj.m1(), obj.m2(1,2), obj.m3(3,b=4))
                                          #
                                          #
proc = obj.m4('arg of proc')              #    proc = obj.m4('arg of proc')
puts "proc: #{proc.call}"                 #    print( "proc:", proc() )
                                          #
begin                                     #    try:
  obj.m2                                  #        obj.m2()
rescue => ex                              #    except RubyException as ex:
  puts ex.to_s                            #        print( ex.args, repr(ex.rb_exception) )
end                                       #
d = MyClass.cm5                           #    d = MyClass.cm5()
puts d                                    #    print( d )
                                          #
e = MyClass.cm6                           #    e = MyClass.cm6()
e.each do |i|                             #    for i in e:
  puts i                                  #        print(i)
end                                       #
obj2 = MyClass.cm7(obj)                   #    obj2 = MyClass.cm7( obj )
puts(obj2 == obj)                         #    print( obj2 == obj )
```


An instance of RubySession, `rb`, has several methods.

- `send_kernel` calls the method against the Kernel object of Ruby.
- `require` corresponds to `require` in Ruby
- `require_relative(arg)` loads a Ruby file named ***arg*** relative to the requiring file's path.
- `const` returns a constant in Ruby such as Class object
    - If you get a class, you can use it as if it is a Python class.

## Limitations

- Python object can not be passed as an argument of Ruby methods.
    - Python function can not either be passed as a block of Ruby methods.
- Method calls against an instance of `RubyObject` is redirected to the corresponding object in Ruby. However, there are exceptions.
    - Some words can not be used as a method name in Python. For instance, `rb_obj.class()` or `rb_obj.in(...)`, `rb_obj.is_a?(...)` is not a valid call in Python, causing a syntax error.
    - To avoid this issue, use `#send` method: `rb_obj.send('class')`.
- If you undefine the method `to_msgpack_ext`, it is not serialized properly by MessagePack. Do not undefine this method.
    - In some library, however, some classes undefine most of the public methods for metaprogramming. In that case, re-define `to_msgpack_ext` method again to avoid the problem.
        - One of such library is "mongoid". If you are using "mongoid", require "patch/mongoid_patch" after you required "mongoid" in your code.

## Test

To run the test,

```
python -m unittest discover -v
```


## License

The MIT License (MIT)
Copyright (c) 2016 RIKEN AICS

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

