# How to run Garuda Linux on Lenovo Yoga Pro 9 gen 10

This repo documents my experience with Lenovo Yoga Pro 9 laptop on Linux and tips to make it work.

Model: **16IAH10 (83L0002YCK)**

I plan to update this guide if I figure more things, this is always work in progress, if you have some more tips, let me know (by e-mail or using the "Discussions" feature).

## Distro

I'm using **Garuda Linux Dr460nized** gaming edition (KDE). I've tried the non-gaming edition, but the installer fails installing bootloader for some reason. I've tried live boot of Linux Mint, but even the touchpad does not work. Rest of the guide concerns my experience on Garuda (unless stated otherwise), you might achieve similar experience on other Arch-based distros.

## Devices

| Device | Status |
| --- | --- |
| [Keyboard](#keyboard) | 🟢 works |
| [Keyboard backlight adjustment](#keyboard-backlight) | 🟢 works |
| Touchpad | 🟢 works (on Garuda) |
| [Webcam](#webcam) | 🟢 works |
| Display | 🟢 works |
| [Touchscreen](#touchscreen) | 🟠 requires kernel patch |
| Brightness control | 🟢 works |
| [HDR + color management](#hdr-and-color-management) | 🟢 works (HDR requires fix) |
| [Switchable graphics](#switchable-graphics) | 🟠 pain |
| Nvidia GPU | 🟢 works |
| Power usage | 🟠 not great, not terrible (I'm getting around 16W when web-browsing) |
| SD card reader | 🟢 works |
| [Sound](#sound) | 🟢 works (after manual tweak) |
| Wifi | 🟢 works |
| Bluetooth | 🟢 works |

### Keyboard

Annoyingly, the keyboard doesn't have MENU key or right CONTROL, but it has the stupid copilot key. You can fix it like this:

* Install `keyd` package.
* `sudo systemctl enable --now keyd`
* Edit `/etc/keyd/default.conf`:

```
[ids]

*

[main]
f23+leftshift+leftmeta = overload(control, compose)
```

* `sudo keyd reload`

After this pressing the copilot key will behave as the MENU key (similar to right-click, you can for example use this to easily apply spell-checker corrections, or access other functions without a mouse). Holding the button will act as holding a control key, so you can press keyboard shortcuts comfortably.

Pressing Fn+Copilot shows contents of clipboard, which is nice behavior I don't intend to re-bind.

You can use `libinput debug-events --show-keycodes` to show what keys are being pressed. Use this to help you define your own bindings and to verify they work.

### Keyboard backlight

Backlight is adjustable in software. Under the "brightness icon" on top statusbar (where you control also screen brightness), you can choose if the backlight is "off", "low" or "bright". When you adjust the backlight using `Fn+space`, it cycles between 4 modes: "off", "high for 30s", "low", "high". The second mode does not display any notification on screen and in the brightness settings it looks like the keyboard backlight is off.

### Webcam

If the webcam shows just black image, verify that the hardware privacy switch located on right side of the laptop is in correct position.

### Touchscreen

By default there are no touchscreens detected. Kernel 6.17.9, does not work with the touchscreen.

You can install [patch](https://bugzilla.kernel.org/show_bug.cgi?id=220567) using [this](https://amini-allight.org/post/patching-the-arch-linux-kernel) tutorial. The process itself is straight-forward, but the patch is for older kernel version, so you might need to modify it. If you are not programmer, you should probably wait untill the patch is merged.

### HDR and color management

* Display reports it can support 1600nit brightness. (You can verify this using `cat /sys/class/drm/card0-eDP-2/edid | edid-decode`.)
* Out of the box, KDE does not detect wide color gamut or HDR support (`kscreen-doctor -o`). By default the screen appears to be using the whole color gamut of the panel (as the colors look oversaturated).

#### Simple workaround for oversaturated colors

In case you don't need HDR support:

You can go to KDE "Display Configuration" (right click on desktop) and choose `Color profile: Build-in`. This makes content way less oversaturated, it appears kwin uses RGB primaries from EDID data to convert colors in software. (I've roughly compared the color primaries reported with the advertised color-space capabilities, and it appears the values are correct. I didn't do any rigorous color calibration to verify this.)

#### HDR fix

Follow these steps to get proper HDR support.

* Get EDID data: `cat /sys/class/drm/card1-eDP-1/edid > original.bin`
* Fix EDID using [patch-edid.py](patch-edid.py).
* Include fixed EDID binary file in initramfs:
    * `sudo mkdir /lib/firmware/edid`
    * `sudo cp edid-patched-hdr.bin /lib/firmware/edid/edid-hdr.bin`
    * Create file `/etc/dracut.conf.d/edid-hdr.conf` with content `install_items+=" /lib/firmware/edid/edid-hdr.bin "`.
    * `sudo dracut-rebuild`
* Add following Linux boot option: `drm.edid_firmware=eDP-1:edid/edid-hdr.bin`
    * Option 1: Use "Boot tools" in "Garuda Rani" (the GUI assistant that helps you with setup) - add the option at the beginning of the "Kernel parameters" field.
    * Option 2:
        * Update `/etc/default/grub`. Add the option to `GRUB_CMDLINE_LINUX_DEFAULT`.
        * Run `sudo update-grub`.
    * Note: In case the display is named differently, make sure to replace `eDP-1` with correct name.
* Reboot.

(Thanks goes to *agnostic* from Arch Linux forums, as the fix is heavily inspired by their [post](https://bbs.archlinux.org/viewtopic.php?pid=2277349#p2277349).)

> [!WARNING]  
> After doing this fix, using HDMI does not work for me. I'm not sure if it's because of EDID fix, which I'm assuming should be applied only to internal display. Just disabling HDR didn't help. If you encounter this issue, you can temporarily remove the boot option and test again. If I figure out how to fix this, I'll update this guide.

#### How to watch HDR content

* Right-click on desktop -> Display settings:
    * Check the `Enable EDR` or `Enable HDR` setting. (Which one you see depends on if you applied [HDR fix](#hdr-fix).)
    * Verify that colour resolution is set to 10bit (the `Limit color resolution to` field).
    * If you enabled HDR, I recommend using the "Calibrate HDR Brightness" wizard:
        * First slider: Sets maximum creen brightness. I don't see reason to choose anything other than 1600 nits. At this brightness you should start to see fully white square. (Note that sometimes the calibration square glitched for me and became completely white only at the end of the slider. If that happens, it's probably a bug, just ignore it and set 1600.)
        * Second slider: Sets reference white or "**paper white**" and max SDR brightness. Note that this value (in nits) will be normally multiplied by your screen brightness. This (multiplied) "reference white" will be used as brightness of pure white in SDR content, and it'll be used to make HDR content brighter or darker. If you want to watch movies exactly as authors mastered them, you'll want this reference white to be set to 203nits per BT.2408 standard. (If you set it to this value, the display will behave exactly as on Windows, or as many televisions. Windows doesn't allow you to change brightness of HDR content.) The logic behind allowing you to change this value is that you might not be in reference viewing environment, so you might want to adjust the brightness to your liking. You can set this slider in calibration to 1015nits, and you'll know that if you ever want to get to 203nit reference, you just need to set brightness of the screen to 20% using keyboard shortcuts (without going into the calibration dialog). If you are in sunny day, you can crank the brightness up.
        * There is also checkbox, that I suppose enables the Windows behavior for the Windows apps.
        * Further reading:
           * [discussion](https://bugs.kde.org/show_bug.cgi?id=499934) (note that it got sometimes quite heated, it might not be worth reading all of it)
           * [Blog post](https://zamundaaa.github.io/colormanagement/2025/03/31/about-brightness.html) that discusses how the HDR in KDE works in more detail. I recommend reading this (although I don't agree with the sentiment that using reference brightness is completely useless).
* Install `vk-hdr-layer-kwin6-git` from AUR.
* Use app that supports HDR, for example:
    * **mpv**: `mpv --hwdec=vaapi --target-trc=pq"/path/to/video.mkv"`
        * `--hwdec=vaapi`: `mpv` uses this anyway, it just prints errors without this.
        * `--target-trc=pq`: For some reason by default `mpv` uses `pq` transfer function when display brightness is less than 100%, and `linear` otherwise. When using `linear` transfer, the image looks weirdly dithered. I'm not sure if it's bug in `mpv`. If you don't like this behavior, just force `pq` all the time.
        * These options might be useful, although in my experience modern versions of `mpv` have good defaults: `--vo=gpu-next --target-colorspace-hint=yes --gpu-api=vulkan --gpu-context=waylandvk`. You can click the menu button (`☰`) and display "Playback statistics" to see the video output being used.

> [!NOTE]
> If you are using EDR, you'll be likely limited to 1000nits brightness as that's the declared brightness in SDR mode.

I didn't try to play any HDR games, you can try looking at [this article](https://web.archive.org/web/20240703130440/https://planet.kde.org/xavers-blog-2023-12-18-an-update-on-hdr-and-color-management-in-kwin/), maybe it'll help, maybe it's outdated.

### Switchable graphics

By default the laptop is in hybrid mode, meaning both Intel and Nvidia GPUs are available. To switch modes, I've used [SuperGFX](https://wiki.archlinux.org/title/Supergfxctl) originally developed for Asus laptops.

* Install `supergfxctl` and `plasma6-applets-supergfxctl`.

This will allow you to switch between hybrid mode and integrated GPU. In hybrid mode, the internal GPU seems to suspend after a while of not being used, but often when I use apps like Firefox, it's active. Each GPU consumes around 5W when idle. I've noticed when using Firefox, the power usage of system goes up by 4W even when nothing is happening. The intel GPU seems to render like crazy (`sudo intel_gpu_top`). But this might happen only in hybrid mode, I haven't noticed this behavior in integrated-only mode. I haven't managed to use only discrete GPU, for that hardware mux would be needed, and I'm not sure if Lenovo has one.

Note that the switching is quite buggy. Sometimes it works without problem, sometimes it takes a while, sometimes you have to press the button twice, sometimes it logs you out... (The last one probably depends on supergfx config file.)

More experimentation is needed.

### Sound

Out of the box there are only tweeters and the sound is terrible. To fix this use script from [here](https://github.com/maximmaxim345/yoga_pro_9i_gen9_linux?tab=readme-ov-file#speakers). Note that the script for the older version of the laptop expected 3 i2c busses, this laptop shows 2. So you just need modify the script a bit and replace `3` with `2` at correct places.

<details>

<summary>Fixed script</summary>

```bash
#!/bin/bash

export TERM=linux
# Some distros don't have i2c-dev module loaded by default, so we load it manually

modprobe i2c-dev
# Function to find the correct I2C bus (third DesignWare adapter)
find_i2c_bus() {
    local adapter_description="Synopsys DesignWare I2C adapter"
    local dw_count=$(i2cdetect -l | grep -c "$adapter_description")
    if [ "$dw_count" -lt 2 ]; then
        echo "Error: Less than 2 DesignWare I2C adapters found." >&2
        return 1
    fi
    local bus_number=$(i2cdetect -l | grep "$adapter_description" | awk '{print $1}' | sed 's/i2c-//' | sed -n '2p')
    echo "$bus_number"
}
i2c_bus=$(find_i2c_bus)
if [ -z "$i2c_bus" ]; then
    echo "Error: Could not find the third DesignWare I2C bus for the audio IC." >&2
    exit 1
fi
echo "Using I2C bus: $i2c_bus"

laptop_model=$(</sys/class/dmi/id/product_name)
echo "Laptop model: $laptop_model"
if [[ "$laptop_model" == "83BY" ]]; then
    # For the 16IRP8 (see issue #17)
    i2c_addr=(0x39 0x38 0x3d 0x3b)
else
    i2c_addr=(0x3f 0x38)
fi

count=0
for value in "${i2c_addr[@]}"; do
    val=$((count % 2))
    i2cset -f -y "$i2c_bus" "$value" 0x00 0x00
    i2cset -f -y "$i2c_bus" "$value" 0x7f 0x00
    i2cset -f -y "$i2c_bus" "$value" 0x01 0x01
    i2cset -f -y "$i2c_bus" "$value" 0x0e 0xc4
    i2cset -f -y "$i2c_bus" "$value" 0x0f 0x40
    i2cset -f -y "$i2c_bus" "$value" 0x5c 0xd9
    i2cset -f -y "$i2c_bus" "$value" 0x60 0x10
    if [ $val -eq 0 ]; then
        i2cset -f -y "$i2c_bus" "$value" 0x0a 0x1e
    else
        i2cset -f -y "$i2c_bus" "$value" 0x0a 0x2e
    fi
    i2cset -f -y "$i2c_bus" "$value" 0x0d 0x01
    i2cset -f -y "$i2c_bus" "$value" 0x16 0x40
    i2cset -f -y "$i2c_bus" "$value" 0x00 0x01
    i2cset -f -y "$i2c_bus" "$value" 0x17 0xc8
    i2cset -f -y "$i2c_bus" "$value" 0x00 0x04
    i2cset -f -y "$i2c_bus" "$value" 0x30 0x00
    i2cset -f -y "$i2c_bus" "$value" 0x31 0x00
    i2cset -f -y "$i2c_bus" "$value" 0x32 0x00
    i2cset -f -y "$i2c_bus" "$value" 0x33 0x01

    i2cset -f -y "$i2c_bus" "$value" 0x00 0x08
    i2cset -f -y "$i2c_bus" "$value" 0x18 0x00
    i2cset -f -y "$i2c_bus" "$value" 0x19 0x00
    i2cset -f -y "$i2c_bus" "$value" 0x1a 0x00
    i2cset -f -y "$i2c_bus" "$value" 0x1b 0x00
    i2cset -f -y "$i2c_bus" "$value" 0x28 0x40
    i2cset -f -y "$i2c_bus" "$value" 0x29 0x00
    i2cset -f -y "$i2c_bus" "$value" 0x2a 0x00
    i2cset -f -y "$i2c_bus" "$value" 0x2b 0x00

    i2cset -f -y "$i2c_bus" "$value" 0x00 0x0a
    i2cset -f -y "$i2c_bus" "$value" 0x48 0x00
    i2cset -f -y "$i2c_bus" "$value" 0x49 0x00
    i2cset -f -y "$i2c_bus" "$value" 0x4a 0x00
    i2cset -f -y "$i2c_bus" "$value" 0x4b 0x00
    i2cset -f -y "$i2c_bus" "$value" 0x58 0x40
    i2cset -f -y "$i2c_bus" "$value" 0x59 0x00
    i2cset -f -y "$i2c_bus" "$value" 0x5a 0x00
    i2cset -f -y "$i2c_bus" "$value" 0x5b 0x00

    i2cset -f -y "$i2c_bus" "$value" 0x00 0x00
    i2cset -f -y "$i2c_bus" "$value" 0x02 0x00
    count=$((count + 1))
done

```

</details>

I haven't noticed the need to re-run this script after suspending, so instead of creating `systemd` service I just added it to startup applications and it fixes sound when KDE starts.

## Other issues

* Kwin randomly crashes.
    * Not sure if there is anything specific in my setup, or if the bug will manifest on this hardware.
    * Bug report: [link](https://bugs.kde.org/show_bug.cgi?id=511880). If you don't encounter the same bug and you have same configuration as me, please contact me. If you experience the same bug and have additional info, use the KDE bug tracker.
