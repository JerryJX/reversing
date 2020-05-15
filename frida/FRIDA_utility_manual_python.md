Python section
========
1. JS Chinese support   
   Use codecs.open(scriptpath, "r", "utf-8") to open the file and read js.
   
2. Get the specified UID device   
```
device = frida.get_device_manager().get_device("094fdb0a0b0df7f8")
```
3. Get remote device
```
mgr = frida.get_device_manager()
device = mgr.add_remote_device("30.137.25.128:13355")
```
4. Start debugging process
```
pid = device.spawn([packename])
process = device.attach(pid)
script = process.create_script(jscode)
script.on('message', on_message)
script.load()
device.resume(pid)
```
5. Official example of python interacting with js
```
from __future__ import print_function
import frida
import sys

session = frida.attach("hello")
script = session.create_script("""
Interceptor.attach(ptr("%s"), {
    onEnter: function(args) {
        send(args[0].toString());
        var op = recv('input', function(value) {
            args[0] = ptr(value.payload);
        });
        op.wait();
    }
});
""" % int(sys.argv[1], 16))
def on_message(message, data):
    print(message)
    val = int(message['payload'], 16)
    script.post({'type': 'input', 'payload': str(val * 2)})
script.on('message', on_message)
script.load()
sys.stdin.read()
```
6. Load script from bytecode
```
  # -*- coding: utf-8 -*-
from __future__ import print_function

import frida


system_session = frida.attach(0)
bytecode = system_session.compile_script(name="bytecode-example", source="""\
'use strict';
rpc.exports = {
  listThreads: function () {
    return Process.enumerateThreadsSync();
  }
};
""")

session = frida.attach("Twitter")
script = session.create_script_from_bytes(bytecode)
script.load()
api = script.exports
# The list "threads here is the result of the automatic conversion of the hump naming method of listThreads, which is exported to python by the rpc exports function
print("api.list_threads() =>", api.list_threads())   
```
