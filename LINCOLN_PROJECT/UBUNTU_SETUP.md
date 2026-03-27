# Quick guide for Ubuntu (clean fork)
Steps to reproduce the results using the custom scripts `my_norfair.py` and `batch_my_norfair.py`.

**Prerequisite:** Conda (Miniconda or Anaconda) must be installed before running the commands below.

## 1. Clone the fork

```bash
git clone https://github.com/<user>/<fork>.git
cd <fork>/<custom_scripts_folder>

# Example (in this case)
git clone https://github.com/MichelSanzPerez/Norfair.git
cd Norfair/LINCOLN_PROJECT
```

## 2. Prepare system dependencies

OpenCV with video support needs FFmpeg and GL; install:

```bash
sudo apt-get update
sudo apt-get install -y libgl1 libglib2.0-0
```

## 3. Create the Conda environment

Use the included `environment.yml` (pinned versions):

```bash
conda env create -f environment.yml
conda activate Norfair
```

## 4. Expected data structure

```text
<root>/
  Annotation/
    <scenario>_json_files/
      fisheye_images_12/cam_fish_left_ann.json
      fisheye_images_13/cam_fish_front_ann.json
      fisheye_images_14/cam_fish_right_ann.json
      output_images/cam_zed_rgb_ann.json
  Data/
    <scenario>_label/
      fisheye_images_12/ ...frames...
      fisheye_images_13/ ...frames...
      fisheye_images_14/ ...frames...
      output_images/     ...frames...
```

## 5. Run a single case

```bash
python my_norfair.py \
  --json /path/to/json/cam_fish_left_ann.json \
  --frames_dir /path/to/frames/fisheye_images_12 \
  --out_mot /path/to/results.txt \
  --out_video /path/to/tracking.mp4 \
  --save_frames_dir /path/to/results_frames \
  --distance_function iou \
  --distance_threshold 0.75 \
  --hit_counter_max 15 \
  --initialization_delay None \
  --box_thickness 2 \
  --id_offset 15
```

### Example

```bash
# With all parameters (if you want to try different parameter values)
python my_norfair.py \
  --json "/media/michel/DATASET/Annotation/footpath2_3walk_st_11_20_2024_json_files/fisheye_images_12/cam_fish_left_ann.json" \
  --frames_dir "/media/michel/DATASET/Data/footpath2_3walk_st_11_20_2024_label/fisheye_images_12" \
  --out_mot "/media/michel/DATASET/Results/Norfair/footpath2_3walk_st_11_20_2024_label/fisheye_images_12/results.txt" \
  --out_video "/media/michel/DATASET/Results/Norfair/footpath2_3walk_st_11_20_2024_label/fisheye_images_12/tracking.mp4" \
  --save_frames_dir "/media/michel/DATASET/Results/Norfair/footpath2_3walk_st_11_20_2024_label/fisheye_images_12/results_frames" \
  --distance_function iou \
  --distance_threshold 0.75 \
  --hit_counter_max 15 \
  --initialization_delay None \
  --box_thickness 2 \
  --id_offset 15
```

```bash
# With the default values
python my_norfair.py \
  --json "/media/michel/DATASET/Annotation/footpath2_3walk_st_11_20_2024_json_files/fisheye_images_12/cam_fish_left_ann.json" \
  --frames_dir "/media/michel/DATASET/Data/footpath2_3walk_st_11_20_2024_label/fisheye_images_12" \
  --out_mot "/media/michel/DATASET/Results/Norfair/footpath2_3walk_st_11_20_2024_label/fisheye_images_12/results.txt" \
  --out_video "/media/michel/DATASET/Results/Norfair/footpath2_3walk_st_11_20_2024_label/fisheye_images_12/tracking.mp4" \
  --save_frames_dir "/media/michel/DATASET/Results/Norfair/footpath2_3walk_st_11_20_2024_label/fisheye_images_12/results_frames"
```

## 6. Run all scenarios/cameras in batch

```bash
python batch_my_norfair.py \
  --root /path/to/root \
  --distance_function iou \
  --distance_threshold 0.75 \
  --hit_counter_max 15 \
  --initialization_delay None \
  --box_thickness 2 \
  --id_offset 15
```

### Examples

```bash
# With all parameters (if you want to try different parameter values)
python batch_my_norfair.py \
  --root "/media/michel/DATASET" \
  --distance_function iou \
  --distance_threshold 0.75 \
  --hit_counter_max 15 \
  --initialization_delay None \
  --box_thickness 2 \
  --id_offset 15
```

```bash
# With the default values
python batch_my_norfair.py \
  --root "/media/michel/DATASET"
```

Generates:

```text
<root>/Results/Norfair/<scenario_label>/<cam>/
  results.txt      # MOT format file
  tracking.mp4     # video with bounding boxes
  results_frames/   # PNG with bounding boxes
```

## 7. Reproducibility notes

- Pinned versions in `environment.yml`: Python 3.10, numpy 1.26, opencv-python 4.8.1.78, norfair 2.3.0.
- If you do not need display windows, you can use `opencv-python-headless` instead of `opencv-python` to reduce dependencies.
- Make sure you have enough disk space: `results_frames/` can be large for long sequences.

## 8. Quick troubleshooting

- `File not found`
  In batch mode: verify that the scenario name in `Annotation/` ends with `_json_files` and in `Data/` with `_label`; the mapping is automatic.

- `Conda: command not found`
  This usually means that Conda is either not installed or not initialized in the current shell.

  **Possible solutions:**
  - Check whether Conda is installed:
    ```bash
    conda --version
    ```

  * If Conda is not available, install **Miniconda** or **Anaconda** first.
  * If Conda is installed but still not recognized, initialize your shell:

    ```bash
    conda init bash
    ```

    Then close and reopen the terminal.

- `Errors caused by paths with spaces`
  If a path contains spaces and is not enclosed in quotes, the shell splits it into multiple arguments and the script may fail with errors such as `unrecognized arguments`.

  **Recommendation:** always wrap paths containing spaces in double quotes.
