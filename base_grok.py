import os
from groq import Groq
from web_scraping import extract_text, get_urls
import re
client = Groq(
    api_key="Enter Your GROK API HERE",
)

def generate_response(query, model, temperature, max_tokens):

    urls = get_urls(query)
    data = extract_text(urls)
    message = [
        {
        "role": "system",
        "content":
            "Generate a comprehensive and informative answer (but no more than 256 words in 2 paragraphs) for a given question solely based on the provided web Search Results (URL and Summary)." +
            "You must only use information from the provided search results." +
            "Use an unbiased and journalistic tone." +
            "Combine search results together into a coherent answer." +
            "Do not repeat text. Cite search results using {number} notation." +
            "Only cite the most relevant results that answer the question accurately." +
            "If different results refer to different entities with the same name, write separate answers for each entity." +
            "You have the ability to search and will be given websites and the scraped chat_data from them and you will have to make up an answer with that only" +
            "You must must provide citations in the format of {number} and it starts with {1}." +
            "You can only cite one source at a time. Don't cite multiple source for same content."
        },
        {
            "role": "user",
            "content": "{chat_data}\n\nQuestion: {query}",
        }
    ]

    message[1]["content"] = message[1]["content"].format(chat_data=data, query=query)

    chat_completion = client.chat.completions.create(
        messages=message,
        temperature=temperature,
        #max_tokens = max_tokens,
        model=model
    )
    response = chat_completion.choices[0].message.content
    regex = r"{([0-9]+)}"
    matches = set(re.findall(r"{([0-9]+)}", response))
    for match in matches:
        new = '{' + str(match) + '}'
        returned = '[' + str(match) + ']' + '(' + urls[int(match) - 1] + ')'
        response = response.replace(new, returned)

    return response, urls





def generate_chat_response(query, chat_hist, model, temperature, max_tokens):

    message = [
        {
        "role": "system",
        "content":
            "You need to build the search query based on the past chat history and current user query that can be feeded to search engine" +
            "Try to get the context from the past chat history based on user current query." +
            "If you dont find any context in past chat history then just return current query as search query. " +
            "Please return the search query in []"

        },
        {
            "role": "user",
            "content": f"{chat_hist}\n\nCurrent User Query: {query}",
        }
    ]
   # message[1]["content"] = message[1]["content"].format(chat_data=chat_data, query=query)
   #  print(message)
    chat_completion = client.chat.completions.create(
        messages=message,
        temperature=temperature,
        #max_tokens = max_tokens,
        model=model
    )
    response = chat_completion.choices[0].message.content
    print(response)
    match = re.search(r'\[(.*?)\]', response)
    query2 = match.group(1) if match else ""
    response, urls = generate_response(query2, model, temperature, max_tokens)
    return response, urls


# hist = """Past Chat History
# user
# surat is famous for which food items
#
# Assistant
# According to the search results, Surat is famous for its street food, particularly the following items:
#
# 1. Sev Tamatar - a delicious snack made of tomatoes, sev, and a mouth-watering spice mixture [1](https://blog.swiggy.com/2023/12/24/do-not-miss-out-on-these-10-must-try-street-food-items-in-surat/#:~:text=Ans.,budget%2Dfriendly%2C%20and%20accessible.).
# 2. Locho - a popular street food in Surat and the whole of Gujarat, defined as steamed Gujarati farsan {1, 2, 3}.
# 3. Anda Ghotala - an ideal mix of eggs and pav bhaji masala, one of the most famous street foods in Surat [1](https://blog.swiggy.com/2023/12/24/do-not-miss-out-on-these-10-must-try-street-food-items-in-surat/#:~:text=Ans.,budget%2Dfriendly%2C%20and%20accessible.).
# 4. Ghari - a delicious sweet dish of Surat, prepared in pure ghee and stuffed with an assortment of dry fruits {1, 3}.
# 5. Khaman - a popular steamed snack made from fermented gram flour, a staple food in Surat {2, 3}.
# 6. Dhokla - a soft and fluffy cake made from fermented rice and lentil batter, a popular snack or light meal in Surat [3](https://www.foodchow.com/blog/surat-top-10-delicious-street-foods/).
# 7. Undhiyu - a popular dish in Surat, made with a variety of vegetables and spices [2](https://g3fashion.com/blog/facts-talks/15-street-food-of-surat/).
# 8. Ponk Wada - a popular street food in Surat, made with ponk (a type of grain) and spices [2](https://g3fashion.com/blog/facts-talks/15-street-food-of-surat/).
# 9. Shev Madhi - a popular street food in Surat, made with sev and a variety of spices [2](https://g3fashion.com/blog/facts-talks/15-street-food-of-surat/).
# 10. Khichyu - a popular street food in Surat, made with a variety of ingredients including gram flour, spices, and vegetables [2](https://g3fashion.com/blog/facts-talks/15-street-food-of-surat/).
# 11. Tomato Bhajiya - a popular street food in Surat, made with tomatoes and spices [2](https://g3fashion.com/blog/facts-talks/15-street-food-of-surat/).
# 12. Cold Coco - a popular dessert in Surat, made with coconut and spices [2](https://g3fashion.com/blog/facts-talks/15-street-food-of-surat/).
# 13. Bhel Puri - a popular street food in Surat, made with puffed rice, onions, tomatoes, and spices [3](https://www.foodchow.com/blog/surat-top-10-delicious-street-foods/).
# 14. Dabeli - a popular street food in Surat, made with pav, dabeli masala, and a variety of toppings [3](https://www.foodchow.com/blog/surat-top-10-delicious-street-foods/).
# 15. Khakhra - a popular street food in Surat, made with a variety of ingredients including gram flour, spices, and vegetables [3](https://www.foodchow.com/blog/surat-top-10-delicious-street-foods/).
#
# These are just a few examples of the many delicious street food items that Surat is famous for.
# """


# hist = """Past Chat History
# user
# surat is famous for which food items
#
# Assistant
# According to the search results, Surat is famous for its street food, particularly Gujarati cuisine.
# Some of the must-try street food items in Surat include Sev Tamatar, Locho, Anda Ghotala, Ghari, Khaman, Dhokla, Jalebi & Fafda,
# Dhokla Sandwich, Vada Pav, Dabeli, Khakhra, and Bhel Puri 1. Locho, a popular street food in Surat, is a spongy,
# steamed bread made from fermented gram flour, typically served with a spicy green chutney and crispy sev 2. Surat's street
# food scene is particularly vibrant in the evening, with numerous roadside stalls serving a wide variety of cuisines,
# from savory snacks to sweet desserts 3.
# """
# query = 'who is the current MP of the above mentioned city?'
#
# print(generate_chat_response(query, hist, "llama3-70b-8192", 0.2, 20))


