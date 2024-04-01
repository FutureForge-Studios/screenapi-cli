def read_mapping(sitename: str, swap: bool = False) -> dict:
    ecom = {
        "S.No.": "sl",
        "Image": "image",
        "URL": "url",
        "Title": "title",
        "MRP": "mrp",
        "Price": "price",
        "Discount Percentage": "discount",
        "Rating": "productRating",
        "Seller Rating": "sellerRating",
        "UserName": "sellerName",
        "Number of Ratings": "totalRating",
        "Number of Reviews": "totalReview",
        "PID": "pid",
        "LID": "lid",
        "Flipkart Assured": "flipkarAssured",
    }

    social = {
        "S.No.": "sl",
        "Image": "image",
        "Heading": "description",
        "URL": "url",
    }


    match sitename:
        case "ecom":
            if swap:
                return {ecom[key]: key for key in ecom}

            return ecom

        case "social":
            if swap:
                return {social[key]: key for key in social}
            return social



print(read_mapping('social', True)) 