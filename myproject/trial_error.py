from flask import Flask, request, jsonify,render_template,Response
import cv2
import numpy as np
import mediapipe as mp
##import serial

app = Flask(__name__)


## ## Adjust the serial port to match Pico
## ser = serial.Serial('/dev/tty.usbmodem13101', 115200)
## ## Wait for the connection to establish
## time.sleep(2.0) 

# Initialize MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

# Assign the fingers IDs
tip_IDs =[4,8,12,16,20]

# Run the HTML code
@app.route('/')
def home():
    return render_template('trial_error.html')


@app.route('/process_frame', methods=['POST'])
def process_frame():
    # Receive the image frame from the browser camera
    file_bytes = request.data
    
    # Prepare the image for processing
    np_arr = np.frombuffer(file_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    
    if img is None:
        return jsonify({"error": "Invalid image"}), 400

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img)
    
    led_st=''
    lmlist = []
    previous_state = None
    

    if results.multi_hand_landmarks:
        # If hands are detected, return information about landmarks
        hand_data =[]
        for hand_landmarks in results.multi_hand_landmarks:
            myHand = results.multi_hand_landmarks[0]
            for hand_landmarks in results.multi_hand_landmarks:
                landmarks = [{'x': lm.x, 'y': lm.y, 'z': lm.z} for lm in hand_landmarks.landmark]
                hand_data.append(landmarks)
                for id,lm in enumerate(myHand.landmark):
                    #the information we need for hand and LED states:
                    h, w, c = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lmlist.append([id, cx, cy])
    else:
        return jsonify({"led_state": led_st,"hands": []})
    #After the hand is detected send the LED state back to the js code 
    if len(lmlist) != 0:
            fingers = []
            # Check if all fingers are up or down
            for id in range(0, 5):
                if lmlist[tip_IDs[id]][2] < lmlist[tip_IDs[id] - 2][2]:
                    fingers.append('1')  
                else:
                    fingers.append('0')
            if all(finger == '1' for finger in fingers):
                led_state = '0\n'
                led_st='ON'
            else:
                led_state = '1\n'
                led_st='OFF'

            ## ## Send action to the Pico
            ## current_state = led_state
            ## if current_state != previous_state:
            ##    print(f'Sending data to Pico: {current_state.strip()}')
            ##    ser.write(current_state.encode())
            ##    previous_state = current_state

    return jsonify({"led_state": led_st,"hands": hand_data})
## ser.close()

if __name__ == '__main__':
    app.run(debug=True)
