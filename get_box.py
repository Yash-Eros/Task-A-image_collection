import cv2

# Load your averaged image
img = cv2.imread(r"D:\TASKA\indian_cultural_dataset\data\eros_frames\raw_frames\love_aaj_kal_2009_full_movie_hd_saif_ali_khan_deepika_padukone_superhit_romantic_film\frame_000006.jpg")

clone = img.copy()

points = []


def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"Clicked: ({x}, {y})")
        points.append((x, y))

        # draw point
        cv2.circle(img, (x, y), 5, (0, 0, 255), -1)
        cv2.imshow("image", img)


cv2.imshow("image", img)
cv2.setMouseCallback("image", click_event)

print("Click TOP-LEFT of watermark, then BOTTOM-RIGHT")
cv2.waitKey(0)
cv2.destroyAllWindows()

# Compute bounding box
if len(points) >= 2:
    (x1, y1), (x2, y2) = points[:2]

    x = min(x1, x2)
    y = min(y1, y2)
    w = abs(x2 - x1)
    h = abs(y2 - y1)

    print("\nBounding Box:")
    print(f"x={x}, y={y}, w={w}, h={h}")
