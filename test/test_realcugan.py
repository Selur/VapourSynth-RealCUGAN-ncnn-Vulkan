#!/usr/bin/env python3
"""Functional tests for the RealCUGAN ncnn Vulkan VapourSynth plugin.

Usage: python3 test/test_realcugan.py [path/to/librealcugannv.so]

Without an argument the plugin is expected to be autoloaded (e.g. from the
installed wheel) or to be found below site-packages/vapoursynth/plugins.
The models have to lie in a folder 'models' next to the plugin.

Without a Vulkan device the test checks loading, the models and the errors;
with one it also upscales a small clip.

Requires the vapoursynth Python module (R55 or newer).
"""
import glob
import os
import sys

import vapoursynth as vs

core = vs.core


def load_plugin(args):
    if args:
        core.std.LoadPlugin(args[0])
        return
    if hasattr(core, "rcnv"):
        return
    # Wheel layout: site-packages/vapoursynth/plugins/realcugan/<plugin> with models/ next to it
    plugin_dir = os.path.join(os.path.dirname(vs.__file__), "plugins")
    for ext in ("so", "dll", "dylib"):
        for path in glob.glob(os.path.join(plugin_dir, "**", "*realcugannv." + ext), recursive=True):
            core.std.LoadPlugin(path)
            return
    raise SystemExit("FAIL: rcnv plugin is neither autoloaded nor found below " + plugin_dir)


def check(cond, msg):
    if not cond:
        raise SystemExit("FAIL: " + msg)
    print("ok  ", msg)


def error_of(fn):
    try:
        fn()
    except vs.Error as e:
        return str(e).strip().splitlines()[-1]
    return None


def expect_error(fn, msg, contains=""):
    error = error_of(fn)
    check(error is not None and contains in error, "%s (%s)" % (msg, error))


def main():
    load_plugin(sys.argv[1:])
    check(hasattr(core, "rcnv"), "plugin loaded (namespace rcnv)")

    clip = core.std.BlankClip(width=96, height=64, format=vs.RGBS, length=2, color=[0.2, 0.5, 0.8])
    expect_error(lambda: core.rcnv.RealCUGAN(clip.resize.Point(format=vs.RGB24)), "integer input rejected", "32 bits float")
    expect_error(lambda: core.rcnv.RealCUGAN(clip, scale=5), "scale 5 rejected", "2 - 4 scale")
    expect_error(lambda: core.rcnv.RealCUGAN(clip, model=3), "model 3 rejected", "0 - 2")
    expect_error(lambda: core.rcnv.RealCUGAN(clip, model=0, scale=3), "models-nose with scale 3 rejected", "models-nose")
    # models-pro has no 4x model: the plugin looks for it next to itself and does not find it.
    expect_error(lambda: core.rcnv.RealCUGAN(clip, model=2, scale=4), "missing model reported", "model files can't be opened")

    gpu_error = error_of(lambda: core.rcnv.RealCUGAN(clip, gpu_id=0).get_frame(0))
    if gpu_error is not None and "gpu_id" in gpu_error:
        # The model files were found, otherwise the call would have failed before the GPU check.
        check(True, "no Vulkan device: models found, error '%s'" % gpu_error)
    else:
        check(gpu_error is None, "upscale on the GPU runs (%s)" % gpu_error)
        for scale in (2, 3, 4):
            out = core.rcnv.RealCUGAN(clip, scale=scale, gpu_id=0)
            f = out.get_frame(1)
            check((out.width, out.height, f.format.id) == (96 * scale, 64 * scale, vs.RGBS), "scale %d: %dx%d RGBS" % (scale, out.width, out.height))
        out = core.rcnv.RealCUGAN(clip, scale=2, tta=1, gpu_id=0)
        check(out.get_frame(0).width == 192, "tta after a non-tta instance in the same process")

    print("all tests passed")


if __name__ == "__main__":
    main()
