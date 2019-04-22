The goal of my project was to build an inexpensive, light quadrocopter that could be controlled from an iOS device. I’ve included all of the code and my presentation slides which contain photos of all the hardware.

The hardware portion of the project involves an array of low pass filters for filtering the output of the Arduino before it’s fed to the quad controller transmitter, and a quadcopter based on a multiwii, open source flight controller built by sun founder.

There are two software components to my final project. These both contain detailed comments. The first is an iOS control app found in ‘iOS controller.’ The main portion of the code is found in ViewController.m. This class handles user input and server communication.

The second is controller_interface, the program which runs on the Arduino and initializes the server, connects to the mini wifi router, and handles client input by writing out to the low pass filters and ultimately to the transmitter.

The quadcopter is controlled by four values, throttle, pitch, roll, and yaw. The app will display a connection indicator (spinning wheel) as it tries to connect to the control_interface server. On connection, you shake the iPhone to “unlock” the quadcopter (on startup the quadcopter is in a safe state), the safety-off light on the quad will turn blue. Then with the phone flat, tilt and twist to control the quad’s orientation, and swipe up and down to control the throttle. 
