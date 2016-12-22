class MyClass

  def initialize(a=nil)
    @a = a
  end

  def a
    @a
  end

  def m1
    "m1"
  end

  def m2(a,b)
    "m2 #{a} #{b}"
  end

  def m3(a, b:)
    "m3 #{a} #{b}"
  end

  def m4(a)
    Proc.new { "m4 #{a}" }
  end

  def self.cm1
    "cm1"
  end

  def self.cm2(a,b)
    "cm2 #{a} #{b}"
  end

  def self.cm3(a, b:)
    "cm3 #{a} #{b}"
  end

  def self.cm4
    [ 1, self.new ]
  end

  def self.cm5
    {1 => self.new, 2 => [1, self.new] }
  end

  def self.cm6
    enum = Enumerator.new{|y|
      (1..10).each{|i|
        y << "#{i} is a multiple of 5" if i % 5 == 0
      }
    }
  end

  def self.cm7(arg)
    arg
  end
end

if $0 == __FILE__
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
  puts("#{k}:#{v}")                               #        print(k, v)
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
end
