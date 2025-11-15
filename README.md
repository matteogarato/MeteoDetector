# 🛰️ Meteo Radar Distance Analyzer

This project processes meteorological radar images from the **ARPAV
Veneto** API, identifies yellow and red radar blobs, computes the
distance between them, and sends a weather alert email if adverse
weather appears to be approaching.

The script performs asynchronous image processing, filtering, blob
detection, distance calculation, visualization, GIF creation, and email
notification.

------------------------------------------------------------------------

## 📌 Features

### ✔️ Radar Image Retrieval

Automatically retrieves radar images from the ARPA Veneto REST API:

    https://api.arpa.veneto.it/REST/v1/radar_imgs_geo

### ✔️ Color-Based Radar Blob Extraction

Processes images to highlight yellow and red radar regions using: - LAB
color space conversion\
- CIE DeltaE color distance\
- Morphological closing\
- Mask creation and filtering

### ✔️ Blob Detection & Distance Calculation

-   Labels red/yellow blob regions\
-   Extracts centroid positions\
-   Computes Euclidean distance\
-   Generates annotated images with arrows and distance labels

### ✔️ GIF Export

Creates an animated GIF (`Meteo.gif`) from all processed frames.

### ✔️ Automated Email Alerts

If the sequence of distances indicates an approaching storm, the script
emails an alert including the generated GIF.

------------------------------------------------------------------------

## 📦 Requirements

Install dependencies:

``` bash
pip install -r requirements.txt
```

**Example `requirements.txt`:**

    numpy
    matplotlib
    Pillow
    requests
    scikit-image
    imageio
    asyncio
    python-dateutil

You will also need: - A Gmail account\
- An app-specific password\
- SMTP enabled

------------------------------------------------------------------------

## 🛠️ How It Works

### 1. Fetch Radar Frames

The API response is parsed and sorted chronologically.

### 2. Decode Base64 Radar Frames

Image data is decoded and converted to floating-point arrays for
processing.

### 3. Extract Colors

The code computes DeltaE color distances to isolate red and yellow radar
intensities.

### 4. Detect Blobs & Measure Distance

`skimage.measure.regionprops` identifies colored regions and extracts
centroids.\
The script then: - draws arrows between centroids\
- annotates distance\
- saves processed frames (`finalElaborationX.png`)

### 5. Evaluate Storm Proximity

If more than half of the distances trend downward → **send alert**.

### 6. Send Email Notification

Email includes: - Warning message\
- Attached `Meteo.gif`

------------------------------------------------------------------------

## 🚀 Usage

Run the script:

``` bash
python main.py
```

Console output example:

    Last run: 15/11/2025 14:32:10
    invio mail

------------------------------------------------------------------------

## 📧 Email Configuration

In the script locate:

``` python
send_from = "sender"
password = "gmailkey"
recipients = ["recipient1", "recipient2"]
```

For Gmail: 1. Enable **2-Step Verification**\
2. Create an **App Password**\
3. Use that password as `gmailkey`

------------------------------------------------------------------------

## 📂 Output Files

  --------------------------------------------------------------------------
  File                      Description
  ------------------------- ------------------------------------------------
  `finalElaboration0.png`   Processed radar image with blob detection and
                            annotations

  `Meteo.gif`               Animation of all frames

  Console output            Shows distances and alert status
  --------------------------------------------------------------------------

------------------------------------------------------------------------

## 📁 Suggested Project Structure

    project-folder/
    │
    ├── main.py
    ├── README.md
    ├── requirements.txt
    └── output/
        ├── finalElaboration0.png
        ├── finalElaboration1.png
        └── Meteo.gif

------------------------------------------------------------------------

## ⚙️ Adjusting Behavior

You can customize: - Color thresholds\
- DeltaE parameters\
- Morphological filtering\
- Alert conditions\
- Email recipients\
- Output image size and style

------------------------------------------------------------------------

## 🛡️ Disclaimer

This project is for **research and educational purposes** and is not a
certified weather forecasting tool.\
Use results responsibly and do not rely solely on this script for
safety-critical decisions.

------------------------------------------------------------------------

## 📜 License

MIT License --- you are free to use and modify the project.
