from PIL import Image, ImageFilter
from PIL.ExifTags import TAGS
import cv2 as cv
import numpy as np
import easyocr
import warnings

warnings.filterwarnings("ignore", category=UserWarning) 
MOBILE = 'MOBILE'
DESKTOP = 'DESKTOP'

class image_parser:

    all_player_stats = []

    origin = 0

    def parse(self, image, origin):

        print(f"Image origin: {self.origin}")
        print("\n\nLoading player stats! Please do not close the window.\n\n")

        # iterate through each player's name and score
        # starting at the top of the scoreboard and going down.
        for iter in range (-1, 3):
            current_player_stats = []
            self.image_black_and_white(image, origin)
            self.crop_full_image('images\\output.png', iter, origin)

            name = self.crop_player_name('images\\output_crop.png', origin)
            if name == 'X': # default value for a blank scrape is 'X'
                continue    # so if it can't find a name we want to end this iteration of the loop
            else:
                current_player_stats.append(name)

            # first stat scrape is hardcoded since playernames sometimes extended out and messed up the value using the loop values
            if origin == MOBILE:
                text_value = self.crop_player_stat('images\\output_crop.png', 320, 440, origin)
                current_player_stats.append(text_value)
 
                # loops over the remaining stats, scrapes them, and puts them in a list
                for i in range(0, 6):
                    text_value = self.crop_player_stat('images\\output_crop.png', (540 + (270 * i)), (690 + (270 * i)), origin)
                    current_player_stats.append(text_value)
            else:
                text_value = self.crop_player_stat('images\\output_crop.png', 380, 460, origin)
                current_player_stats.append(text_value)
 
                for i in range(0, 6):
                    text_value = self.crop_player_stat('images\\output_crop.png', (560 + (180 * i)), (640 + (180 * i)), origin)
                    current_player_stats.append(text_value)
        
            # stats from the current iteration of the loop are added to a list that will contain every player's stats. 
            if len(current_player_stats) != 8:
                print("Image not recognized as a valid Terraforming Mars Screenshot.")
                current_player_stats = []
                self.all_player_stats = []
                break
            else:
                self.all_player_stats.append(current_player_stats)

        for stat_list in self.all_player_stats:
            print(stat_list)

    def detect_origin(self, image):
        desktop_number = 1.7778
        img = Image.open(image)
        width, height = img.size

        if ((round((width / height), 4) == 1.7778) or (round((width / height), 4) == 1.6000)):
            self.origin = DESKTOP
        else:
            self.origin = MOBILE

    # convert image to black and white
    def image_black_and_white(self, image, origin):

        img = Image.open(image)
        data = np.array(img)

        converted = np.where(data == 255, 0, 255)

        img = Image.fromarray(converted.astype('uint8'))
        img.save('images\\output.png')

        img = cv.imread('images\\output.png', cv.IMREAD_GRAYSCALE)

        if origin == MOBILE:
            # standardize image to iphone12 resolution
            img = cv.resize(img, (2532, 1170))
        else:
            img = cv.resize(img, (1920, 1080))

        cv.imwrite('images\\output.png', img)

    # many settings to boost clarity of the value, ensuring higher accuracy of the scraper.
    def add_image_filters(self, input_image, output_image, scale):

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

        # save PIL edits to image
        img.save(output_image)

    # crops unecessary detail from image - leaving just the player name and the relevant stats for the match.
    def crop_full_image(self, image, iter, origin):

        img = Image.open(image)

        if (origin == MOBILE):
            VERTICAL_OFFSET = 150
            left = 157
            top =  457  + (iter * VERTICAL_OFFSET)
            right = 2220
            bottom = 625  + (iter * VERTICAL_OFFSET)
        else:
            VERTICAL_OFFSET = 100
            left = 0
            top = 366 + (iter * VERTICAL_OFFSET)
            right = 1580
            bottom = 425 + (iter * VERTICAL_OFFSET)

        img = img.crop((left, top, right, bottom))
        img.save('images\\output_crop.png')  

    # crops the player name from output_crop.png and parses the text.
    def crop_player_name(self, image, origin):

        img = Image.open(image)

        if (origin == MOBILE):
            player_name_left = 0
            player_name_top = 0
            player_name_right = 305
            player_name_bottom = 85
        else:
            player_name_left = 0
            player_name_top = 0
            player_name_right = 103
            player_name_bottom = 21

        player_name = img.crop((player_name_left, player_name_top, player_name_right, player_name_bottom))
        player_name.save('images\\player_name.png')

        if (origin == DESKTOP):
            name = self.parse_image_text('images\\player_name.png', 'images\\player_name.png', 100, False, True)[0]
            print(name)
        else:
            name = self.parse_image_text('images\\player_name.png', 'images\\player_name.png', 100, False)[0]

        return name

    # crops each individual stat from each sequential player and parses 5 times, each under a different image scaling value
    # to ensure maximum detection accuracy (some numbers would be wrong at lower/higher scaling values, like 1s, 4s, and 7s)
    def crop_player_stat(self, image, num_left, num_right, origin):

        img = Image.open(image)

        # MOBILE ONLY

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

        # DESKTOP ONLY

         # intervals of (180, 80)
        '''         (left, right)

        1st number: (380, 460) 
        2nd number: (560, 640)
        ALL AFTER INTERVALS OF 270
        3rd number: (740, 820)
        4th number: (920, 1000) 
        5th number: (1100, 1180) 
        6th number: (1280, 1360)
        7th number: (1460, 1540)
        '''
  
        if origin == MOBILE:
            number_left = num_left                               
            number_top = 30
            number_right = num_right
            number_bottom = 160
        else:
            number_left = num_left                               
            number_top = 18
            number_right = num_right
            number_bottom = 58
   
        number_value = img.crop((number_left, number_top, number_right, number_bottom))
        number_value.save('images\\number_value.png')

        # scales the number 5 separate times, higher image_scale value = less jagged edges, more clarity
        image_scale_100 = self.parse_image_text('images\\number_value.png', 'images\\number_value_100.png', 100, True) 
        image_scale_150 = self.parse_image_text('images\\number_value.png', 'images\\number_value_150.png', 150, True)
        image_scale_200 = self.parse_image_text('images\\number_value.png', 'images\\number_value_200.png', 200, True)
        image_scale_300 = self.parse_image_text('images\\number_value.png', 'images\\number_value_300.png', 300, True)
        image_scale_400 = self.parse_image_text('images\\number_value.png', 'images\\number_value_400.png', 400, True)

        # puts all images in a list and finds the one wih the highest confidence value
        image_confidence_list = [image_scale_100, image_scale_150, image_scale_200, image_scale_300, image_scale_400]
        image_confidence_list.sort(key= lambda x: x[1])
        best_match = image_confidence_list[-1]

        print("Highest confidence is {}, selecting value '{}'.".format(best_match[1], best_match[0]))

        # returns value with highest confidence
        return best_match[0]

    # scrapes the text from the image using easyOCR     
    def parse_image_text(self, input_image, output_image, scale, number_parse, desktop_name_parse = False):
   
        if not desktop_name_parse:
            self.add_image_filters(input_image, output_image, scale)

        reader = easyocr.Reader(['en'], verbose= False, gpu= True)

        # ensures whitelist is used for number scrapes to not get false detections (l as a 1, etc)
        if number_parse:
            text = reader.readtext(output_image, detail= 1, text_threshold= .000000000000001, mag_ratio= 2, allowlist="0123456789")
        else:
            text = reader.readtext(output_image, detail= 1, text_threshold= .000000000000001, mag_ratio= 2)
        
        # print(text)
 
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

ip = image_parser()

ip.detect_origin('images\\test5.png')
ip.parse('images\\test5.png', ip.origin)
          