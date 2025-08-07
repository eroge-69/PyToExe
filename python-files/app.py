import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
from sklearn.decomposition import TruncatedSVD
import warnings
from fuzzywuzzy import process
from fuzzywuzzy import fuzz
import importfile



###############--------code for Dataset import and Data Preprocessing-------------###################

###############--------End for Dataset import and Data Preprocessing-------------###################


def get_recommendation(book_name):
    coffey_hands = importfile.us_canada_book_list.index(book_name)
    corr_coffey_hands  = importfile.corr[coffey_hands]
    list(importfile.us_canada_book_title[(corr_coffey_hands > 0.9)])
    return list(importfile.us_canada_book_title[(corr_coffey_hands > 0.9)])

def get_image_url(book_title):
    book_entry = importfile.books[importfile.books['bookTitle'] == book_title]
    if not book_entry.empty:
        return book_entry.iloc[0]['imageUrlL']
    return None

def search_books(query,book_list=importfile.us_canada_book_list,threshold=80):


    # Check for the presence of all keywords in each book title
    matches = process.extract(query, book_list, limit=len(book_list), scorer=fuzz.partial_ratio)
    return [match[0] for match in matches if match[1] >= threshold]

def main():
    st.title("Book Recommendation System Using Matrix Factorization")

    book_name = st.text_input("Enter Book Title")
    if st.button("Search") or book_name:
        try:
            recommended_books = get_recommendation(book_name)
            st.write("Recommended Books:")
            # Iterating over the books two at a time
            for i in range(0, len(recommended_books), 2):
                book1 = recommended_books[i]
                image_url1 = get_image_url(book1)
                
                # Check if there's a next book
                book2 = recommended_books[i + 1] if i + 1 < len(recommended_books) else None
                image_url2 = get_image_url(book2) if book2 else None

                col1, col2 = st.columns(2)

                if image_url1:
                    col1.success(book1)
                    col1.image(image_url1,width=250)

                if book2 and image_url2:
                    col2.success(book2)
                    col2.image(image_url2,width=250)
        except:
            st.warning("There is no Book with This Title. Write the Book Title Correctly")
            matched_books = search_books(book_name)
            st.success("Possible Title for a Book. Attempt with One of Them")
            for book in matched_books:
                st.write(book)
            




if __name__ == "__main__":
    main()