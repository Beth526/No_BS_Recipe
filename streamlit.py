import streamlit as st
import requests
import re
import urllib
import html

html_translation_dict = {'&#x25a2;':'\n\n',
                '&#39;&#3':'X ',
                '&;': " ",
                '&#160;':' '                   
}

def fix_run_on_word(word):
    result=word[0]
    for i, c in enumerate(word[1:]):
        i=i-1
        # Check if the character is uppercase
        if word[i].islower() and c.isupper():
            result = result + " " + c.upper()
        elif c.isupper() and word[i+3].islower():
            # Concatenate a space and the uppercase version of the character to the result
            result = result + " " + c.upper()
        elif word[i+1].isnumeric() and not c.isnumeric():
            result = result + " " + c
        elif c != " " and word[i]==")":
            result = result + " " + c
        else:
            # Concatenate the character to the result
            result = result + c
    return result

def remove_wierd_word(string):
    string = string.split(' ')
    string = [w for w in string if w.find('[')==-1 and w.find(']')==-1 and w.find('{')==-1 and w.find('}')==-1]
    string = [w for w in string if w.find('@')==-1]
    string = [w for w in string if w.count('&')<2 and w.count(':')<2 and w.count('-')<2 and w.count(';')<2]
    string = (' ').join(string)
    string = re.sub(';[^\s\n]+','',string)
    string = re.sub('[\d]+px','',string)
    string = re.sub('[\d]+ px','',string)
    return(string)

def add_new_lines_ingredients(string, html_translation_dict):
    translation_dict = {
                '1x':'',
                '2x':'',
                '3x':'',
                '1.5':'',
                '1 x':'',
                '2 x':'',
                '3 x':'',
                'Prevent your screen from going dark':'',
                'Cook mode':'',
                'Cook  Mode':'',
                'Scale':'',
                'prevent screen from going dark':'',
                'Prevent screen from going dark':'',
                'Copy to clipboard':'',
                'US Customary Metric':'',
                '\n':'  \n',
                '\n                    ':'  \n'
               }
    translation_dict.update(html_translation_dict)
    # loop through the dictionary and replace each character in the string
    for key, value in translation_dict.items():
        string = string.replace(key, value)
    string=html.unescape(string)
    starts = [(m.start()) for m in re.finditer('[^\n/]\d+\.*\d*',string)]
    #starts = [(m.start()) for m in re.finditer('^(?!\n|/|-)\d+\.*\d*',string)]
    other_starts = [(m.start()-2) for m in re.finditer('(?<=\d)[¼½⅔⅓¾]',string)]
    other_starts2 = [(m.start()-1) for m in re.finditer('(?<!\d)[¼½⅔⅓¾]',string)]
    undo = [(m.end()) for m in re.finditer('to |and |or |about |approximately |-|–|\d |\(|\([^\)]*\d|\([^\)]*[¼½⅔⅓¾]|\d',string)]
    undo2 = [(m-1) for m in undo]
    undo3 = [(m-2) for m in undo]
    all_starts = starts + other_starts + other_starts2
    string = list(string)
    offset=1
    for s in sorted(all_starts):
        if s not in undo+undo2+undo3:
            string.insert(s+offset,'  \n')
            offset += 1 

    string = ('').join(string)
    other_starts3 = [(m.start()) for m in re.finditer('\)[A-Za-z]|\d[A-Za-z]{3,}|[A-Za-z]\d',string)]
    string = list(string)
    offset=1
    for s in sorted(other_starts3):
        string.insert(s+offset,'  \n')
        offset += 1 
    return(('').join(string))

    
def add_new_lines_instructions(string,html_translation_dict):
    translation_dict = {'Notes':'  \nNotes  \n',
                'Tips':'  \nTips  \n',
                #'Nutrition':'  \nNutrition  \n',
                '\n':'  \n',
                'Recommendations':'  \nRecommendations  \n',
                'Equipment':'  \nEquipment   \n',
                'Video':'  \nVideo   \n'
               }
    translation_dict.update(html_translation_dict)
    # loop through the dictionary and replace each character in the string
    for key, value in translation_dict.items():
        string = string.replace(key, value)
    string=html.unescape(string)
    starts = [(m.start()) for m in re.finditer('Cook |Fry |Bake |Heat |Season |Combine |Add |Mix |Blend |Stir |Shake |Bring |Remove |Divide |Sprinkle |Sift |Seperate |Place |Top |Pour |Fill |Spoon |Make |Place |Cut |Chop |Strain |Serve |In a |Peel |Puree |Wrap |Roll |Preheat |Pre-heat |Melt |Marinate |Simmer |Steam |Prick |Process |With a |Store |Freeze |Refridgerate |Microwave |Toast |Grill |Chill |Sauté |Saute |Cover |Allow |Defrost |Use |Boil |Chill |Rub |Swirl |Slice |Sear |Soak |Heat |While |Crumble |Scramble |Roast |Kneed |Dice |Peel |Baste |Batter |Coat |Blanch |Brew |Braise |Brush |Deep fry |Shape |Deep-fry |Drain |Flambe |Filet |Fold |Grease |Grind |Take |Form |Juice |Juliene |Mash |Parboil |Poach |Press |Pickle |Pare |Quarter |Render |Reduce |Shred |Shuck |Toss |Steep |Sweeten |Skewer |Score |Shell |Thicken |Whisk |Whip |Trim |Warm |Zest |Cover |Cure |Slather |Garnish |Crack |Tear |Beat |Shave |Scrape |Glaze |Blacken |Char |Fluff |Dredge |Pulse |Macerate |Mince |Grate |Drizzle |Caramelise |Caramelize |Using |Use |Then |Next |Finally |Once |After |Before |First |Next |During |When |Line |Grease |Moisten |Wet |Transfer |Spread |Flip |Rest |Prepare |Prior to |Set up |Replace |Keep |To a |Gather |Set |If using |Loosen ',string)]
    string_list = list(string)
    offset=0
    for s in starts:
        string_list.insert(s+offset,'  \n  \n '+str(offset+1)+') ')
        offset += 1
    return(('').join(string_list))

def clean_up(string):
    string = re.sub('#[a-zA-Z0-9]+','',string)
    string = re.sub('[^\s]+:[^\s\n]+','',string)
    #string = re.sub('[^\s]+;[^\s\n]+','',string)
    string = re.sub('{[^\s]}+}','',string)
    #string = re.sub('\.[^\s]','\. ',string)
    #string = re.sub('[\t\n]{5,}','\n\n',string)
    string = re.sub('\t','',string)
    string = re.sub('\n{3,}','\n',string)
    string = re.sub('\[{.*"text":',' ',string)
    string = re.sub('"}\]',' ',string)
    string = re.sub('[www|http]+/.com','',string)
    string = fix_run_on_word(string)
    return(string)

def no_bs_recipe(url):
    if url=='':
        return(None)
    url_parts = urllib.parse.urlparse(url)
    path_parts = url_parts[2].rpartition('/')
    if len(path_parts[0])==0:
      path_parts = path_parts[::-1]
    st.write(path_parts[0].replace('/',' ').replace('-',' ').upper()+'\n')
    user_agent = {'User-agent': 'Mozilla/5.0'}
    response = requests.get(url, headers = user_agent)
    page = response.text
    plain_page = re.sub('<[^>]*>','',page)
    ingredient_locations = [(m.span()) for m in re.finditer('Ingredients:*|INGREDIENTS:*|You Will Need:*|You will need:*',plain_page)]
    if ingredient_locations == []:
        ingredient_locations = [(m.span()) for m in re.finditer('Serves:*|Servings:*|Yields*:*',plain_page,flags=re.IGNORECASE)]
    instruction_locations = [(m.span()) for m in re.finditer('Instructions:*|INSTRUCTIONS:*|Directions:*|DIRECTIONS:*|HOW TO:*|How To Make:*|How to Make:*|Steps:*|STEPS:*|STEP 1:*|Step 1:*|Method:*|You  Will  Need:*|Preparation:*',plain_page)]
    instruction_locations = [a + ('instruction',) for a in instruction_locations]
    ingredient_locations = [a + ('ingredient',) for a in ingredient_locations]
    combined_locations = instruction_locations + ingredient_locations
    combined_locations = sorted(combined_locations,key=lambda x: x[0])
    serving_size = re.search('Serving Size[: ][ ]*([\d]+)|Serves[: ][ ]*([\d]+)|Servings[: ][ ]*([\d]+)|yield[: ][ ]*([\d]+)|yields[: ][ ]*([\d]+)',plain_page,flags=re.IGNORECASE)
    if serving_size:
        st.write(serving_size.group(0)+'\n')
    prep_time = re.search('Prep Time[: ][ ]*[\d\.]+ min|Prep Time[: ][ ]*[\d\.]+ hour|Prep Time[: ][ ]*[\d\.]+ hr',plain_page,flags=re.IGNORECASE)
    if prep_time:
        st.write(prep_time.group(0)+'\n')
    cook_time = re.search('Cook Time[: ][ ]*[\d\.]+ min|Cook Time[: ][ ]*[\d\.]+ hour|Cook Time[: ][ ]*[\d\.]+ hr',plain_page,flags=re.IGNORECASE)
    if cook_time:
        st.write(cook_time.group(0)+'\n')
    temp = [i for i, x in enumerate(combined_locations) if x[-1] == 'instruction' and combined_locations[i-1][-1] == 'ingredient']
    if temp == [] or temp == [0]:
        st.write('Sorry, we had trouble finding the recipe on this page! Note that Food Network blocks web scraping, so this app will not work with Food Network.')
        return('Error')
    
    st.write('INGREDIENTS\n\n')
    t = max(temp)
    ingredients = plain_page[combined_locations[t-1][1]:combined_locations[t][0]]

    if (sum([c in ['{','}','[',']'] for c in html.unescape(plain_page[combined_locations[t-1][1]:combined_locations[t][0]])])>4 or len(ingredients)<20) and len(temp)>1:
        temp.remove(t)
        def get_num_digits(t):
            return sum(c.isdigit() for c in html.unescape(plain_page[combined_locations[t-1][1]:combined_locations[t][0]]))
        temp = sorted(temp,key=get_num_digits)
        t = temp[-1]
        ingredients = plain_page[combined_locations[t-1][1]:combined_locations[t][0]]
    st.write(remove_wierd_word(add_new_lines_ingredients(clean_up(ingredients),html_translation_dict)))
    
    instructions = plain_page[combined_locations[t][1]:]
    stop_instructions_pos = [(m.start()) for m in re.finditer('Comment|Facebook|Instagram|Rate|Rating|Subscribe|Review|Share|Tag|Print|Did you make this|Tried this recipe|Let us know if you|Did you love|Did you like|Email|Nutrition',instructions)]

    st.write('\n\nINSTRUCTIONS\n\n')
    if stop_instructions_pos == []:
        st.write(remove_wierd_word(add_new_lines_instructions(clean_up(instructions),html_translation_dict)))
    else:
        st.write(remove_wierd_word(add_new_lines_instructions(clean_up(instructions[:stop_instructions_pos[0]]),html_translation_dict)))
        
        
st.write("No BS Recipes! No Ads, no pop ups, no life story.")
url = st.text_input("Copy and paste a recipe's URL in the box below and then hit enter")

no_bs_recipe(url)
        



