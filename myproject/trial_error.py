from flask import Flask, request, jsonify,render_template,Response
import cv2
import numpy as np
import mediapipe as mp

app = Flask(__name__)

# Initialize MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

tip_IDs =[4,8,12,16,20]

@app.route('/')
def home():
    return render_template('trial_error.html')

@app.route('/process_frame', methods=['POST'])
def process_frame():
    # Receive the image frame
    file_bytes = request.data
    
    # Convert the byte data to a numpy array
    np_arr = np.frombuffer(file_bytes, np.uint8)
    
    # Decode the image
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    
    previous_state = None
    led_st=''
    
    if img is None:
        return jsonify({"error": "Invalid image"}), 400

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img)

    lmlist = []

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
    #After the hand is detected send the LED state back to js 
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
    return jsonify({"led_state": led_st,"hands": hand_data})


if __name__ == '__main__':
    app.run(debug=True)
