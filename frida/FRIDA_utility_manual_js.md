JS part
========
1. hook Android RegisterNatives   
    https://github.com/deathmemory/fridaRegstNtv
2. Send SendDataMessage via hook Android SMS   
```
function hook_sms() {
    var SmsManager = Java.use('android.telephony.SmsManager');
    SmsManager.sendDataMessage.implementation = function (
        destinationAddress, scAddress, destinationPort, data, sentIntent, deliveryIntent) {
        console.log("sendDataMessage destinationAddress: " + destinationAddress + " port: " + destinationPort);
        showStacks();
        this.sendDataMessage(destinationAddress, scAddress, destinationPort, data, sentIntent, deliveryIntent);
    }
}
```
3. Timed execution function   
```
//setTimeout is delayed once  
setTimeout(funcA, 15000);
//setInterval interval loop execution   
var id_ = setInterval(funcB, 15000);   
clearInterval(id_);    // termination   
```
4. bin array to string   
```
function bin2String(array) {
    if (null == array) {
        return "null";
    }
    var result = "";
    try {
        var String_java = Java.use('java.lang.String');
        result = String_java.$new(array);
    }
    catch (e) {
        dmLogout("== use bin2String_2 ==");
        result = bin2String_2(array);
    }

    return result;
}

function bin2String_2(array) {
    var result = "";
    try {
        var tmp = 0;
        for (var i = 0; i < array.length; i++) {
            tmp = parseInt(array[i]);
            if ( tmp == 0xc0
                || (tmp < 32 && tmp != 10)
                || tmp > 126 )  {
                return result;
            }  // Not visible, except for line breaks
            result += String.fromCharCode(parseInt(array[i].toString(2), 2));
        }
    }
    catch (e) {
        console.log(e);
    }
    return result;
}
```
5. Encapsulate output function to add thread ID and time   
```
function getFormatDate() {
    var date = new Date();
    var month = date.getMonth() + 1;
    var strDate = date.getDate();
    if (month >= 1 && month <= 9) {
        month = "0" + month;
    }
    if (strDate >= 0 && strDate <= 9) {
        strDate = "0" + strDate;
    }
    var currentDate = date.getFullYear() + "-" + month + "-" + strDate
            + " " + date.getHours() + ":" + date.getMinutes() + ":" + date.getSeconds();
    return currentDate;
}

function dmLogout(str) {
    var threadid = Process.getCurrentThreadId();
    console.log("["+threadid+"][" + getFormatDate() + "]" + str);
}
```
6. Print Android Java layer stack   
```
var showStacks = function () {
    Java.perform(function () {
        dmLogout(Java.use("android.util.Log").getStackTraceString(Java.use("java.lang.Exception").$new()));  // Print stack
    });
}
```
7. TracerPid fgets de debugging   
```
var anti_fgets = function () {
    dmLogout("anti_fgets");
    var fgetsPtr = Module.findExportByName("libc.so", "fgets");
    var fgets = new NativeFunction(fgetsPtr, 'pointer', ['pointer', 'int', 'pointer']);
    Interceptor.replace(fgetsPtr, new NativeCallback(function (buffer, size, fp) {
        var retval = fgets(buffer, size, fp);
        var bufstr = Memory.readUtf8String(buffer);
        if (bufstr.indexOf("TracerPid:") > -1) {
            Memory.writeUtf8String(buffer, "TracerPid:\t0");
            // dmLogout("tracerpid replaced: " + Memory.readUtf8String(buffer));
        }
        return retval;
    }, 'pointer', ['pointer', 'int', 'pointer']));
};
```
8. Read LR register traceability during Anti debugging   
```
var anti_antiDebug = function() {
    var funcPtr = null;

     funcPtr = Module.findExportByName("xxxx.so", "p57F7418DCD0C22CD8909F9B22F0991D3");

    dmLogout("anti_antiDebug " + funcPtr);
    Interceptor.replace(funcPtr, new NativeCallback(function (pathPtr, flags) {
        dmLogout("anti ddddddddddddddebug LR: " + this.context.lr);
        return 0;
    }, 'int', ['int', 'int']));
};
```
9. hook JNI API NewStringUTF   
```
function hook_native_newString() {
    var env = Java.vm.getEnv();
    var handlePointer = Memory.readPointer(env.handle);
    dmLogout("env handle: " + handlePointer);
    var NewStringUTFPtr = Memory.readPointer(handlePointer.add(0x29C));
    dmLogout("NewStringUTFPtr addr: " + NewStringUTFPtr);
    Interceptor.attach(NewStringUTFPtr, {
        onEnter: function (args) {
            ...
        }
    });
}
```
10. hook JNI API GetStringUTFChars   
```
function hook_native_GetStringUTFChars() {
    var env = Java.vm.getEnv();
    var handlePointer = Memory.readPointer(env.handle);
    dmLogout("env handle: " + handlePointer);
    var GetStringUTFCharsPtr = Memory.readPointer(handlePointer.add(0x2A4));
    dmLogout("GetStringUTFCharsPtr addr: " + GetStringUTFCharsPtr);
    Interceptor.attach(GetStringUTFCharsPtr, {
        onEnter: function (args) {
            var str = "";
            Java.perform(function () {
                str = Java.cast(args[1], Java.use('java.lang.String'));
            });
            dmLogout("GetStringUTFChars: " + str);
            if (str.indexOf("linkData:") > -1) {    // Set filter conditions
                dmLogout("========== found linkData LR: " + this.context.lr + "  ==========");
            }
        }
    });
};
```
11. Value of cycle output parameter   
```
Interceptor.attach(Module.findExportByName("libc.so", "strcat"), {
    onEnter: function (args) {
        for (var i = 0; i < args.length; i ++) {
            dmLogout("strcat args[" + i + "](" + ptr(args[i]) + "): " + Memory.readUtf8String(args[i]));
        }
    }
});
```
12. hook Android URI print stack   
```
var hook_uri = function() {
    // coord: (7520,0,19) | addr: Ljava/net/URI;->parseURI(Ljava/lang/String;Z)V | loc: ?
    var uri = Java.use('java.net.URI');
    uri.parseURI.implementation = function (a1, a2) {
        a1 = a1.replace("xxxx.com", "yyyy.com");

        dmLogout("uri: " + a1);
        showStacks();
        return this.parseURI(a1, a2);
    }
}
```
13. hook KXmlSerializer assembly content   
```
function hook_xml() {
    var xmlSerializer = Java.use('org.kxml2.io.KXmlSerializer');    // org.xmlpull.v1.XmlSerializer
    xmlSerializer.text.overload('java.lang.String').implementation = function (text) {
        dmLogout("xtext: " + text);
        if ("GPRS" == text) {
            dmLogout("======>>> found GPRS");
            showStacks();
        }
        return this.text(text);
    }
}
```
14. hook Android Log output   
```
function hook_log() {
    dmLogout(TAG, "do hook log");
    var Log = Java.use('android.util.Log');
    Log.v.overload('java.lang.String', 'java.lang.String').implementation = function (tag, content) {
        dmLogout(tag + " v", content);
    };
    Log.d.overload('java.lang.String', 'java.lang.String').implementation = function (tag, content) {
        dmLogout(tag + " d", content);
    };
    Log.w.overload('java.lang.String', 'java.lang.String').implementation = function (tag, content) {
        dmLogout(tag + " w", content);
    };
    Log.i.overload('java.lang.String', 'java.lang.String').implementation = function (tag, content) {
        dmLogout(tag + " i", content);
    };
    Log.e.overload('java.lang.String', 'java.lang.String').implementation = function (tag, content) {
        dmLogout(tag + " e", content);
    };
}
```
16. native active call   
```
var friendlyFunctionName = new NativeFunction(friendlyFunctionPtr, 'void', ['pointer', 'pointer']);
var returnValue = Memory.alloc(sizeOfLargeObject);
friendlyFunctionName(returnValue, param1);
```
