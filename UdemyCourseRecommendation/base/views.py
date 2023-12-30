from django.shortcuts import render
from pickle import load
import pandas as pd

def recommend_course(title, numrec):
    with open('./savedmodels/df.pkl', 'rb') as g:
        df = load(g)
    with open('./savedmodels/cosine_sim_mat.pkl', 'rb') as h:
        cosine_mat = load(h)

    course_index = pd.Series(df.index, index=df['course_title']).drop_duplicates()
    index = course_index[title]

    scores = list(enumerate(cosine_mat[index]))
    sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)

    selected_course_index = [i[0] for i in sorted_scores[1:]]
    selected_course_score = [i[1] for i in sorted_scores[1:]]

    rec_df = df.iloc[selected_course_index]
    rec_df['Similarity_Score'] = selected_course_score

    final_recommended_courses = rec_df[['course_title', 'Similarity_Score', 'url', 'price', 'num_subscribers']]

    return final_recommended_courses.head(numrec)

def search_term(term):
    with open('./savedmodels/df.pkl', 'rb') as g:
        df = load(g)
    result_df = df[df['course_title'].str.contains(term, case=False)]
    top_6 = result_df.sort_values(by='num_subscribers', ascending=False).head(6)
    return top_6

def extract_features(rec_df):
    course_url = list(rec_df['url'])
    course_title = list(rec_df['course_title'])
    course_price = list(rec_df['price'])

    return course_url, course_title, course_price

def welcome(request):
    if request.method == 'POST':
        try:
            my_dict = request.POST
            title_name = my_dict['course']

            num_rec = 6

            rec_df = recommend_course(title_name, num_rec)
            course_url, course_title, course_price = extract_features(rec_df)

            dict_map = dict(zip(course_title, course_url))

            if dict_map:
                return render(request, 'index.html', {'coursemap': dict_map, 'coursename': title_name, 'showtitle': True})
            else:
                return render(request, 'index.html', {'showerror': True, 'coursename': title_name})
        except Exception as e:
            print(e)
            result_df = search_term(title_name)
            if result_df.shape[0] > 6:
                result_df = result_df.head(6)
            course_url, course_title, course_price = extract_features(result_df)
            course_map = dict(zip(course_title, course_url))
            if course_map:
                return render(request, 'index.html', {'coursemap': course_map, 'coursename': title_name, 'showtitle': True})
            else:
                return render(request, 'index.html', {'showerror': True, 'coursename': title_name})

    return render(request, 'index.html')
