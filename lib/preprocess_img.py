import numpy as np
import cv2

def reorderPts(pts):
    idx = np.lexsort((pts[:, 1], pts[:, 0]))  # 칼럼0 -> 칼럼1 순으로 정렬한 인덱스를 반환
    pts = pts[idx]  # x좌표로 정렬

    if pts[0, 1] > pts[1, 1]:
        pts[[0, 1]] = pts[[1, 0]]

    if pts[2, 1] < pts[3, 1]:
        pts[[2, 3]] = pts[[3, 2]]

    return pts

def affine(img):
    h, w, *_ = img.shape
    srcQuad = np.array([[0, 0], [0, 0], [0, 0], [0, 0]], np.float32)
    dstQuad = np.array([[0, 0], [0, h], [w, h], [w, 0]], np.float32)

    # 입력 영상 전처리
    src_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, src_bin = cv2.threshold(src_gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    # 외곽선 검출 및 명함 검출
    _, contours, _ = cv2.findContours(src_bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    #cpy = img.copy()
    max_area = 0
    for pts in contours:
        # 너무 작은 객체는 무시
        if cv2.contourArea(pts) < 1000:
            continue

        # 외곽선 근사화
        approx = cv2.approxPolyDP(pts, cv2.arcLength(pts, True) * 0.02, True)

        # 컨벡스가 아니고, 사각형이 아니면 무시
        if not cv2.isContourConvex(approx) or len(approx) != 4:
            continue
        if max_area < cv2.contourArea(approx):
            max_area = cv2.contourArea(approx)
        else:
            continue
        #cv2.polylines(cpy, [approx], True, (0, 255, 0), 2, cv2.LINE_AA)
        srcQuad = reorderPts(approx.reshape(4, 2).astype(np.float32))

    pers = cv2.getPerspectiveTransform(srcQuad, dstQuad)
    dst = cv2.warpPerspective(img, pers, (w, h))
    return dst

def refine(img):
    # dst = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # dst = cv2.medianBlur(dst,1)
    # # >> High Contrast
    # alpha = 1
    # dst = dst + (dst-170)*alpha
    dst = dilate()
    return dst

def dilate(ary, N, iterations):
    """Dilate using an NxN '+' sign shape. ary is np.uint8."""
    kernel = np.zeros((N, N), dtype=np.uint8)
    kernel[(N - 1) // 2, :] = 1
    dilated_image = cv2.dilate(ary / 255, kernel, iterations=iterations)

    kernel = np.zeros((N, N), dtype=np.uint8)
    kernel[:, (N - 1) // 2] = 1
    dilated_image = cv2.dilate(dilated_image, kernel, iterations=iterations)
    dilated_image = cv2.convertScaleAbs(dilated_image) #
    return dilated_image

def process(img):
    cv2.imshow('origin', cv2.resize(img, tuple(x // 4 for x in img.shape[:2][::-1])))
    img = affine(img)
    cv2.imshow('affined', cv2.resize(img, tuple(x // 4 for x in img.shape[:2][::-1])))
    img = refine(img)
    cv2.imshow('refined', cv2.resize(img, tuple(x//4 for x in img.shape[:2][::-1])))
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return img


#process(cv2.imread('../s0.png'))