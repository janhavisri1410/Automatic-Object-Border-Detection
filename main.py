import cv2
from rembg import remove
import os

def read_image(image_path: str):
    '''
    The function reads an image from specified path and returns it.
    '''
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    return image

def show_image(image, image_window = "Temp"):
    cv2.imshow(image_window, image)

def select_roi(image):
    '''
    Selects an ROI from the input image and returns the
    ROI along with top-left coordinates.
    '''
    # Select ROI
    r = cv2.selectROI("Image", image)
    
    # Crop image
    cropped_image = image[int(r[1]):int(r[1]+r[3]),
                        int(r[0]):int(r[0]+r[2])]
    # return the cropeed image
    return cropped_image, (r[0], r[1])

def remove_bg_using_rembg(src_path, dst_path):
    '''
    Removes the background using rembg library.
    CLI command is executed to remove background.
    '''
    cmd = f"rembg i {src_path} {dst_path}"
    os.system(cmd)
    
def draw_outline(roi_fg):
    '''
    The function draws an outline on the given image.
    The input image must only be the foreground part.
    '''
    temp_image = roi_fg.copy()
    
    blur = cv2.GaussianBlur(temp_image, (29,29), 0)

    _ , thresholded = cv2.threshold(blur, 251 , 150,cv2.THRESH_BINARY )
    # cv2.imwrite("thresh.jpg", thresholded)
    
    edges = cv2.Canny(thresholded, 30, 60)
    # cv2.imwrite("edge.jpg", edges)
    contours, hierarchy= cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    cv2.drawContours(temp_image, contours, -1, (0,255,0),15)
 
    return temp_image

def place_overlay_on_input_img(input_img, overlay, roi_coord):
    '''
    The function places the overlay on the input image. roi_coord is used
    to place the overlay at particular position.
    '''
    x,y = roi_coord
    
    _overlay = overlay.copy()
    
    h1, w1 = _overlay.shape[:2]
    
    roi = input_img[y: y+h1, x:x + w1]
    
    gray = cv2.cvtColor(_overlay, cv2.COLOR_BGRA2GRAY)
    _, mask = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY_INV)
    
    
    img_bg = cv2.bitwise_and(roi, roi, mask = mask)
    
    dst = cv2.add(img_bg, _overlay)

    input_img[y: y+h1, x:x + w1] = dst
    

# {
# Driver Code starts
if __name__ == "__main__":
    # We'll create a main window where the original image
    # will be displayed
    cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Image", 700, 400)
    
    image_path = "TEST IMAGES/2.jpg"
        
    image = read_image(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
    
    h,w,c = image.shape
    font_scale = (w * h) / (1000 * 1000)
    
    while True:
        
        cv2.putText(image, "Select ROI", (int(w*0.04), int(h*0.07)), 
                    cv2.FONT_HERSHEY_PLAIN, font_scale, (255,0,0), 5)
        
        # roi image is saved so we can read it while removing the background
        roi, roi_coord = select_roi(image)
        cv2.imwrite("roi.jpg", roi)
        
        remove_bg_using_rembg("roi.jpg", "roi_fg.jpg")
        
        roi_fg = read_image("roi_fg.jpg")
        
        # Draw outline on the roi_fg image
        overlay = draw_outline(roi_fg)
        cv2.imwrite("overlay.jpg", overlay)
        
        place_overlay_on_input_img(image, overlay, roi_coord)
        cv2.imwrite("output.jpg", image)
        
        cv2.putText(image, "Press Q->Exit or C->Clear", (int(w*0.04), int(h*0.95)), 
                    cv2.FONT_HERSHEY_PLAIN, font_scale, (0,0,0), 5)
        
        show_image(image, "Image")
        
        # as long as the user presses "q" the window will be displaying
        k = cv2.waitKey(0) & 0xFF
        
        if k == ord('q'):        
            cv2.destroyAllWindows()
            break
        
        elif k == ord('c'):
            image = read_image(image_path)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
            show_image(image, "Image")

# } Driver Code ends