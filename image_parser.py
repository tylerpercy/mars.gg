from PIL import Image, ImageFilter
import cv2 as cv
import numpy as np
import easyocr
import warnings

warnings.filterwarnings("ignore", category=UserWarning) 

all_player_stats = []

def main():

    print("\n\nLoading player stats! Please do not close the window.\n\n")

    for iter in range (-1, 3):
        current_player_stats = []
        image_black_and_white('test2.png')
        crop_full_image('output.png', iter)

        name = crop_player_name('output_crop.png')
        if name == 'X':
            continue
        else:
            current_player_stats.append(name)

        text_value = crop_player_stat('output_crop.png', 300, 420)
        current_player_stats.append(text_value)

        
        for i in range(0, 6):
            text_value = crop_player_stat('output_crop.png', (540 + (270 * i)), (690 + (270 * i)))
            current_player_stats.append(text_value)
        
        all_player_stats.append(current_player_stats)

    print(all_player_stats)

def image_black_and_white(image):
    img = Image.open(image)
    data = np.array(img)

    converted = np.where(data == 255, 0, 255)

    img = Image.fromarray(converted.astype('uint8'))
    img.save('output.png')

def add_image_filters(input_image, output_image, scale):

    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])

    img = cv.imread(input_image, cv.IMREAD_GRAYSCALE)

    scale_percent = scale
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)
  
    # resize image
    img = cv.resize(img, dim, interpolation = cv.INTER_AREA)

    blurred = cv.GaussianBlur(img, (3, 3), 0)
    thresh = cv.threshold(blurred, 0, 255, cv.THRESH_BINARY)[1]
    
    # apply morphology
    kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (5,5))
    morph = cv.morphologyEx(thresh, cv.MORPH_OPEN, kernel)

    # find contours - write black over all small contours
    letter = morph.copy()
    cntrs = cv.findContours(morph, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    cntrs = cntrs[0] if len(cntrs) == 2 else cntrs[1]
    for c in cntrs:
        area = cv.contourArea(c)
        if area < 100:
            cv.drawContours(letter,[c],0,(0,0,0),-1)

    cv.imwrite(output_image, img)

    img = Image.open(output_image)
    img = img.filter(ImageFilter.ModeFilter(size=2))
    '''
    img = img.filter(ImageFilter.BLUR) 
    img = img.filter(ImageFilter.CONTOUR) 
    img = img.filter(ImageFilter.DETAIL) 
    img = img.filter(ImageFilter.EDGE_ENHANCE) 
    img = img.filter(ImageFilter.EDGE_ENHANCE_MORE) 
    img = img.filter(ImageFilter.EMBOSS) 
    img = img.filter(ImageFilter.FIND_EDGES) 
    img = img.filter(ImageFilter.SMOOTH) 
    img = img.filter(ImageFilter.SMOOTH_MORE) 
    img = img.filter(ImageFilter.SHARPEN)
    '''
    img.save(output_image)


def crop_full_image(image, iter):

    VERTICAL_OFFSET = 150

    img = Image.open(image)
    left = 157
    top =  457  + (iter * VERTICAL_OFFSET)
    right = 2220
    bottom = 625  + (iter * VERTICAL_OFFSET)

    img = img.crop((left, top, right, bottom))
    img.save('output_crop.png')  

def crop_player_name(image):
    img = Image.open(image)
    player_name_left = 0
    player_name_top = 0
    player_name_right = 305
    player_name_bottom = 85

    player_name = img.crop((player_name_left, player_name_top, player_name_right, player_name_bottom))
    player_name.save('player_name.png')

    name = parse_image_text('player_name.png', 'player_name.png', 100, False)[0]
    return name
 
def crop_player_stat(image, num_left, num_right):
    img = Image.open(image)

     # intervals of 270
    '''         (left, right)

    1st number: (300, 420) 
    2nd number: (540, 690)
    ALL AFTER INTERVALS OF 270
    3rd number: (810, 960)
    4th number: (1080, 1230) 
    5th number: (1350, 1500) 
    6th number: (1620, 1770)
    7th number: (1890, 2045)

    '''
  
    number_left = num_left                               
    number_top = 30
    number_right = num_right
    number_bottom = 160
   
    number_value = img.crop((number_left, number_top, number_right, number_bottom))
    number_value.save('number_value.png')

    image_scale_100 = parse_image_text('number_value.png', 'number_value_100.png', 100, True) 
    image_scale_400 = parse_image_text('number_value.png', 'number_value_400.png', 150, True)
    image_scale_200 = parse_image_text('number_value.png', 'number_value_200.png', 200, True)
    image_scale_400 = parse_image_text('number_value.png', 'number_value_400.png', 300, True)
    image_scale_400 = parse_image_text('number_value.png', 'number_value_400.png', 400, True)

    if image_scale_100[1] > image_scale_200[1] and image_scale_100[1] > image_scale_400[1]:
        best_match = image_scale_100[0]
        print("Highest confidence is {} with image scaling 100.".format(image_scale_100[1]))
    elif image_scale_200[1] > image_scale_400[1]:
        best_match = image_scale_200[0]
        print("Highest confidence is {} with image scaling 200.".format(image_scale_200[1]))
    else:
        best_match = image_scale_400[0]
        print("Highest confidence is {} with image scaling 400.".format(image_scale_400[1]))
    
    return best_match
    
def parse_image_text(input_image, output_image, scale, number_parse):
   
    add_image_filters(input_image, output_image, scale)

    reader = easyocr.Reader(['en'], verbose= False, gpu= True)

    if number_parse:
        text = reader.readtext(output_image, detail= 1, text_threshold= .000000000000001, mag_ratio= 2, allowlist="0123456789")
    else:
        text = reader.readtext(output_image, detail= 1, text_threshold= .000000000000001, mag_ratio= 2)
    print(text)
 
    try:
        text_value = text[0][1]
        text_confidence = float(text[0][2])
    except:
        return ['X', float('0')]
    else:
        return [text_value, text_confidence]



if __name__ == '__main__':
    main()
          