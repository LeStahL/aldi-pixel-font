# aldi-pixel-font
Generate very small pixel fonts for PC-8k intros.

# Features
![image](https://user-images.githubusercontent.com/7655767/208553227-d00df40b-f2fb-4ca6-8951-11f156e2162b.png)

See the font in action: https://www.shadertoy.com/view/dtfGz7

# Building
* Download and install Python; add it and its script directory to your system PATH.
* Download and install CMake and git; add their binary dirs to your system PATH.
* Clone this repository, create an out-of-source build directory and cd there.
* `cmake [SOURCE_ROOT] -DCMAKE_INSTALL_PREFIX=install`
* `cmake --build . --config Release --target install`
* Enjoy.
