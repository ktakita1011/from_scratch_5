import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import os

# GitHub Personal Access Token
load_dotenv()
token = os.getenv('GITHUB_TOKEN')

# リポジトリ情報
owner = 'ktakita1011'
repo = 'from_scratch_5'

headers = {
    'Authorization': f'token {token}',
    'Accept': 'application/vnd.github.v3+json',
}

url = f'https://api.github.com/repos/{owner}/{repo}/discussions'

discussions = []

while url:
    response = requests.get(url, headers=headers)
    data = response.json()
    
    for discussion in data:
        reactions_total = discussion['reactions'].get('total_count', 0)
        
        # ディスカッションの投稿を取得
        comments_url = f"https://api.github.com/repos/{owner}/{repo}/discussions/{discussion['number']}/comments"
        comments_response = requests.get(comments_url, headers=headers)
        comments_data = comments_response.json()
        
        # 投稿内容を文字列として結合
        comments_content = "\n\n".join([f"Author: {comment['user']['login']}\nCreated at: {comment['created_at']}\n{comment['body']}" for comment in comments_data])
        
        discussion_info = {
            'id': discussion['id'],
            'title': discussion['title'],
            'body': discussion['body'],
            'html_url': discussion['html_url'],
            'created_at': discussion['created_at'],
            'updated_at': discussion['updated_at'],
            'author': discussion['user']['login'],
            'author_url': discussion['user']['html_url'],
            'category': discussion['category']['name'],
            'comments_count': discussion['comments'],
            'reactions_count': reactions_total,
            'labels': ', '.join([label['name'] for label in discussion.get('labels', [])]),
            'state': discussion['state'],
            'number': discussion['number'],
            'comments_content': comments_content
        }
        discussions.append(discussion_info)
    
    url = response.links.get('next', {}).get('url')

df = pd.DataFrame(discussions)

# 日付列を読みやすい形式に変換
for col in ['created_at', 'updated_at']:
    df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d %H:%M:%S')

# CSVファイル名に現在の日時を追加
current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
csv_filename = f'github_discussions_{current_time}.csv'

df.to_csv(csv_filename, index=False, encoding='utf-8-sig')

print(f"Discussions exported to {csv_filename}")