# Lenovo Yoga Pro 9 16IAH10 (83L0002YCK) Linux tips and tricks

This repo documents my experience with Lenovo Yoga Pro 9 laptop on Linux and tips to make it work.

I plan to update this guide if I figure more things, this is always work in progress, if you have some more tips, let me know.

## Distro

I'm using **Garuda Linux Dr460nized** gaming edition (KDE). I've tried the non-gaming edition, but the installer fails installing bootloader for some reason. I've tried live boot of Linux Mint, but even the touchpad does not work. Rest of the guide concerns my experience on Garuda (unless stated otherwise), you might achieve similar experience on other Arch-based distros.

## Devices

| Device | Status |
| --- | --- |
| Keyboard | 🟢 works |
| Touchpad | 🟢 works (on Garuda) |
| [Webcam](#webcam) | 🟢 works |
| Display | 🟢 works |
| [Touchscreen](#touchscreen) | 🔴 not detected |
| Brightness control | 🟢 works |
| [HDR + color management](#hdr-and-color-management) | 🟠 HDR support not detected, see details below |
| [Keyboard backlight adjustment](#keyboard-backlight) | 🟢 works |
| [Switchable graphics](#switchable-graphics) | 🟠 pain |
| Nvidia GPU | 🟢 works |
| Power usage | 🟠 not great, not terrible (I'm getting around 16W when web-browsing) |
| SD card reader | 🟢 works |
| [Sound](#sound) | 🟢 works (after manual tweak) |

### Webcam

If the webcam shows just black image, verify that the hardware switch located on right side of the laptop is in correct position.

### Touchscreen

I don't see any touchscreens in settings and I couldn't identify any device that could possibly indicate touchscreen. It's possible you need some magic I2C or ACPI calls to turn it on.

### HDR and color management

* Display reports it can support 1600nit brightness. (You can verify this using `cat /sys/class/drm/card0-eDP-2/edid | edid-decode`.)
* KDE does not detect wide color gamut or HDR support (`kscreen-doctor -o`).
* I have following error in boot logs, it might be related: `i915 0000:00:02.0: [drm] *ERROR* GT1: GSC proxy component didn't bind within the expected timeout`

My current assumption is that intel GPU should handle the display, but the driver is buggy and does not work with the display. By default the screen appears to be using it's full color gamut.

As a workaround, you can still go to KDE "Display Configuration" (right click on desktop) and choose `Color profile: Build-in`. This makes content way less oversaturated, it appears kwin uses RGB primaries from EDID data to convert colors in software. (I've roughly compared the color primaries reported with the advertised color-space capabilities, and it appears the values are correct. I didn't do any rigorous color calibration to verify this.)

To watch HDR movies, follow these steps:

* Check the `Enable EDR` setting.
* Limit color resolution to 10 bit per pixel. (The panel reports ability to have 12bit colors, but for some reason KDE allows only 10. During my experimentation with switching graphics on and off I did notice one time that this menu offered 12bit, but I could not reproduce it. It does not matter much as most of the content is 10bit anyway and the hardware limits the tones probably more.)
* Install `vk-hdr-layer-kwin6-git` from AUR.
* Use app that supports HDR, for example `ENABLE_HDR_WSI=1 mpv --vo=gpu-next --target-colorspace-hint --gpu-api=vulkan --gpu-context=wa
ylandvk "/path/to/video.mkv"`
* Max out your brightness. The brightness will be limited to brightness you set. (Note that if there is a dark scene in the movie, it might not appear to be getting brighter as you increase the brightness. But if you don't increase it, the bright scenes will be limited.)

Note that using this process you'll be limited to 1000nits SDR brightness. I've also noticed slight banding in dark colors, I'm not sure if it's limitation of the panel, or the setup is incorrect and you don't get full bit depth, or it's just limitation of the media.

I didn't try to play any HDR games, you can try looking at [this article](https://web.archive.org/web/20240703130440/https://planet.kde.org/xavers-blog-2023-12-18-an-update-on-hdr-and-color-management-in-kwin/), maybe it'll help, maybe it's outdated.

### Keyboard backlight

Backlight is adjustable in software. Under the "brightness icon" on top statusbar (where you control also screen brightness), you can choose if the backlight is "off", "low" or "bright". When you adjust the backlight using `Fn+space`, it cycles between 4 modes: "off", "high for 30s", "low", "high". The second mode does not display any notification on screen and in the brightness settings it looks like the keyboard backlight is off.

### Switchable graphics

By default the laptop is in hybrid mode, meaning both Intel and Nvidia GPUs are available. To switch modes, I've used [SuperGFX](https://wiki.archlinux.org/title/Supergfxctl) originally developed for Asus laptops.

* Install `supergfxctl` and `plasma6-applets-supergfxctl`.

This will allow you to switch between hybrid mode and integrated GPU. In hybrid mode, the internal GPU seems to suspend after a while of not being used, but often when I use apps like Firefox, it's active. Each GPU consumes around 5W when idle. I've noticed when using Firefox, the power usage of system goes up by 4W even when nothing is happening. The intel GPU seems to render like crazy (`sudo intel_gpu_top`). But this might happen only in hybrid mode, I haven't noticed this behavior in integrated-only mode. I haven't managed to use only discrete GPU, for that hardware mux would be needed, and I'm not sure if Lenovo has one.

Note that the switching is quite buggy. Sometimes it works without problem, sometimes it takes a while, sometimes you have to press the button twice, sometimes it logs you out... (The last one probably depends on supergfx config file.)

More experimentation is needed.

### Sound

Out of the box there are only tweeters and the sound is terrible. To fix this use script from [here](https://github.com/maximmaxim345/yoga_pro_9i_gen9_linux?tab=readme-ov-file#speakers). Note that the script for the older version of the laptop expected 3 i2c busses, this notebook shows 2. So you just need modify the script a bit and replace `3` with `2` at correct places.

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
