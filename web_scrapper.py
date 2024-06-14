from bs4 import BeautifulSoup
import requests
import pandas as pd
import demoji


def extract_field(review_table,field):
    try:
        return review_table.find('td',class_=field).find_next_sibling().text
    except AttributeError:
        return None

def extract_stars(review_table,field):
    try:
        return len(review_table.find('td',class_=field).find_next_sibling().find_all("span",class_="star fill"))
    except Exception:
        return None

def extract_with_itemprop(review,element,prop):
    try:
        return review.find(element,itemprop=prop).text
    except AttributeError:
        return None


def extract_table(review_table):
    aircraft_flown = extract_field(review_table,"aircraft")
    type_of_traveller = extract_field(review_table,"type_of_traveller")
    cabin_flown = extract_field(review_table,"cabin_flown")
    route_flown = extract_field(review_table,"route")
    recommend_to_others = extract_field(review_table,"recommended")
    date_flown = extract_field(review_table,"date_flown")

    seat_comfort = extract_stars(review_table,"seat_comfort")
    cabin_service = extract_stars(review_table,"cabin_staff_service")
    food_and_beverages = extract_stars(review_table,"food_and_beverages")
    ground_service = extract_stars(review_table,"ground_service")
    wifi_service = extract_stars(review_table,"wifi_and_connectivity")
    value_for_money = extract_stars(review_table,"value_for_money")

    return (aircraft_flown,type_of_traveller,cabin_flown,route_flown,date_flown,recommend_to_others,seat_comfort,cabin_service,food_and_beverages,ground_service,wifi_service,value_for_money)



rows = []
for page_num in range(1,39):
    url = f"https://www.airlinequality.com/airline-reviews/british-airways/page/{page_num}/?sortby=post_date%3ADesc&pagesize=100"
    page = requests.get(url)
    soup = BeautifulSoup(page.content,'html.parser')
    reviews = soup.find_all('article',itemprop='review')
    for review in reviews:
        rating =  extract_with_itemprop(review,'span','ratingValue')
        timestamp = extract_with_itemprop(review,'time','datePublished')
        reviewBody = extract_with_itemprop(review,'div','reviewBody')
        
        stats_table = review.find("table",class_="review-ratings")
        aircraft_flown,type_of_traveller,cabin_flown,route_flown,date_flown,recommend_to_others,seat_comfort,cabin_service,food_and_beverages,ground_service,wifi_service,value_for_money = extract_table(stats_table)
        row = {
            "rating":rating,
            'timestamp':timestamp,
            "aircraft_flown":aircraft_flown,
            "travel_type":type_of_traveller,
            "cabin":cabin_flown,
            "route":route_flown,
            "date_of_flight":date_flown,
            'content':reviewBody,
            "seat_comfort":seat_comfort,
            "cabin_service":cabin_service,
            "food_and_beverages":food_and_beverages,
            "ground_service":ground_service,
            "wifi_service":wifi_service,
            "value_for_money":value_for_money,
            "will_recommend":recommend_to_others
        }
        rows.append(row)


df_reviews = pd.DataFrame(rows)
df_reviews = df_reviews.convert_dtypes()
df_reviews["travel_type"] = df_reviews["travel_type"].astype('category')
df_reviews["cabin"] = df_reviews["cabin"].astype('category')
df_reviews["date_of_flight"] = df_reviews["date_of_flight"].astype('category')
df_reviews["will_recommend"] = df_reviews["will_recommend"].astype('category')

df_reviews[["trip_verified","user_reviews"]] = df_reviews["content"].str.split("|",expand=True)
df_reviews.drop(["content"],inplace=True,axis=1)
df_reviews.loc[2252:,"user_reviews"]  = df_reviews.loc[2252:,"trip_verified"].copy() #earlier reviews don't have trip_verification
df_reviews.loc[2252:,"trip_verified"] = ''


df_reviews["trip_verified"] = df_reviews["trip_verified"].apply(lambda x:demoji.replace(x,''))
df_reviews["trip_verified"] = df_reviews["trip_verified"].astype('category')
df_reviews["user_reviews"] = df_reviews["user_reviews"].astype('string')

df_reviews.to_csv("British_Airways_reviews.csv")
  