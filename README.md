# Discord Rich Presence for World of Warcraft
This particular repository was made for Mists of Pandaria(5.4.8), but it probably will work with other versions. If you will, you'd probably need to get a new list of zones with their IDs(`script/zones.txt`), because every version has it's own list of IDs. If you will use this on version <5.0.4, change the line 87 in `IPC.lua`.
I tried to make the installation as easy as possible, so I hope you won't face any problems.
## Requirements
- Python 3 for Windows, the [web-based installer](https://www.python.org/downloads/windows/) is OK. When it's finished installing, you will be asked if you want Python to be added to your $PATH, you have to say yes.
## Setup
[Download](https://github.com/AipNooBest/wow-discord-rpc/releases) the latest release and decompress it in the `Interface/AddOns/` folder. Then launch the `Installer.bat`. It will install everything is required, create `WoW.bat` and delete itself. From now on you'll need to run the game from this .bat file. You can make a shortcut and set an icon. You can't move `WoW.bat` anywhere else, it has to be launched from `AddOns/IPC/` directory.

**Note:** you have to play the game in borderless or windowed mode, full-screen is **not supported**!

Now you can launch the game through the .bat file and check if it works. It should look like this.

![image](https://user-images.githubusercontent.com/47401054/113831744-9d97fb00-9790-11eb-862e-8909c7cb6a53.png)

It is? Perfect! Now log into the world and check if you see some colorful array at the top left corner.

![image](https://user-images.githubusercontent.com/47401054/113832547-6249fc00-9791-11eb-8360-38b2f2568029.png)

If you see them, then AddOn is working properly. That means that you already should see the rich presence in your profile.

![image](https://user-images.githubusercontent.com/47401054/113833771-bacdc900-9792-11eb-8e19-672df784adb2.png)

That's it! Now you have a pleasant and informative Rich Presence in your Discord profile. It will update automatically as long as the script is kept running.

## LICENSE
Both the addon and the WoWPresence.py script are in the public domain.
The rpc.py file is from [this repo](https://github.com/suclearnub/python-discord-rpc) and it's [MIT licenced](https://raw.githubusercontent.com/wodim/wow-discord-rich-presence/master/script/rpc.py-LICENSE).
