import unittest
import rb_call

class TestRbCall(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print('setting up RubySession')
        cls.rb = rb_call.RubySession()

    def setUp(self):
        self.rb.require_relative('../sample_class')
        klass = self.rb.const('MyClass')
        self.obj = klass('a')

    def test_require(self):
        self.assertTrue( self.rb.require("json") )
        self.assertEqual( self.rb.const('JSON').to_s(), 'JSON' )

    def test_require_relative(self):
        self.assertEqual( self.rb.const('MyClass').to_s(), 'MyClass')

    def test_constructing_ruby_object(self):
        MyClass = self.rb.const('MyClass')
        obj = MyClass('a')
        self.assertIsInstance( obj, rb_call.RubyObject )
        self.assertTrue( obj.send('is_a?', MyClass) )

    def test_dir(self):
        methods = dir( self.rb.const('MyClass') )
        self.assertTrue( 'cm1' in methods )

    def test_instance_methods(self):
        self.assertEqual( self.obj.a(), "a" )
        self.assertEqual( self.obj.m1(), "m1" )
        self.assertEqual( self.obj.m2(1,2), "m2 1 2" )
        self.assertEqual( self.obj.m3(3,b=4), "m3 3 4" )

    def test_proc(self):
        proc = self.obj.m4('abcde')
        self.assertIsInstance( proc, rb_call.RubyObject )
        self.assertEqual( proc(), 'm4 abcde' )

    def test_exception(self):
        with self.assertRaises( rb_call.RubyException ) as cm:
            self.obj.m2()
        self.assertTrue( cm.exception.rb_exception.send('is_a?', self.rb.const('ArgumentError') ) )

    def test_hash_array(self):
        klass = self.rb.const('MyClass')
        ret = klass.cm5()  # {1: rbobj, 2: [1, rbobj] }
        self.assertIsInstance( ret, dict )
        self.assertIsInstance( ret[1], rb_call.RubyObject )
        self.assertIsInstance( ret[2], list )
        self.assertEqual( ret[2][0], 1 )

    def test_enumerable(self):
        e = self.rb.const('MyClass').cm6()
        a = [i for i in e ]
        self.assertEqual( a, ["5 is a multiple of 5", "10 is a multiple of 5"] )

    def test_equality(self):
        returned = self.rb.const('MyClass').cm7( self.obj )
        self.assertEqual( self.obj, returned )

