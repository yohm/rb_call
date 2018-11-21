if defined? Mongoid::Association::Proxy
  # Patch for Mongoid 7
  # Since Mongoid::Association::Proxy undef method `to_msgpack_ext`,
  # we define to_msgpack_ext again so that rb_call works well.
  Mongoid::Association::Proxy.class_eval do

    def to_msgpack_ext
      RbCall.store_object( self )
      MessagePack.pack( [self.class.to_s, self.object_id] )
    end
  end
end
if defined? Mongoid::Relations::Proxy
  # Patch for Mongoid 6
  # Since Mongoid::Relations::Proxy undef method `to_msgpack_ext`,
  # we define to_msgpack_ext again so that rb_call works well.
  Mongoid::Relations::Proxy.class_eval do

    def to_msgpack_ext
      RbCall.store_object( self )
      MessagePack.pack( [self.class.to_s, self.object_id] )
    end
  end
end
