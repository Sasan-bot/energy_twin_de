import cv2
import numpy as np
from config import PIXEL_TO_SQM_COEFF, PANEL_WIDTH, PANEL_HEIGHT, PANEL_GAP

# --- CALIBRATION FOR MAPBOX ZOOM 19 (Standard Resolution) ---
# ساسان: این عدد را از 14 به 11 کاهش دادم تا پنل‌ها کوچک‌تر و واقعی‌تر شوند
PIXELS_PER_METER = 11.0 

def place_panels_on_roof(image_path, roof_contour):
    """
    Layer 1 (Visual Geometry): 
    Fits the maximum number of solar panels within the user-defined roof polygon.
    """
    img = cv2.imread(image_path)
    if img is None:
        print("❌ Error: Image file not found for panel placement.")
        return 0
    
    img_overlay = img.copy()
    
    # Calculate panel dimensions in pixels based on the calibrated scale
    px_w = int((PANEL_WIDTH + PANEL_GAP) * PIXELS_PER_METER)
    px_h = int((PANEL_HEIGHT + PANEL_GAP) * PIXELS_PER_METER)
    
    # Define bounding box to optimize the grid search area
    x_b, y_b, w_b, h_b = cv2.boundingRect(roof_contour)
    panel_count = 0
    
    # Iterate through the bounding box to place panels in a grid
    for y in range(y_b, y_b + h_b - px_h, px_h):
        for x in range(x_b, x_b + w_b - px_w, px_w):
            # Define 4 corners of a candidate panel
            corners = [(x, y), (x + px_w, y), (x, y + px_h), (x + px_w, y + px_h)]
            
            # Validation: All 4 corners must reside inside the drawn roof polygon
            if all(cv2.pointPolygonTest(roof_contour, p, False) >= 0 for p in corners):
                # Draw panel visualization: Yellow fill with black border
                cv2.rectangle(img_overlay, (x + 1, y + 1), (x + px_w - 1, y + px_h - 1), (0, 255, 255), -1)
                cv2.rectangle(img_overlay, (x + 1, y + 1), (x + px_w - 1, y + px_h - 1), (0, 0, 0), 1)
                panel_count += 1
    
    # Blend the overlay with the original satellite image
    final_view = cv2.addWeighted(img_overlay, 0.7, img, 0.3, 0)
    
    # Display the panel count on the UI window
    cv2.putText(final_view, f"Total Panels: {panel_count}", (20, 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
    
    cv2.imshow("Energy-Twin: Panel Placement Result", final_view)
    print(f"✅ Visual Analysis Complete: {panel_count} panels detected.")
    cv2.waitKey(1) 
    return panel_count

def detect_shadows(image_path, roof_contour):
    """
    Layer 2 (Risk Assessment): 
    Identifies shaded or obstructed areas within the roof perimeter using HSV thresholding.
    """
    img = cv2.imread(image_path)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Define HSV range for dark/shadowed pixels
    lower_shadow = np.array([0, 0, 0])
    upper_shadow = np.array([180, 255, 65]) 
    
    mask = cv2.inRange(hsv, lower_shadow, upper_shadow)
    
    # Create a binary mask for the specific roof area selected by the user
    roof_mask = np.zeros(mask.shape, dtype=np.uint8)
    cv2.drawContours(roof_mask, [roof_contour], -1, 255, -1)
    
    # Calculate shadow area by intersecting the shadow mask with the roof area
    shadow_pixels = cv2.bitwise_and(mask, roof_mask)
    
    # Convert pixel area to square meters using the squared scaling factor
    return np.sum(shadow_pixels > 0) / (PIXELS_PER_METER ** 2)

def select_roof_manually(image_path):
    """
    Main UI Component: 
    Enables interactive roof boundary definition via mouse clicks.
    """
    points = []
    img_orig = cv2.imread(image_path)
    if img_orig is None: 
        print("❌ Error: Could not load satellite image.")
        return 0, 0, 0
    
    # Apply detail enhancement for sharper roof edges
    enhanced_img = cv2.detailEnhance(img_orig, sigma_s=10, sigma_r=0.15)

    def mouse_event(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            points.append((x, y))
        elif event == cv2.EVENT_RBUTTONDOWN:
            if len(points) > 0: points.pop()
        
        # Draw interactive lines and points
        temp_img = enhanced_img.copy()
        for i, pt in enumerate(points):
            cv2.circle(temp_img, pt, 5, (0, 0, 255), -1)
            if i > 0:
                cv2.line(temp_img, points[i-1], points[i], (255, 255, 0), 2)
        cv2.imshow("Action: Pin Roof Corners", temp_img)

    cv2.imshow("Action: Pin Roof Corners", enhanced_img)
    cv2.setMouseCallback("Action: Pin Roof Corners", mouse_event)
    
    print("👉 INSTRUCTIONS:")
    print("1. Left-Click: Set roof corners")
    print("2. Right-Click: Undo last point")
    print("3. Press any keyboard key: Finalize selection")
    
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    if len(points) > 2:
        contour = np.array(points, dtype=np.int32)
        
        # Calculate derived metrics for the AI Engine
        area_sqm = cv2.contourArea(contour) / (PIXELS_PER_METER ** 2)
        
        # --- بخش دیباگ برای ساسان ---
        print("\n" + "🔍" * 10)
        print(f"DEBUG - Roof Area: {area_sqm:.2f} m2")
        print(f"DEBUG - Scale: {PIXELS_PER_METER} px/m")
        # ---------------------------

        shadow_sqm = detect_shadows(image_path, contour)
        panel_count = place_panels_on_roof(image_path, contour)
        
        return area_sqm, shadow_sqm, panel_count
    
    print("⚠️ Warning: Selection invalid. Minimum 3 points required.")
    return 0, 0, 0