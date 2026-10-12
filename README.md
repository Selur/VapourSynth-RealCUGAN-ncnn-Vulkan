# VapourSynth-RealCUGAN-ncnn-Vulkan

[![Build Status](https://github.com/Kiyamou/VapourSynth-RealCUGAN-ncnn-Vulkan/workflows/CI/badge.svg)](https://github.com/Kiyamou/VapourSynth-RealCUGAN-ncnn-Vulkan/actions)

Real-CUGAN (Real Cascade U-Nets) super resolution for VapourSynth, based on [realcugan-ncnn-vulkan](https://github.com/nihui/realcugan-ncnn-vulkan). Some code is from [vapoursynth-waifu2x-ncnn-vulkan](https://github.com/Nlzy/vapoursynth-waifu2x-ncnn-vulkan).

Real-CUGAN is designed for anime. More information about Real-CUGAN can be found at [Real-CUGAN](https://github.com/bilibili/ailab/tree/main/Real-CUGAN).

## Usage

```python
core.rcnv.RealCUGAN(clip clip, [int scale, int noise, int model, 
                    int tilesize_x, int tilesize_y, int prepadding, 
                    bool tta, int syncgap, int gpu_id, int gpu_thread])
```
Models should be located in folder `models`, and folder `models` should be located in the same folder as dynamic link library.

### Parameter description

* ***clip***
  * Required parameter.
  * Clip to process.
  * Only 32bit RGB is supported.
* ***scale***
  * Optional parameter. *Default: 2*.
  * Upscale ratio.
  * Value range: 2, 3, 4.
* ***noise***
  * Optional parameter. *Default: 0*.
  * Denoise level.
  * Value range: -1, 0, 1, 2, 3.
    * Higher level means stronger denoise. `noise = -1` means no effect.
    * When `scale = 3` or `scale = 4`, `noise = 1` and `noise = 2` are not supported.
* ***model***
  * Optional parameter. *Default: 1*.
  * Select pre-trained model.
  * Value range: 0, 1, 2.
    * model = 0: models-nose. Only support `scale = 2` and `noise = 0`.
    * model = 1: models-se.
    * model = 2: models-pro.
  
  **The models and their supported upscale ratio and denoise level are shown in the list below.**

* ***tilesize_x***
  * Optional parameter. *Default: 0 (when `scale = 3` or `4` and `tta = True`, default: 100)*.
  * The tilesize for horizontal.
  * Value range: >= 32 or 0.
    * `tilesize_x = 0` means setting automatically according to the video size.
    * When `scale = 3` or `4` and `tta = True`, please set small value to make sure the plugin run normally.
* ***tilesize_y***
  * Optional parameter. *Default: same as tilesize_x*.
  * The tilesize for vertical.
  * Value range: >= 32 or 0.
    * `tilesize_y = 0` means setting automatically according to the video size.
    * When `scale = 3` or `4` and `tta = True`, please set small value to make sure the plugin run normally.
* ***prepadding***
  * Optional parameter. *Default: 18 (2x scale), 14 (3x scale), 19 (4x scale)*.
  * Pre-padding. If don't have experience for training model, please keep it.
* ***tta***
  * Optional parameter. *Default: False*.
  * TTA switch.
  * If true, quality will be improved, but speed will be significantly slower.
* ***syncgap***
  *  Optional parameter. *Default: 2*.
  *  Sync Gap. Reduce the impact of image blocking. It's a trade-off between speed and quality.
  *  Value range: 0, 1, 2, 3.
     * syncgap = 0: without process for sync gap (fast).
     * syncgap = 1: lossless (slow).
     * syncgap = 2: some loss for background, less loss for texture (middle).
     * syncgap = 3: more loss for background, less loss for texture (fast).

### Support list

|   Parameters   | scale = 2<br/>(model-nose) | scale = 2<br/>(model-se) | scale = 2<br/>(model-pro) | scale = 3<br/>(model-se) | scale = 3<br/>(model-pro) | scale = 4<br/>(model-se) |
| :------------: | :------------------------: | :----------------------: | :-----------------------: | :----------------------: | :-----------------------: | :----------------------: |
| **noise = -1** |            :x:             |    :heavy_check_mark:    |    :heavy_check_mark:     |    :heavy_check_mark:    |    :heavy_check_mark:     |    :heavy_check_mark:    |
| **noise = 0**  |     :heavy_check_mark:     |    :heavy_check_mark:    |    :heavy_check_mark:     |    :heavy_check_mark:    |    :heavy_check_mark:     |    :heavy_check_mark:    |
| **noise = 1**  |            :x:             |    :heavy_check_mark:    |            :x:            |           :x:            |            :x:            |           :x:            |
| **noise = 2**  |            :x:             |    :heavy_check_mark:    |            :x:            |           :x:            |            :x:            |           :x:            |
| **noise = 3**  |            :x:             |    :heavy_check_mark:    |    :heavy_check_mark:     |    :heavy_check_mark:    |    :heavy_check_mark:     |    :heavy_check_mark:    |

## VapourSynth API 4 and wheels

This fork targets the VapourSynth API 4 (R55 and newer, required since R80). The namespace `rcnv`, the function and its
arguments are unchanged. It builds against ncnn 20260526, which loads the Vulkan driver itself, so no Vulkan SDK is needed.

Each instance compiles its own shaders: with a shader cache shared by all instances, a `tta=True` instance after a
non-TTA one in the same process got the non-TTA shader and failed with `binding_count not match`.

Wheels for Windows x64, Linux x86_64 and macOS arm64 are attached to the GitHub releases. They contain the models of
[realcugan-ncnn-vulkan 20220728](https://github.com/nihui/realcugan-ncnn-vulkan/releases/tag/20220728):

```
pip install vapoursynth_realcugan_ncnn_vulkan-<version>-py3-none-<platform>.whl
```

The plugin and its `models` folder go to `site-packages/vapoursynth/plugins/realcugan`.

## Compilation

```
git clone --recursive https://github.com/Selur/VapourSynth-RealCUGAN-ncnn-Vulkan
cd VapourSynth-RealCUGAN-ncnn-Vulkan
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build build
```

The VapourSynth API 4 headers are vendored in `include/vapoursynth`. For the tests, put the `models-*` folders of the
realcugan-ncnn-vulkan release into `build/models` and run `python3 test/test_realcugan.py build/librealcugannv.so`.

## Reference Code

* realcugan-ncnn-vulkan: https://github.com/nihui/realcugan-ncnn-vulkan
* vapoursynth-waifu2x-ncnn-vulkan: https://github.com/Nlzy/vapoursynth-waifu2x-ncnn-vulkan
