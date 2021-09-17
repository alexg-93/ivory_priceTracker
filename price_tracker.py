import requests
from bs4 import BeautifulSoup
import time
from bidi.algorithm import get_display
from operator import itemgetter
from email_sender import send_email
from tabulate import tabulate
from colorama import Fore, Style

 
#Track prices for specific product and get alert by email when price reach price you're looking for
def check_price_of_product_and_notify(URL,required_price):
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    title = soup.find(id="titleProd").get_text()
    price = soup.select_one('.print-actual-price').get_text()
    price = int(price.translate({ord(','): None}))
   
    
    products = [['Product','Price (₪)','Link'],[get_display(title),f"₪{price}",URL]]
    print(Fore.GREEN + tabulate(products, tablefmt='fancy_grid') + Style.RESET_ALL)
    

   
    if(price<=required_price):
             send_email(get_display(title.strip()),price,URL)
             print(Fore.RED + f"PRICE IS DOWN TO {price}!")
             return False
    return True
        

               
#function to check products of specific category
def check_products_single_page(CATEGORY_URL):
    try: 
        page = requests.get(CATEGORY_URL)
        soup = BeautifulSoup(page.content, 'html.parser')

        category_name = soup.select_one(".title_page_catalog").get_text()
    
        titles = soup.find_all(
            class_='col-md-12 col-12 title_product_catalog mb-md-1 hoverorange main-text-area')

        prices=[]
        products=[]
        
        all_products = soup.find_all(class_='row p-1 entry-wrapper')
        for prod in all_products:
            prices_with_sale=prod.find_all(class_='price-area d-inline-block')
            prices_no_sale = prod.find_all(class_='text-center right-position pricing-col col-12 col-md-12')
            
            if prices_with_sale:
                for price in prices_with_sale:
                    sale_price = price.find_all(class_='price')
                    for p in sale_price:
                        p=p.get_text()
                        sale_price = int(p.translate({ord(','): None}))
                        prices.append(f"{sale_price} {Fore.RED + 'SALE!'}"+ Style.RESET_ALL)
            if prices_no_sale:
                for price in prices_no_sale:
                    no_sale_price = price.find_all(class_='price')
                    for p in no_sale_price:
                        p=p.get_text()
                        regular_price = int(p.translate({ord(','): None}))
                        prices.append(regular_price)
            
    
        for title, price in zip(titles, prices):
            products.append({'Product': get_display(title.text), 'Price': price})
        
        
        header = products[0].keys()
        rows =  [prod.values() for prod in products]
        
        print("\n")
        print("###################################\n")
        Category_Info = [['Category','Total Products','Link'],[get_display(category_name),len(products),CATEGORY_URL]]
        print(Fore.LIGHTGREEN_EX + tabulate(Category_Info, tablefmt='fancy_grid') + Style.RESET_ALL)
        print(tabulate(rows,header, tablefmt='fancy_grid'))
    
        print("\n\n###################################\n")

        print("Do you want to sort prices by Low or High ? type L or H ..\nor any other key to continue")

        toSort  = input()
        print("\n\n###################################\n\n")
        if toSort == 'L':
            # sorted products price low to high
            sorted_products_by_price_LH = sorted(products, key=itemgetter('Price'))
            header =  sorted_products_by_price_LH[0].keys()
            rows =  [prod.values() for prod in sorted_products_by_price_LH]
            print(f"Sorted by price Low to High :\n")
            print(Fore.GREEN + tabulate(rows,header, tablefmt='fancy_grid') + Style.RESET_ALL)
            print("\n\n###################################\n\n")
        elif toSort == 'H':
            # sorted products price high to low
            sorted_products_by_price_HL = sorted(products, key=itemgetter('Price'), reverse=True)
            header =  sorted_products_by_price_HL[0].keys()
            rows =  [prod.values() for prod in sorted_products_by_price_HL]
            print(f"Sorted by price High to Low :\n")
            print(Fore.GREEN + tabulate(rows,header, tablefmt='fancy_grid') + Style.RESET_ALL)
            print("\n\n###################################\n\n")
        else:
         pass
        return products
    except :
        raise Exception(Fore.RED + "Something went wrong..check URL maybe" + Style.RESET_ALL)


#function to check products of category with multiple pages
def check_multiple_pages_in_category(URL):
    page = requests.get(URL)
    doc = BeautifulSoup(page.content, 'html.parser')
    check_products_single_page(URL)
    page_list = doc.find(id="pagesList")
    if page_list:
            pages = page_list.find_all("a",href=True)
            pages_found = len(pages[:-2])
            pages_found = str(pages_found)
            print(Fore.YELLOW + f'FOUND MORE {pages_found} PAGES' + Style.RESET_ALL)
            for url in pages[:-2]:
                    url=url['href']
                    print('Searching in',url)
                    check_products_single_page(url)
              
#function to select category from given list and check product prices.
def choose_category():
    print(" ### To select category choose one of below numbers ###\n")
    print("1.PS4 Games\n2.PS5 Games\n3.Xbox Games\n4.Nintendo Switch Games")

    choosen_category = input()
    choosen_category = int(choosen_category)

    if choosen_category == 1:
        check_multiple_pages_in_category('https://www.ivory.co.il/PS4_Games.html')
    if choosen_category == 2:
        check_multiple_pages_in_category(
            'https://www.ivory.co.il/catalog.php?act=cat&id=36117')
    if choosen_category == 3:
        check_multiple_pages_in_category(
            'https://www.ivory.co.il/catalog.php?act=cat&id=13923')
    if choosen_category == 4:
        check_multiple_pages_in_category(
            'https://www.ivory.co.il/catalog.php?act=cat&id=29338')
    

    
key = input("If you want to get data of specific product & get alert by email when price down press : 1\nIf you want to get data of specific category press : 2\nIf you want to get data by choosing category from a list press : 3\nWaiting for key..")
key=int(key)

if key == 1:
    URL = input('Enter URL Address\nWaiting for URL..')
    required_price = input(Fore.YELLOW + 'Type price when to alert\n' + Style.RESET_ALL)
    if required_price.isnumeric():
        required_price = int(required_price)
    else:
        raise ValueError(Fore.RED + 'required_price is not an int number!' + Style.RESET_ALL)
    
    how_often_to_check_price = input(Fore.YELLOW + 'Set time in seconds to re-check the price of the product\ne.g 1hour=3600seconds\n' + Style.RESET_ALL)
    if how_often_to_check_price.isnumeric():
        how_often_to_check_price = int(how_often_to_check_price)
    else:
        raise ValueError(Fore.RED + "time input is not an number!" + Style.RESET_ALL)
        
    try:
         search = True
         while search:
            search = check_price_of_product_and_notify(URL,required_price)
            time.sleep(how_often_to_check_price)
            
    except:
        print(Fore.RED + "Something went wrong" + Style.RESET_ALL)
        exit(1)
elif key == 2:
    URL = input('Enter URL Address\nWaiting for URL..')
    try:
         check_multiple_pages_in_category(URL)
    except:
        print(Fore.RED + "Something went wrong" + Style.RESET_ALL)
        exit(1)
elif key == 3 :
    try:
     choose_category()
    except:
        print(Fore.RED + "Something went wrong" + Style.RESET_ALL)




