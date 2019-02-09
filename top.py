from operator import itemgetter
from answers import answer

def top_answer(author):
    return author + answer('TOP_SUFFIX')

def top_score(top_collection, author_id, chat_id, author_name):
    score = top_collection.find_one({ 'author_id': author_id, 'chat_id': chat_id })
    if (score is not None):
        top_collection.find_one_and_update({ 'author_id': author_id, 'chat_id': chat_id }, { '$inc': { 'count': 1}})
    else:
        score = {
            'author_id': author_id,
            'author_name': author_name,
            'chat_id': chat_id,
            'count': 1
        }
        top_collection.insert_one(score)

    return top_answer(author_name)

def top_leaderboard(top_collection, chat_id):
    top = top_collection.find({ 'chat_id': chat_id })
    answer_content = 'LEADERBOARD\n'
    top_sorted = sorted(top, key= itemgetter('count'), reverse=True)
    i = 0
    while i < len(top_sorted) and i < 3:
        value = top_sorted[i]
        answer_content += value['author_name'] + '\t [' + str(value['count']) + ']\n'
        i += 1
    
    return answer_content