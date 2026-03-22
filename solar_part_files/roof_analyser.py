import cv2
import numpy as np
import config 
import os

def calculate_dynamic_scale():
    """
    Ensures PIXELS_PER_METER is derived from config to maintain Digital Twin integrity.
    """
    return 1.0 / np.sqrt(config.PIXEL_TO_SQM_COEFF)

def place_panels_on_roof(image_path, roof_contour):
    """
    Advanced Aligned Packing: Rotates the grid to match the roof's natural tilt.
    FIXED: Expanded scan range to ensure 100% coverage of the selected area.
    """
    img = cv2.imread(image_path)
    if img is None: return 0, None
    
    px_per_m = calculate_dynamic_scale()
    px_w = int((config.PANEL_WIDTH + config.PANEL_GAP) * px_per_m)
    px_h = int((config.PANEL_HEIGHT + config.PANEL_GAP) * px_per_m)
    
    # --- STEP 1: Find orientation and rotation matrices ---
    rect = cv2.minAreaRect(roof_contour.astype(np.float32))
    center_coords, dims, angle = rect[0], rect[1], rect[2]
    
    # Standardize angle logic
    if dims[0] < dims[1]:
        angle -= 90

    center = (int(center_coords[0]), int(center_coords[1]))
    rot_mat = cv2.getRotationMatrix2D(center, angle, 1.0)
    rev_mat = cv2.getRotationMatrix2D(center, -angle, 1.0)

    # --- STEP 2: Flatten the roof contour (Upright conversion) ---
    flat_contour = []
    for pt in roof_contour:
        curr_pt = pt[0] if isinstance(pt[0], (list, np.ndarray)) else pt
        p = np.array([curr_pt[0], curr_pt[1], 1], dtype='float32')
        new_p = rot_mat @ p
        flat_contour.append([new_p[0], new_p[1]])
        
    flat_contour = np.array(flat_contour, dtype=np.int32)

    # Get bounding box of the flattened roof
    x_b, y_b, w_b, h_b = cv2.boundingRect(flat_contour)
    
    img_overlay = img.copy()
    panel_count = 0

    # --- STEP 3: Expanded Dense Packing ---
    # We add a buffer to the range and ensure we cover the FULL height/width
    # This prevents the "early cutoff" seen in the previous version
    for y in range(y_b - px_h, y_b + h_b + px_h, px_h):
        for x in range(x_b - px_w, x_b + w_b + px_w, px_w):
            flat_corners = np.array([
                [x, y], [x + px_w, y], 
                [x + px_w, y + px_h], [x, y + px_h]
            ], dtype='float32')
            
            # Verify if panel is within the defined perimeter
            if all(cv2.pointPolygonTest(flat_contour, (float(p[0]), float(p[1])), False) >= 0 for p in flat_corners):
                # --- STEP 4: Inverse Transform back to original image ---
                real_corners = []
                for p in flat_corners:
                    orig_p = np.array([p[0], p[1], 1], dtype='float32')
                    back_p = rev_mat @ orig_p
                    real_corners.append([int(back_p[0]), int(back_p[1])])
                
                real_corners_np = np.array(real_corners, dtype=np.int32)
                cv2.fillPoly(img_overlay, [real_corners_np], (180, 255, 0))
                cv2.polylines(img_overlay, [real_corners_np], True, (0, 0, 0), 1)
                panel_count += 1

    final_view = cv2.addWeighted(img_overlay, 0.7, img, 0.3, 0)
    print(f"✅ Aligned Optimization: {panel_count} panels fitted parallel to roof edges.")
    return panel_count, final_view

def detect_shadows(image_path, roof_contour):
    """
    Environment Risk: Uses HSV thresholding to find obstructions.
    """
    img = cv2.imread(image_path)
    if img is None: return 0.0
    
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    px_per_m = calculate_dynamic_scale()
    
    lower_shadow = np.array([0, 0, 0])
    upper_shadow = np.array([180, 255, 75]) 
    
    mask = cv2.inRange(hsv, lower_shadow, upper_shadow)
    roof_mask = np.zeros(mask.shape[:2], dtype=np.uint8)
    cv2.drawContours(roof_mask, [roof_contour], -1, 255, -1)
    
    shadow_pixels = cv2.bitwise_and(mask, roof_mask)
    shadow_area_sqm = np.sum(shadow_pixels > 0) / (px_per_m ** 2)
    return round(shadow_area_sqm, 2)

def select_roof_manually(image_path):
    """
    Interactive UI: Define roof boundaries with Coordinate Snapping.
    """
    points = []
    img_orig = cv2.imread(image_path)
    if img_orig is None: return 0, 0, 0
    
    enhanced_img = cv2.detailEnhance(img_orig, sigma_s=15, sigma_r=0.15)
    px_per_m = calculate_dynamic_scale()
    window_name = "Energy-Twin: Define Roof Perimeter"

    def mouse_event(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            snapped_x = int(round(x / 5.0) * 5)
            snapped_y = int(round(y / 5.0) * 5)
            points.append((snapped_x, snapped_y))
        elif event == cv2.EVENT_RBUTTONDOWN:
            if points: points.pop()

    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
    cv2.setMouseCallback(window_name, mouse_event)

    while True:
        temp_img = enhanced_img.copy()
        for i, pt in enumerate(points):
            cv2.circle(temp_img, pt, 5, (0, 0, 255), -1)
            if i > 0: cv2.line(temp_img, points[i-1], points[i], (255, 255, 0), 2)
            if len(points) > 2 and i == len(points) - 1:
                cv2.line(temp_img, points[i], points[0], (0, 255, 255), 1)

        cv2.imshow(window_name, temp_img)
        if cv2.waitKey(1) & 0xFF == 13: break 

    cv2.destroyAllWindows()
    cv2.waitKey(1)
    
    if len(points) > 2:
        contour = np.array(points, dtype=np.int32)
        raw_area = cv2.contourArea(contour) / (px_per_m ** 2)
        actual_area_sqm = round(raw_area * 2) / 2 
        
        shadow_sqm = detect_shadows(image_path, contour)
        panel_count, result_img = place_panels_on_roof(image_path, contour)
        
        if result_img is not None:
            overlay_path = os.path.join("assets", "analyzed_roof.png")
            cv2.imwrite(overlay_path, result_img)
        
        return actual_area_sqm, shadow_sqm, panel_count
    
    return 0, 0, 0