import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

################################
wCam, hCam = 640, 480
################################
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0
detector = htm.handDetector(detectionCon=0.7)
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# Mendapatkan rentang volume
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 400
volPer = 0

while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    
    if len(lmList) != 0:
        # Mendapatkan koordinat ibu jari dan telunjuk
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        
        # Menggambar titik dan garis pada jari
        cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
        cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)
        
        # Menghitung panjang antara ibu jari dan telunjuk
        length = math.hypot(x2 - x1, y2 - y1)
        
        # Mengatur volume berdasarkan panjang tangan
        vol = np.interp(length, [50, 170], [minVol, maxVol])
        volBar = np.interp(length, [50, 170], [400, 150])
        volPer = np.interp(length, [50, 170], [0, 100])
        
        print(length)
        volume.SetMasterVolumeLevel(vol, None)
        
        if length <= 50:
            cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)

    # Menampilkan bar volume
    cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (255, 0, 0), cv2.FILLED)
    
    # Menampilkan persentase volume
    cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)
    
    # Menghitung dan menampilkan FPS
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)
    
    # Menampilkan frame
    cv2.imshow("Img", img)

    # Keluar dari aplikasi jika tombol ESC ditekan
    if cv2.waitKey(1) & 0xFF == 27:  # 27 adalah kode ASCII untuk tombol ESC
        print("ESC ditekan. Menutup aplikasi...")
        break

# Menutup kamera dan jendela setelah keluar
cap.release()
cv2.destroyAllWindows()