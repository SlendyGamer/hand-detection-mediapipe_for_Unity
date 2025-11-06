# Hand Detection Mediapipe

This project implements a hand detection system using the Mediapipe library and OpenCV. It captures video from the webcam, detects hand landmarks, and visualizes the hand movements by drawing vectors and calculating angles between them.

## Project Structure

```
src
├── __init__.py
├── main.py
├── hand_detection.py
├── hand_detection_gui.py
├── calculation_amplitude.py
└── vector_drawer.py
requirements.txt
README.md
```

## Installation

To set up the project, ensure you have Python installed on your machine. Then, install the required dependencies by running:

```
pip install -r requirements.txt
```

## Usage

To run the hand detection application, execute the following command:

```
python src/main.py
```

This will open a window displaying the webcam feed with hand landmarks and vectors drawn on it. Press the `Esc` key to exit the application.

## Dependencies

The project requires the following Python packages:

- `mediapipe`
- `opencv-python`

You can install these packages using the provided `requirements.txt` file.