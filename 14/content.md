# How to kill BadUSB - Software Section (Windows)

> BadUSB is to simulate human keyboard input, which can be prevented on the Software side. It just needs to block all keyboard input globally when the unexpected HID device is detected. This is especially for Windows OS.


## Introduction
Recall the concept of Software prevention, the flowchart is slightly adjusted. As shown in the figure, the software will record the IDs of HID devices currently connected at the start of the service and block global keyboard inputs when any unexpected HID device is detected. Users can unblock the keyboard lock with the GUI notifications.

![flowchart][1]

In order to implement the functions described above, there should be two parts of the software: GUI and service running in the background.

## GUI
There should be a GUI for users to interface with the background service. Additionally, it could operate the global keyboard lock according to the response from the service. Therefore, the GUI should mainly have three parts: Communication with background service, Graphical interface and keyboard lock. I want to make this end to be easy to be ported into multiple platforms as well as quick and convenient to be implemented so Python can be the best choice.

### Communication with background service
As the communication is between two separated processes in the same machine, ZeroMQ (a.k.a. ZMQ) is a good choice because it is lightweight, fast and easy to be implemented. With a simple command typing in the Command Prompt: `pip install pyzmq`, you are good to go. As seen in the graph below, it is shown that there are two kinds of messages to pass in this application: Service start-stop and HID detection trigger.

![messaging][2]

Here I use PUSH-PULL structure in ZMQ as it is the simplest to be implemented without the requirement of response or request in the beginning. Due to the special structure of the background service, there are two separate channels for Service start-stop and one channel for HID detection trigger. As I have used so many threads inside one of the processes made from `multiprocessing` module, the socket should be created individually inside each thread for thread safety.

There is a thread to keep receiving the trigger message from service because the receiving function of ZMQ will block the following operations.

### Graphical Interface
The Interface should be as minimal as possible. As this is especially for Windows OS, operating an icon on the system tray could be a good choice. It can be operated from system tray directly while some pop-up windows are created for notifications and unblocking the keyboard lock. [`pystray`][u1] is a cross-platform library in Python to make the program appear on the system tray as an icon with a context menu. [`plyer`][u2] module contains the `notification` class to create a system notification. [`tkinter`][u3] module can create pop-up windows with buttons to be clicked.

However, unlike `plyer.notification` can be called directly as a method, `pystray` and `tkinter` are both implemented as long-run applications. When one of the modules is working, the other operations are blocked. Therefore, [`multiprocessing`][u4] module is the best choice for that scenario. Two processes are created: one runs the main loop of `tkinter` and the other runs `pystray` main loop. The two processes communicate with `multiprocessing.Pipe`. `pystray` process sends the command according to the context operation, and the other receives the command with an individual thread and take action according to it.

### Keyboard Block
In Windows, there are specialised API to control keyboard operations. The first method to block the keyboard inputs is to inherit the [`BlockInput`][u5] from `Winuser.h`. However, as described in the API:
> Blocks keyboard and mouse input events from reaching applications.

This is only for applications but not for the global system. Additionally, the block will be passed when the user presses `Ctrl+Alt+Del`, which is easy to be simulated by BadUSB. Therefore, this method is not applicable.

There is a library called [`pyHook`][u6] that provides a callback to the **global* events for keyboard and mouse in Windows. I can hook an empty callback to the keyboard global event so that there is no action taken when all keys are pressed. However, `pyHook` module stops updating on Pypi after 2008 but there is [a resource from Laboratory for Fluorescence Dynamics][u7]. Additionally, `pyWinHook` is a maintained fork for this library. With [`pythoncom.PumpMessages`][u8], all the messages can be pumped for the current thread until a WM_QUIT message.[^1] That is the blocking logic.
To unblock the keyboard input, all the callback should be unhooked from the global input hook. `win32api.PostThreadMessage` can be used to post the WM_QUIT message to a particular thread with:
```
win32api.PostThreadMessage(thread_id, win32con.WM_QUIT, 0, 0)
```

There is a problem with the blocking logic. When it is called directly, all the following operations are blocked. This is because of `pythoncom.PumpMessages`. There is an alternative method [`pythoncom.PumpWaitingMessages`][u9] that does not block the following operations. However, all the inputs will be delayed rather than being blocked so this is not the solution for the problem. Actually, creating a thread that contains the unblocking method directly targeting to the main blocking thread will effectively solve the problem.

## Background Service
This part will run as a service in the background so this more focuses on System Programming. There are many system programming languages such as C, C++, Rust, C#, etc. Especially in C#, there is an application type called "Worker Service" that can run in the background, and being started and stopped in multiple platforms. Among all the platforms, Windows OS is the one C# supports the best. There are nugget packages that make the development process much easier with less effort than C++. Object-Oriented Programming makes the implementation at a higher level.

This service will send a trigger message to the GUI process when an unexpected HID is detected. In order to use the least resources of the machine, it will start detection only if a USB device is inserted. Additionally, it can start and stop detection with service control. Therefore, this application consists of two parts: frontend control (`Program.cs`) and backend worker (`Worker.cs`).

### Backend Control (`Worker.cs`)
Along with the creation of Worker Service in Visual Studio 2019, there is only `ExecuteAsync` with a while loop to check whether the cancellation is requested. In `BackgroundService` class, there are also `StartAsync` method that contains the logic executed after the worker is started and `StopAsync` method that contains the logic executed when the service stop is requested.

As the detection will be triggered only if the USB device is inserted into the machine, a callback can be added. A cross-platform nugget package [`Usb.Events`][u10] is used to detect the events of USB connection such as insertion, mounted, deleted, etc. A lambda function can be added to the event handler.

The detection is to compare the stored HID device list and the current one. In order to get a list of all HID devices, `HidSharp` package is used, which does not need any additional drivers installed on multiple platforms. Within that namespace, [`DeviceList.Local.GetHidDevices()`][u11] will get a full list or a specified list of connected HID devices.

However, for a single pair of Vender (VID) and Product (PID) IDs, there is a possibility that multiple devices are detected. Therefore, a storage class with essential methods should be implemented as well. It can store the information of unexpected HID device and detect whether the VID and PID have been detected in the same run (single insertion) with the counting of the total number of the HID devices. The count and device list storage will be cleared when a single run is completed. With such logic, it can be ensured that one device will only send one notification to the GUI.

In order to notify the GUI of unexpected HID devices, `NetMQ` package is used. It follows the opposite socket settings and the same port as the GUI. Please note that the ZMQ socket should be only created once as a global constant with `connect` method because the worker can be started and stopped dynamically according to the documentation:
> As a general rule use bind from the most stable points in your architecture, and use connect from dynamic components with volatile endpoints. For request/reply, the service provider might be the point where you bind and the client uses to connect. Just like plain old TCP.

The above are the main logic in the handler. The handler is assigned at the start of the service (inside `StartAsync`) in order to ensure the stored device list is those currently connected and stored for later use. Then inside `StartAsync`, the handler is added to the specified event handler.

As the detection and messaging happen inside the callback, there are no actions during the run `ExecuteAsync` method. Additionally, the "repeat-until-your-BackgroundService-is-stopped"-loop may block the service stop. Therefore, the `ExecuteAsync` method should be empty according to [my asked question in Stack Overflow][u12].

The `StopAsync` method will delete all the temporary values and clear the registered callback. The stored handler lambda function will be deleted from the USB event handler. The storage will be cleared. And finally, the GUI is notified that the worker is stopped.

### Frontend Control (`Program.cs`)
In the created template in VS2019, an `IHostBuilder` linked to the worker is created and called with `Run()` method in `Main`. What I want to achieve is to make it start and stop the service on request from the GUI.

With the help of `NetMQ`, I am able to create a pull socket to receive the request. When the start request is received, it will do the following sequence of actions:
1. Create a [`CancellationTokenSource`][u13] `source`.
2. Create a `CancellationToken token` from `source`.
3. Create and start a thread that will stop the worker on request with `token` as an input.
4. Start the worker with [`RunAsync`][u14] with `token` as an input.

According to the documentation, [`IHostBuilder.Build()`][u15] will create an [`IHost`][u16] instance. Among the methods, I have found a method [`RunAsync`][u14]. It is said that:
> Runs an application and returns a Task that only completes when the token is triggered or shutdown is triggered.

Therefore, I can set a token that can be cancelled manually. [`CancellationTokenSource`][u13] is able to create a token and be cancelled with the method [`Cancel`][u17]. It means that the worker will stop after the `Cancel` method is called. Inside thread logic, it will take the source as an input. When the stop is requested, it will cancel and dispose of the source.

With such logic, the worker can be started and stopped as a request without having any wasted resources.

## Packaging
This application should start two programs: GUI and the Worker Service. A batch file can be used to open both of them. The batch can be compressed into an executable file `.exe` with [Bat to EXE Converter][u20].

## Tests
Please note that I have joined the Windows Insider Programme on the Fast Ring. Until now, my Windows version is shown as below. During my development, the version has been updated more than once.

![winver][8]

The whole software is tested with two kinds of devices: normal keyboard and programmed MCU BadUSB device. The BadUSB emulator I use here is [Wio Terminal][u18] with [USB client keyboard feature][u19]. It successfully detects unexpected HID device and blocks the input. Before the detection and input blocking, the BadUSB device can enter 64 characters continuously (like keep pressing one key without releasing). The sequence of the software operation is followed by the pictures below.

Firstly, the software starts up and pop a notification.

![PS][3]

Then start the worker service.

![CM][9]

![SS][4]

When an unexpected HID device is connected, it will block the keyboard input and pop up the window as shown. (Now even you cannot type)

![UD][5]

After removing the device, click the button to release the keyboard lock.

![RL][6]

You can stop the service from the context menu.

![SD][7]

If you want to quit, please click "Quit Program". Or the exit will not be clean and you will suffer from repeated and unexpected warning if the program is started again.

## After that...
I will make the hardware solution for that, which is not limited to the platform. Then the Mac OS version software will be considered at first as it is another widely used consumer OS. Finally, Linux (Unix) version one will be developed.



[1]: https://cdn.jsdelivr.net/gh/onlya/blog_resources/14/1.png "Flowchart of this software section"
[2]: https://cdn.jsdelivr.net/gh/onlya/blog_resources/14/2.png "Messaging groups between GUI and Background Service processes"
[3]: https://cdn.jsdelivr.net/gh/onlya/blog_resources/14/3.jpg "Program Startup"
[4]: https://cdn.jsdelivr.net/gh/onlya/blog_resources/14/4.jpg "Service Starts"
[5]: https://cdn.jsdelivr.net/gh/onlya/blog_resources/14/5.jpg "Unexpected HID Device detected"
[6]: https://cdn.jsdelivr.net/gh/onlya/blog_resources/14/6.jpg "Unblock (Release) Keyboard lock"
[7]: https://cdn.jsdelivr.net/gh/onlya/blog_resources/14/7.jpg "Service stopped"
[8]: https://cdn.jsdelivr.net/gh/onlya/blog_resources/14/8.png "My current Windows OS version"
[9]: https://cdn.jsdelivr.net/gh/onlya/blog_resources/14/9.png "Context Menu"

[u1]:https://pystray.readthedocs.io/en/latest/usage.html
[u2]:https://plyer.readthedocs.io/en/latest/#plyer.facades.Notification
[u3]:https://docs.python.org/3.7/library/tkinter.html
[u4]:https://docs.python.org/3.7/library/multiprocessing.html
[u5]:https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-blockinput
[u6]:https://pypi.org/project/pyHook/
[u7]:https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyhook
[u8]:http://docs.activestate.com/activepython/3.4/pywin32/pythoncom__PumpMessages_meth.html
[u9]:http://docs.activestate.com/activepython/3.4/pywin32/pythoncom__PumpWaitingMessages_meth.html
[u10]:https://github.com/Jinjinov/Usb.Events
[u11]:https://docs.zer7.com/hidsharp/html/76d0678a-fad7-ff49-5e2d-c26cb0ac257e.htm
[u12]:https://stackoverflow.com/questions/63497181/start-and-stop-worker-service-repeatedly
[u13]:https://docs.microsoft.com/en-us/dotnet/api/system.threading.cancellationtokensource?view=netcore-3.1
[u14]:https://docs.microsoft.com/en-us/dotnet/api/microsoft.extensions.hosting.hostingabstractionshostextensions.runasync?view=dotnet-plat-ext-3.1#Microsoft_Extensions_Hosting_HostingAbstractionsHostExtensions_RunAsync_Microsoft_Extensions_Hosting_IHost_System_Threading_CancellationToken_
[u15]:https://docs.microsoft.com/en-us/dotnet/api/microsoft.extensions.hosting.ihostbuilder.build?view=dotnet-plat-ext-3.1#Microsoft_Extensions_Hosting_IHostBuilder_Build
[u16]:https://docs.microsoft.com/en-us/dotnet/api/microsoft.extensions.hosting.ihost?view=dotnet-plat-ext-3.1
[u17]:https://docs.microsoft.com/en-us/dotnet/api/system.threading.cancellationtokensource.cancel?view=netcore-3.1#System_Threading_CancellationTokenSource_Cancel
[u18]:https://www.seeedstudio.com/Wio-Terminal-p-4509.html
[u19]:https://wiki.seeedstudio.com/Wio-Terminal-USBCLIENT-Keyboard/
[u20]:https://www.battoexeconverter.com/

[^1]: `pythoncom`, `win32api` and `win32con` can be installed with `pip install pypiwin32`.