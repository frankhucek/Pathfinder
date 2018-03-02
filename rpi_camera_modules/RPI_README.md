This Raspbian-OS system service is the replacement of
any GoPro modules for this project.

Hardware Requirements:
    - Raspberry Pi 3 Model B running Raspbian 9.3-Stretch OS
    - Official Raspberry Pi Camera module
    - 2.5A battery pack to power RPi in field

This service will work as follows:
    1) When switched on, the RPi will automatically start this service which initializes a connection to the network.
    2) Once connected to the network, the RPI will initialize the process of taking photographs for Pathfinder image data, which involves setting up the camera and initializing data directories with proper job information.
    3) After initialization and after the RPi has been properly set up, the service will being taking photos with a specified delay between captures.
    4) Each photo that is taken gets packaged up with relevant job information and will get posted to the awaiting service on the server.
    5) The server will receive job information data from each RPi in the field and assign that data to its proper location for image processing.