require 'pp'
require 'msgpack'
require 'msgpack/rpc'

class RbCall
  def initialize
    @@variables = {}
  end

  def self.store_object( obj )
    key = obj.object_id
    if @@variables.has_key?( key )
      @@variables[key][1] += 1
    else
      @@variables[key] = [obj, 1]
    end
  end

  def self.find_object( obj_id )
    @@variables[obj_id][0]
  end

  private
  def send_impl( obj, method_name, args, kwargs)
    # See https://bugs.ruby-lang.org/issues/12022
    kwargs = kwargs.map {|k,v| [k.to_sym,v]}.to_h
    if kwargs.empty?
      ret = obj.send(method_name, *args)
    else
      ret = obj.send(method_name, *args, **kwargs)
    end
    ret
  end

  public
  def send_method( objid, method_name, args = [], kwargs = {})
    obj = self.class.find_object(objid)
    send_impl( obj, method_name, args, kwargs )
  end

  def del_object( objid )
    @@variables[objid][1] -= 1
    if @@variables[objid][1] == 0
      @@variables.delete(objid)
      #$stderr.puts "deleted #{objid} #{@@variables.inspect}"
    end
    nil
  end

  def get_kernel
    Kernel
  end
end

Object.class_eval do
  def self.from_msgpack_ext( data )
    rb_cls, obj_id = MessagePack.unpack( data )
    RbCall.find_object( obj_id )
  end

  def to_msgpack_ext
    RbCall.store_object( self )
    MessagePack.pack( [self.class.to_s, self.object_id] )
  end
end

MessagePack::DefaultFactory.register_type(40, Object)

if $0 == __FILE__
  svr = MessagePack::RPC::Server.new
  svr.listen('localhost', 0, RbCall.new)
  # a dirty hack to get the port number
  port = svr.instance_variable_get(:@listeners).first.instance_variable_get(:@lsock).instance_variable_get(:@listen_socket).addr[1]
  $stdout.puts port
  $stdout.flush
  svr.run
end

