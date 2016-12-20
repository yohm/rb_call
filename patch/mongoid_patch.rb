Mongoid::Relations::Proxy.class_eval do
  # Since Mongoid::Relations::Proxy undef method `to_msgpack_ext`,
  # we define to_msgpack_ext again so that rb_call works well.

  def to_msgpack_ext
    RbCall.store_object( self )
    MessagePack.pack( [self.class.to_s, self.object_id] )
  end
end

