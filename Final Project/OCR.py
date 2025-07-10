import easyocr
import cv2
from picamera2 import Picamera2
import pyttsx3
import time

# Initialize EasyOCR
reader = easyocr.Reader(['en'], gpu=False)

# TTS setup
engine = pyttsx3.init()
engine.setProperty('rate', 150)

# Camera setup
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (300, 300)})
picam2.configure(config)
picam2.start()
time.sleep(2)

spoken_text = ""
frame_count = 0
ocr_interval = 5  # Run OCR every 5 frames for speed

print("?? EasyOCR system running. Press 'q' to quit.")

try:
    while True:
        frame = picam2.capture_array()
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        frame_count += 1
        clean_text = ""

        if frame_count % ocr_interval == 0:
            h, w = frame_bgr.shape[:2]
            roi = frame_bgr[h // 4:h * 3 // 4, w // 4:w * 3 // 4]

            results = reader.readtext(roi)

            text_out = ""
            for (bbox, text, prob) in results:
                if prob > 0.5:
                    text_out += f"{text} "

            clean_text = text_out.strip()

            if clean_text and clean_text != spoken_text:
                print(f"?? Detected: {clean_text}")
                engine.say(clean_text)
                engine.runAndWait()
                spoken_text = clean_text

        # Overlay most recent result
        if spoken_text:
            cv2.putText(frame_bgr, spoken_text[:80], (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        cv2.imshow("?? EasyOCR Live Feed", frame_bgr)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("\n? Terminated by user.")

finally:
    picam2.stop()
    cv2.destroyAllWindows()
    print("? System shut down cleanly.")
