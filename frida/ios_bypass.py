import frida 
import sys 




script = 'bypassing_jailbreak.js'

f = open(script, 'r')
s = f.read()

if __name__ == "__main__":
    #PACKAGE_NAME = "com.happypointcard.order.enterprise"
    PACKAGE_NAME = "com.kjbank.smart.public.pbanking"
    APP_NAME = "해피오더"
    device = frida.get_usb_device(1000)

    pid = device.spawn([PACKAGE_NAME])
    print ("[log] {} is starting. (pid : {})".format(PACKAGE_NAME, pid))

    session = device.attach(pid)
    device.resume(pid)

    script = session.create_script(s)
    script.load()
    device.resume(pid)
    sys.stdin.read()