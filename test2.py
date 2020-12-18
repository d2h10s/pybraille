import glob
import os
import sys
import random
import cv2
import numpy as np
from lib.preprocess_img import process
from scipy.ndimage.filters import rank_filter
import pytesseract

def dilate(ary, N, iterations):
    kernel = np.zeros((N, N), dtype=np.uint8)
    kernel[(N - 1) // 2, :] = 1
    dilated_image = cv2.dilate(ary / 255, kernel, iterations=iterations)

    kernel = np.zeros((N, N), dtype=np.uint8)
    kernel[:, (N - 1) // 2] = 1
    dilated_image = cv2.dilate(dilated_image, kernel, iterations=iterations)
    dilated_image = cv2.convertScaleAbs(dilated_image) #
    cv2.imshow('a', cv2.resize(dilated_image, tuple(x // 4 for x in dilated_image.shape[:2][::-1])))
    return dilated_image


def props_for_contours(contours, ary):
    c_info = []
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        c_im = np.zeros(ary.shape)
        cv2.drawContours(c_im, [c], 0, 255, -1)
        c_info.append({
            'x1': x,
            'y1': y,
            'x2': x + w - 1,
            'y2': y + h - 1,
            'sum': np.sum(ary * (c_im > 0)) / 255
        })
    return c_info


def union_crops(crop1, crop2):
    """Union two (x1, y1, x2, y2) rects."""
    x11, y11, x21, y21 = crop1
    x12, y12, x22, y22 = crop2
    return min(x11, x12), min(y11, y12), max(x21, x22), max(y21, y22)


def intersect_crops(crop1, crop2):
    x11, y11, x21, y21 = crop1
    x12, y12, x22, y22 = crop2
    return max(x11, x12), max(y11, y12), min(x21, x22), min(y21, y22)


def crop_area(crop):
    x1, y1, x2, y2 = crop
    return max(0, x2 - x1) * max(0, y2 - y1)


def find_border_components(contours, ary):
    borders = []
    area = ary.shape[0] * ary.shape[1]
    for i, c in enumerate(contours):
        x, y, w, h = cv2.boundingRect(c)
        if w * h > 0.5 * area:
            borders.append((i, x, y, x + w - 1, y + h - 1))
    return borders


def angle_from_right(deg):
    return min(deg % 90, 90 - (deg % 90))


def remove_border(contour, ary):
    c_im = np.zeros(ary.shape)
    r = cv2.minAreaRect(contour)
    degs = r[2]
    if angle_from_right(degs) <= 10.0:
        box = cv2.boxPoints(r) #
        box = np.int0(box)
        cv2.drawContours(c_im, [box], 0, 255, -1)
        cv2.drawContours(c_im, [box], 0, 0, 4)
    else:
        x1, y1, x2, y2 = cv2.boundingRect(contour)
        cv2.rectangle(c_im, (x1, y1), (x2, y2), 255, -1) # (x2,y2)->0
        cv2.rectangle(c_im, (x1, y1), (x2, y2), 0, 4) # (x2,y2)->0

    return np.minimum(c_im, ary)


def find_components(edges, max_components=16):
    count = 21
    dilation = 5
    n = 1
    while count > 16:
        n += 1
        dilated_image = dilate(edges, N=3, iterations=n)
        _, contours, *_ = cv2.findContours(dilated_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        count = len(contours)
    return contours


def find_optimal_components_subset(contours, edges):
    c_info = props_for_contours(contours, edges)
    c_info.sort(key=lambda x: -x['sum'])
    total = np.sum(edges) / 255
    area = edges.shape[0] * edges.shape[1]

    c = c_info[0]
    del c_info[0]
    this_crop = c['x1'], c['y1'], c['x2'], c['y2']
    crop = this_crop
    covered_sum = c['sum']

    while covered_sum < total:
        changed = False
        recall = 1.0 * covered_sum / total
        prec = 1 - 1.0 * crop_area(crop) / area
        f1 = 2 * (prec * recall / (prec + recall))
        for i, c in enumerate(c_info):
            this_crop = c['x1'], c['y1'], c['x2'], c['y2']
            new_crop = union_crops(crop, this_crop)
            new_sum = covered_sum + c['sum']
            new_recall = 1.0 * new_sum / total
            new_prec = 1 - 1.0 * crop_area(new_crop) / area
            new_f1 = 2 * new_prec * new_recall / (new_prec + new_recall)

            remaining_frac = c['sum'] / (total - covered_sum)
            new_area_frac = 1.0 * crop_area(new_crop) / crop_area(crop) - 1
            if new_f1 > f1 or (
                    remaining_frac > 0.25 and new_area_frac < 0.15):
                print('%d %s -> %s / %s (%s), %s -> %s / %s (%s), %s -> %s' % (
                    i, covered_sum, new_sum, total, remaining_frac,
                    crop_area(crop), crop_area(new_crop), area, new_area_frac,
                    f1, new_f1))
                crop = new_crop
                covered_sum = new_sum
                del c_info[i]
                changed = True
                break

        if not changed:
            break

    return crop


def pad_crop(crop, contours, edges, border_contour, pad_px=15):
    bx1, by1, bx2, by2 = 0, 0, edges.shape[0], edges.shape[1]
    if border_contour is not None and len(border_contour) > 0:
        c = props_for_contours([border_contour], edges)[0]
        bx1, by1, bx2, by2 = c['x1'] + 5, c['y1'] + 5, c['x2'] - 5, c['y2'] - 5

    def crop_in_border(crop):
        x1, y1, x2, y2 = crop
        x1 = max(x1 - pad_px, bx1)
        y1 = max(y1 - pad_px, by1)
        x2 = min(x2 + pad_px, bx2)
        y2 = min(y2 + pad_px, by2)
        return crop

    crop = crop_in_border(crop)

    c_info = props_for_contours(contours, edges)
    changed = False
    for c in c_info:
        this_crop = c['x1'], c['y1'], c['x2'], c['y2']
        this_area = crop_area(this_crop)
        int_area = crop_area(intersect_crops(crop, this_crop))
        new_crop = crop_in_border(union_crops(crop, this_crop))
        if 0 < int_area < this_area and crop != new_crop:
            print('%s -> %s' % (str(crop), str(new_crop)))
            changed = True
            crop = new_crop

    if changed:
        return pad_crop(crop, contours, edges, border_contour, pad_px)
    else:
        return crop


def downscale_image(im, max_dim=2048):
    a, b, *_ = im.shape
    if max(a, b) <= max_dim:
        return 1.0, im

    scale = 1.0 * max_dim / max(a, b)
    dim = (int(a * scale), int(b * scale))
    im = cv2.cvtColor(np.float32(im), cv2.COLOR_RGB2GRAY)
    new_im = cv2.resize(im, dim, cv2.INTER_AREA) #
    return scale, new_im


def process_image(orig_im):
    cv2.imshow('origin', cv2.resize(orig_im, tuple(x//4 for x in orig_im.shape[:2][::-1])))
    orig_im = process(orig_im.copy())
    scale, im = downscale_image(orig_im)
    edges = cv2.Canny(np.uint8(im), 100, 200)

    # TODO: dilate image _before_ finding a border. This is crazy sensitive!
    contours, *_ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    borders = find_border_components(contours, edges)
    borders.sort(key=lambda ix1y1x2y2: (ix1y1x2y2[3] - ix1y1x2y2[1]) * (ix1y1x2y2[4] - ix1y1x2y2[2]))

    border_contour = None
    if len(borders):
        border_contour = contours[borders[0][0]]
        edges = remove_border(border_contour, edges)

    edges = 255 * (edges > 0).astype(np.uint8)

    # Remove ~1px borders using a rank filter.
    maxed_rows = rank_filter(edges, -5, size=(1, 20)) #
    maxed_cols = rank_filter(edges, -5, size=(20, 1)) #
    debordered = np.minimum(np.minimum(edges, maxed_rows), maxed_cols)
    edges = debordered

    contours = find_components(edges)
    if len(contours) == 0:
        return

    crop = find_optimal_components_subset(contours, edges)
    crop = pad_crop(crop, contours, edges, border_contour)

    crop = [int(x / scale) for x in crop]  # upscale to the original image size.
    rgb_im = cv2.cvtColor(orig_im, cv2.COLOR_BGR2RGB)
    x1, y1, x2, y2 = crop
    cropped = rgb_im[y1:y2, x1:x2]

    cv2.imshow('c', cv2.resize(cropped, tuple(x//4 for x in cropped.shape[:2][::-1])))
    cv2.waitKey(0)
    return cropped

img= process_image(cv2.imread('s2.jpg'))
#img = cv2.imread('s3.jpg')
text = pytesseract.image_to_string(img, lang='kor', config='--psm 1 -c preserve_interword_spaces=1 --oem 1')
#print(text)