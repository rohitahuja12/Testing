import imageLib
import cv2
import detector
import math


"""
Visualize the results of the spot detection algorithm. 
Creates a set of annotated images.
This function should be called after calling the 'detect_intensities'
function. Its inputs are similar to the 'detect_intensities' function.
The 'spots_with_intensities' argument should be the results of call
to 'detect_intensities'.
"""
def visualize_spot_detection(
    images, 
    top_lefts_um, 
    bottom_rights_um, 
    spots_with_intensities,
    roi_size_um):


    def annotate(im, roi_size_px, spot_pts_px, spot_intensities):

        im = imageLib.imageToColorImage(im)
        im = imageLib.invert(im)
        im = cv2.applyColorMap(im, cv2.COLORMAP_JET)
        # add black point at pos ctl feature location (pre-shift)
        # cv2.circle(im, (posCtlPoint.x, posCtlPoint.y), 2, (0,0,0), 3)
        # add white circle around pos ctl spot
        # cv2.circle(im, (spotNearestPosControl['x'],spotNearestPosControl['y']), 40, (256,256,256), 3)
        halfGridUnit = int(roi_size_px / 2)
        for pt, intensity in zip(spot_pts_px, spot_intensities):
            cv2.circle(im, (pt[0], pt[1]), 2, (256,0,0), 3)
            cv2.rectangle( im, (pt[0]-halfGridUnit, pt[1]-halfGridUnit), (pt[0]+halfGridUnit, pt[1]+halfGridUnit), (0,0,256), 2)
            cv2.putText( 
                im, 
                str(math.floor(intensity)) if not math.isnan(intensity) else "NaN", 
                (pt[0]-halfGridUnit, pt[1]-halfGridUnit+20), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                0.75, 
                (256,0,0), 
                2)

        return im

    result_images = []
    for image, \
        (top_left_x, top_left_y), \
        (bottom_right_x, bottom_right_y) \
    in zip(images, top_lefts_um, bottom_rights_um,):

        xbounds_um = [top_left_x, bottom_right_x]
        ybounds_um = [top_left_y, bottom_right_y]

        bounded_spots_um = detector.get_spots_within_bounds(
            xbounds_um, 
            ybounds_um, 
            spots_with_intensities)

        bounded_spots_px = detector.convert_points_from_um_to_pixels(
            xbounds_um,
            ybounds_um,
            image,
            bounded_spots_um)
        
        [(roi_size_px, _)] = detector.convert_vectors_from_um_to_pixels(
            xbounds_um, ybounds_um, image, [(roi_size_um,0)])

        annotated_image = annotate(
            image, 
            roi_size_px, 
            bounded_spots_px,
            [s[-1] for s in bounded_spots_px])
        result_images.append(annotated_image)

    return result_images
