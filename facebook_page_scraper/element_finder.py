#!/usr/bin/env python3
import dateparser

try:
    from selenium.common.exceptions import NoSuchElementException
    from .scraping_utilities import Scraping_utilities
    from .driver_utilities import Utilities
    import sys
    import urllib.request
    import re
    from dateutil.parser import parse
    import dateutil
    import datetime
    from selenium.webdriver.common.by import By
except Exception as ex:
    print(ex)

class Finder():
    """
    Holds the collections of methods that finds element of the facebook's posts using selenium's webdriver's methods
    """

    @staticmethod
    def __get_status_link(link_list):
        status = ""
        for link in link_list:
            link_value = link.get_attribute("href")
            if "/posts/" in link_value and "/groups/" in link_value:
                status = link
                break
            if "/posts/" in link_value:
                status = link
                break
            if "/videos/pcb" in link_value:
                status = link
                break
            elif "/photos/" in link_value:
                # print(link_value)
                status = link
                break
            if "fbid=" in link_value:
                status = link
                break
            elif "/group/" in link_value:
                # print(link_value)
                status = link
                break
            if "/videos/" in link_value:
                # print(link_value)
                status = link
                break
            elif "/groups/" in link_value:
                # print(link_value)
                status = link
                break
        return status

    @staticmethod
    def __find_status(post,layout):
        """finds URL of the post, then extracts link from that URL and returns it"""
        try:
            link = None
            if layout == "old":
              #aim is to find element that looks like <a href="URL" class="_5pcq"></a>
              #after finding that element, get it's href value and pass it to different method that extracts post_id from that href
              status_link = post.find_element(By.CLASS_NAME,"_5pcq").get_attribute("href")
              #extract out post id from post's url
              status = Scraping_utilities._Scraping_utilities__extract_id_from_link(status_link)
            elif layout == "new":
              #links = post.find_elements(By.CSS_SELECTOR,"a[role='link']")
              # link = post.find_element(By.CSS_SELECTOR,'.gpro0wi8.b1v8xokw')
              # link = post.find_element(By.CSS_SELECTOR, '.jxuftiz4.cxfqmxzd.tes86rjd')
              link = post.find_element(
                  By.CSS_SELECTOR, 'span > a[aria-label][role="link"]')
              status_link = link.get_attribute('href')
              status = Scraping_utilities._Scraping_utilities__extract_id_from_link(
                  status_link)
        except NoSuchElementException:
            #if element is not found
            status = "NA"

        except Exception as ex:
            print("error at find_status method : {}".format(ex))
            status = "NA"

        return (status,status_link,link)

    @staticmethod
    def __find_share(post,layout):
        """finds shares count of the facebook post using selenium's webdriver's method"""
        print("Type: " + layout)
        try:
            if layout == "old":
              #aim is to find element that have datatest-id attribute as UFI2SharesCount/root
              shares = post.find_element(By.CSS_SELECTOR,"[data-testid='UFI2SharesCount/root']").get_attribute('textContent')
              shares = Scraping_utilities._Scraping_utilities__extract_numbers(shares)
            elif layout == "new":
              elements = post.find_elements(By.CSS_SELECTOR, "div.gtad4xkn")
              print(post)
              elements = post.find_elements(By.CSS_SELECTOR, "div.dkzmklf5")
              shares = "0"
              for element in elements:
                print(element.text)
                text = element.text
                if "Share" in text:
                    shares = text.split()[0]
                    # shares = re.findall("\d+", text)[0]
                    break
            return shares
        except NoSuchElementException:
            #if element is not present that means there wasn't any shares
            shares = 0

        except Exception as ex:
            print("error at find_share method : {}".format(ex))
            shares = 0


        return shares

    @staticmethod
    def __find_reactions(post):
        """finds all reaction of the facebook post using selenium's webdriver's method"""
        try:
            #find element that have attribute aria-label as 'See who reacted to this
            reactions_all = post.find_element(By.CSS_SELECTOR,'[aria-label="See who reacted to this"]')
        except NoSuchElementException:
            reactions_all = ""
        except Exception as ex:
            print("error at find_reactions method : {}".format(ex))
        return reactions_all

    @staticmethod
    def __find_comments(post,layout):
        """finds comments count of the facebook post using selenium's webdriver's method"""
        try:
            # print(layout)
            comments = ""
            if layout == "old":
              comments = post.find_element(By.CSS_SELECTOR,"a._3hg-").get_attribute('textContent')
              #extract numbers from text
              comments = Scraping_utilities._Scraping_utilities__extract_numbers(comments)
            elif layout == "new":
              elements = post.find_elements(By.CSS_SELECTOR,"div.dkzmklf5")
              comments = "0"
              for element in elements:
                text = element.text
                print(text)
                if "Comment" in text:
                    comments = text.split()[0]
                    # comments = Scraping_utilities._Scraping_utilities__extract_numbers(
                    #     text.split()[0])
                    # print(comments)
        except NoSuchElementException:
            comments = 0
        except Exception as ex:
            print("error at find_comments method : {}".format(ex))
            comments = 0

        return comments

    @staticmethod
    def __fetch_post_passage(href):

        response = urllib.request.urlopen(href)

        text = response.read().decode('utf-8')

        post_message_div_finder_regex = '<div data-testid="post_message" class=".*?" data-ft=".*?">(.*?)<\/div>'

        post_message = re.search(post_message_div_finder_regex,text)

        replace_html_tags_regex = '<[^<>]+>'
        message = re.sub(replace_html_tags_regex,'',post_message.group(0))

        return message

    @staticmethod
    def __element_exists(element,css_selector):
        try:
            found = element.find_element(By.CSS_SELECTOR,css_selector)
            return True
        except NoSuchElementException:
            return False

    @staticmethod
    def __find_content(post,driver,layout):
        """finds content of the facebook post using selenium's webdriver's method and returns string containing text of the posts"""
        try:
            if layout == "old":
              post_content = post.find_element(By.CLASS_NAME,'userContent')
            elif layout == "new":
              post_content = post.find_element(By.CSS_SELECTOR,'[data-ad-preview="message"]')
            #if 'See more' or 'Continue reading' is present in post
            if Finder._Finder__element_exists(post_content,"span.text_exposed_link > a"):
                element = post_content.find_element(By.CSS_SELECTOR,"span.text_exposed_link > a") #grab that element
                #if element have already the onclick function, that means it is expandable paragraph
                if element.get_attribute("onclick"):
                    Utilities._Utilities__click_see_more(driver,post_content) #click 'see more' button to get hidden text as well
                    content = Scraping_utilities._Scraping_utilities__extract_content(post_content) #extract content out of it
                elif element.get_attribute("target"): #if element have attribute of target="_blank"
                #if it does not have onclick() method, it means we'll to extract passage by request
                #if content have attribute target="_blank" it indicates that text will open in new tab,
                #so make a seperate request and get that text
                    content = Finder._Finder__fetch_post_passage(element.get_attribute("href"))
            else:
                #if it does not have see more, just get the text out of it
                content = post_content.get_attribute("textContent")

        except NoSuchElementException:
            #if [data-testid="post_message"] is not found, it means that post did not had any text,either it is image or video
            content = ""
        except Exception as ex:
            print("error at find_content method : {}".format(ex))
            content = ""
        return content


    @staticmethod
    def __find_posted_time(post,layout,link_element):
        """finds posted time of the facebook post using selenium's webdriver's method"""
        try:
            #extract element that looks like <abbr class='_5ptz' data-utime="some unix timestamp"> </abbr>
            #posted_time = post.find_element_by_css_selector("abbr._5ptz").get_attribute("data-utime")
            if layout == "old":
              posted_time = post.find_element(By.TAG_NAME,"abbr").get_attribute('data-utime')
              return datetime.datetime.fromtimestamp(float(posted_time)).isoformat()
            elif layout == "new":
              aria_label_value = link_element.get_attribute("aria-label")
              # print(aria_label_value)
              timestamp = dateparser.parse(aria_label_value).isoformat()
              return timestamp

              # if "at" in aria_label_value:
              #     timestamp = parse(aria_label_value).isoformat() if len(
              #         aria_label_value) > 5 else Scraping_utilities._Scraping_utilities__convert_to_iso(aria_label_value)
              # else:
              #     aria_label_value = aria_label_value + " at 0:00 AM"
              #     timestamp = parse(aria_label_value).isoformat() if len(
              #         aria_label_value) > 5 else Scraping_utilities._Scraping_utilities__convert_to_iso(aria_label_value)
              # return timestamp
        except dateutil.parser._parser.ParserError:
            timestamp = Scraping_utilities._Scraping_utilities__convert_to_iso(
                aria_label_value)
            return timestamp
        except TypeError:
            timestamp = ""
        except Exception as ex:
            print("error at find_posted_time method : {}".format(ex))
            timestamp = ""
            return timestamp


    @staticmethod
    def __find_video_url(post,page_name,status):
        """finds video of the facebook post using selenium's webdriver's method"""
        try:
            #if video is found in the post, than create a video URL by concatenating post's id with page_name
            video_element = post.find_element(By.TAG_NAME,"video")
            video = "https://www.facebook.com/{}/videos/{}".format(page_name,status)

        except NoSuchElementException:
            video = ""
            pass
        except Exception as ex:
            video = ""
            print("error at find_video_url method : {}".format(ex))

        return video

    @staticmethod
    def __find_image_url(post):
        """finds all image of the facebook post using selenium's webdriver's method"""
        try:
            #find all img tag that looks like <img class="scaledImageFitWidth img" src="">
            # images = post.find_elements(By.CSS_SELECTOR,"img.scaledImageFitWidth.img")
            images = post.find_elements(By.CSS_SELECTOR, "img.p9wrh9lq")
            images = post.find_elements(
                By.CSS_SELECTOR, "div > img[referrerpolicy]")
            # images = post.find_elements(By.TAG_NAME, 'img')
            #extract src attribute from all the img tag,store it in list
            #<div class="i85zmo3j z6erz7xo bdao358l alzwoclg on4d8346 jcxyg2ei s8sjc6am myo4itp8 ekq1a7f9"
            # data-visualcompletion="ignore"><img alt="" class="pytsy3co ncxvlvn8" referrerpolicy="origin-when-cross-origin"
            # src="https://scontent.ffln6-1.fna.fbcdn.net/v/t15.5256-10/298813062_611675610309072_7590354201326377892_n.jpg?stp=dst-jpg_p180x540&amp;_nc_cat=1&amp;ccb=1-7&amp;_nc_sid=ad6a45&amp;_nc_eui2=AeFjHSx1aqYMnIhU7ricxRGZre7AMKVCWMOt7sAwpUJYw0SctnXWicnT2023NRj1zEGo8KnHbBoPTGr-iXmvTaXL&amp;_nc_ohc=w-nnKTu5i_sAX9-qYk4&amp;_nc_ht=scontent.ffln6-1.fna&amp;oh=00_AT8z2uOrySCrBCbau1pHQquoQR1w63iI_reha01kcN9bqQ&amp;oe=630816F6"></div>
            if len(images) > 0:
                sources = [image.get_attribute("src") for image in images] if len(images) > 0 else []
            else:
                images = post.find_elements(By.CSS_SELECTOR, "img.p9wrh9lq")
                if len(images) > 0:
                    sources = [image.get_attribute("src") for image in images] if len(images) > 0 else []
                else:
                    images = post.find_elements(By.CSS_SELECTOR, "img.ncxvlvn8")
                    if len(images) > 0:
                        sources = [image.get_attribute("src") for image in images] if len(images) > 0 else []
                    else:
                        #if multiples images the class is different from single image
                        images = post.find_elements(By.CSS_SELECTOR, "img.s8sjc6am")
                        if len(images) > 0:
                            sources = [image.get_attribute("src") for image in images] if len(images) > 0 else []
                        else:
                            images = post.find_elements(By.CSS_SELECTOR, "img.scaledImageFitWidth.img")
                            sources = [image.get_attribute("src") for image in images] if len(images) > 0 else []

        except NoSuchElementException:
            sources = []
            pass
        except Exception as ex:
            print("error at find_image_url method : {}".format(ex))
            sources = []

        return sources

    @staticmethod
    def __find_all_posts(driver,layout):
        """finds all posts of the facebook page using selenium's webdriver's method"""
        try:
            #find all posts that looks like <div class="userContentWrapper"> </div>
            if layout == "old":
              all_posts = driver.find_elements(By.CSS_SELECTOR,"div.userContentWrapper")
            elif layout == "new":
              all_posts = driver.find_elements(By.CSS_SELECTOR,'[aria-posinset]')
            return all_posts
        except NoSuchElementException:
            print("Cannot find any posts! Exiting!")
            #if this fails to find posts that means, code cannot move forward, as no post is found
            Utilities.__close_driver(driver)
            sys.exit(1)
        except Exception as ex:
            print("error at __find_all_posts method : {}".format(ex))
            Utilities.__close_driver(driver)
            sys.exit(1)

    @staticmethod
    def __find_name(driver,layout):
        """finds name of the facebook page using selenium's webdriver's method"""
        try:
            if layout == "old":
              name =  driver.find_element(By.CSS_SELECTOR,'a._64-f').get_attribute('textContent')
            elif layout == "new":
              name = driver.find_element(By.TAG_NAME,"strong").get_attribute("textContent")
            return name
        except Exception as ex:
            print("error at __find_name method : {}".format(ex))

    @staticmethod
    def __detect_ui(driver):
      try:
        driver.find_element(By.ID,"pagelet_bluebar")
        return "old"
      except NoSuchElementException:
        return "new"
      except Exception as ex:
        print("error art __detect_ui: {}".format(ex))
        Utilities.__close_driver(driver)
        sys.exit(1)

    @staticmethod
    def __find_reaction(layout, reactions_all):
      try:
        if layout == "old":
          return reactions_all.find_elements(By.TAG_NAME,
              "a")
        elif layout == "new":
          return reactions_all.find_elements(By.TAG_NAME,
            "div")

      except Exception as ex:
        print("find_reaction", ex)
        return ""

