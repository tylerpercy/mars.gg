from PIL import Image, ImageFilter
import cv2 as cv
import numpy as np
import easyocr
import warnings

warnings.filterwarnings("ignore", category=UserWarning) 

def parse():

    print("\n\nLoading player stats! Please do not close the window.\n\n")

    # iterate through each player's name and score
    # starting at the top of the scoreboard and going down.
    for iter in range (-1, 3):
        current_player_stats = []
        image_black_and_white('images\\test3.png')
        crop_full_image('images\\output.png', iter)

        name = crop_player_name('images\\output_crop.png')
        if name == 'X': # default value for a blank scrape is 'X'
            continue    # so if it can't find a name we want to end this iteration of the loop
        else:
            current_player_stats.append(name)

        # first stat scrape is hardcoded since playernames sometimes extended out and messed up the value using the loop values
        text_value = crop_player_stat('images\\output_crop.png', 320, 440)
        current_player_stats.append(text_value)
 
        # loops over the remaining stats, scrapes them, and puts them in a list
        for i in range(0, 6):
            text_value = crop_player_stat('images\\output_crop.png', (540 + (270 * i)), (690 + (270 * i)))
            current_player_stats.append(text_value)
        
        # stats from the current iteration of the loop are added to a list that will contain every player's stats. 
        all_player_stats.append(current_player_stats)

    for stat_list in all_player_stats:
        print(stat_list)

# convert image to black and white
def image_black_and_white(image):
    img = Image.open(image)
    data = np.array(img)

    converted = np.where(data == 255, 0, 255)

    img = Image.fromarray(converted.astype('uint8'))
    img.save('images\\output.png')

# many settings to boost clarity of the value, ensuring higher accuracy of the scraper.
def add_image_filters(input_image, output_image, scale):

    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])

    img = cv.imread(input_image, cv.IMREAD_GRAYSCALE)

    # scale image
    scale_percent = scale
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)
  
    # resize image
    img = cv.resize(img, dim, interpolation = cv.INTER_AREA)

    # blur image
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

    # save openCV edits to image
    cv.imwrite(output_image, img)

    # apply filters using PIL
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

    # save PIL edits to image
    img.save(output_image)


# crops unecessary detail from image - leaving just the player name and the relevant stats for the match.
def crop_full_image(image, iter):

    VERTICAL_OFFSET = 150

    img = Image.open(image)
    left = 157
    top =  457  + (iter * VERTICAL_OFFSET)
    right = 2220
    bottom = 625  + (iter * VERTICAL_OFFSET)

    img = img.crop((left, top, right, bottom))
    img.save('images\\output_crop.png')  

# crops the player name from output_crop.png and parses the text.
def crop_player_name(image):
    img = Image.open(image)
    player_name_left = 0
    player_name_top = 0
    player_name_right = 305
    player_name_bottom = 85

    player_name = img.crop((player_name_left, player_name_top, player_name_right, player_name_bottom))
    player_name.save('images\\player_name.png')

    name = parse_image_text('images\\player_name.png', 'images\\player_name.png', 100, False)[0]
    return name


# crops each individual stat from each sequential player and parses 5 times, each under a different image scaling value
# to ensure maximum detection accuracy (some numbers would be wrong at lower/higher scaling values, like 1s, 4s, and 7s)
def crop_player_stat(image, num_left, num_right):
    img = Image.open(image)

     # intervals of 270
    '''         (left, right)

    1st number: (320, 440) 
    2nd number: (540, 690)
    ALL AFTER INTERVALS OF 270
    3rd number: (810, 960)
    4th number: (1080, 1230) 
    5th number: (1350, 1500) 
    6th number: (1620, 1770)
    7th number: (1890, 2045)

    '''
  
    # crops the number
    number_left = num_left                               
    number_top = 30
    number_right = num_right
    number_bottom = 160
   
    number_value = img.crop((number_left, number_top, number_right, number_bottom))
    number_value.save('images\\number_value.png')

    # scales the number 5 separate times, higher image_scale value = less jagged edges, more clarity
    image_scale_100 = parse_image_text('images\\number_value.png', 'images\\number_value_100.png', 100, True) 
    image_scale_150 = parse_image_text('images\\number_value.png', 'images\\number_value_150.png', 150, True)
    image_scale_200 = parse_image_text('images\\number_value.png', 'images\\number_value_200.png', 200, True)
    image_scale_300 = parse_image_text('images\\number_value.png', 'images\\number_value_300.png', 300, True)
    image_scale_400 = parse_image_text('images\\number_value.png', 'images\\number_value_400.png', 400, True)

    # puts all images in a list and finds the one wih the highest confidence value
    image_confidence_list = [image_scale_100, image_scale_150, image_scale_200, image_scale_300, image_scale_400]
    image_confidence_list.sort(key= lambda x: x[1])
    best_match = image_confidence_list[-1]

    print("Highest confidence is {}, selecting value '{}'.".format(best_match[1], best_match[0]))

    # returns value with highest confidence
    return best_match[0]

# scrapes the text from the image using easyOCR     
def parse_image_text(input_image, output_image, scale, number_parse):
   
    add_image_filters(input_image, output_image, scale)

    reader = easyocr.Reader(['en'], verbose= False, gpu= True)

    # ensures whitelist is used for number scrapes to not get false detections (l as a 1, etc)
    if number_parse:
        text = reader.readtext(output_image, detail= 1, text_threshold= .000000000000001, mag_ratio= 2, allowlist="0123456789")
    else:
        text = reader.readtext(output_image, detail= 1, text_threshold= .000000000000001, mag_ratio= 2)
    print(text)
 
    # this will raise an exception when no value is detected (blank white square)
    # it is fine for this to happen, as it usually means it just did not detect a player on that iteration of the loop
    # default values returned for no detection is [X, '0']
    try:
        text_value = text[0][1]
        text_confidence = float(text[0][2])
    except:
        return ['X', float('0')]
    else:
        return [text_value, text_confidence]


all_player_stats = []

parse()
          