import cv2
import numpy as np
import os
import glob

# http://labs.eecs.tottori-u.ac.jp/sd/Member/oyamada/OpenCV/html/py_tutorials/py_calib3d/py_calibration/py_calibration.html

# チェッカーボードの両辺のマス目の数から1引いた値を設定する
CHECKERBOARD = (9, 8)

# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((CHECKERBOARD[0]*CHECKERBOARD[1], 3), np.float32)
objp[:, :2] = np.mgrid[:CHECKERBOARD[0], :CHECKERBOARD[1]].T.reshape(-1, 2)
# Arrays to store object points and image points from all the images.
objpoints = []  # 3d point in real world space
imgpoints = []  # 2d points in image plane.
images = glob.glob(
    './resources/checkerboards/*.tif')
for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Find the chess board corners
    ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, None)
    # If found, add object points, image points (after refining them)
    if ret == True:
        objpoints.append(objp)
        corners2 = cv2.cornerSubPix(
            gray, corners, (11, 11), (-1, -1), criteria)
        imgpoints.append(corners)
        # Draw and display the corners
        cv2.drawChessboardCorners(img, CHECKERBOARD, corners2, ret)

        # チェスボードの識別が確認したければimshowを呼ぶ
        # cv2.imshow('img', img)
        # cv2.waitKey(10)
cv2.destroyAllWindows()

ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
    objpoints, imgpoints, gray.shape[::-1], None, None)


target = cv2.imread(
    './resources/sample.tif')
h,  w = target.shape[:2]
newcameramtx, roi = cv2.getOptimalNewCameraMatrix(
    mtx, dist, (w, h), 1, (w, h))  # roiはregion-of-interest(関心領域)の略
# undistort
dst = cv2.undistort(target, mtx, dist, None, newcameramtx)

x, y, w, h = roi
dst = dst[y:y+h, x:x+w]

try:
    # resultディレクトリの作成を行う
    os.mkdir("./results")
except:
    pass
cv2.imwrite(
    './results/calibrated.png', dst)

