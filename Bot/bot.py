import json
import random as rand
import requests
import names


class Config:
    def __init__(self, json_file):
        file = open(json_file, "r")
        data = json.load(file)
        file.close()
        self.number_of_users = data.get("number_of_users")
        self.max_posts_per_user =data.get("max_posts_per_user")
        self.max_likes_per_user = data.get("max_likes_per_user")


class User:
    IP = "127.0.0.1"
    PORT = "8000"
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    credential = {}
    def __init__(self, config):
        self.config = config

    def get_host(self):
        return f"http://{self.IP}:{self.PORT}"

    def get_header(self):
        headers = {
            "Content-Type": "application/json; charset=utf-8"
            }

        return headers

    def user_generate(self):
        first_name = names.get_first_name()
        last_name = names.get_last_name()
        email = "%s@gmail.com" % ''.join(rand.choice(self.letters) for i in range(10)) 
        password = ''.join(rand.choice(self.letters) for i in range(8))
        re_password = password

        data = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "password": password,
            "re_password": re_password
        }
        return data


    def authentication(self, email, password):
        url = f"{self.get_host()}/api/user/login/"
        headers = self.get_header()
        data = {
            "email": email,
            "password": password
        }
        response = requests.post(url=url, json=data, headers=headers)
        response = response.json()
        return response['token']


    def register_user(self):
        post_instance = Post(self.config)
        print("\n\nSocial Network Automation Bot ...\n\n")
        number_of_users = self.config.number_of_users
        url = f"{self.get_host()}/api/user/"
        headers = self.get_header()

        count = 0
        for user in range(number_of_users):
            data = self.user_generate()
            try:
                response = requests.post(url=url, json=data, headers=headers)
            except Exception as e:
                print(e)
                print(f"{count} %s registered0 successfully" % ("users" if count > 1 else "user"))
                return
            if response.ok:
                email = data['email']
                password = data['password']
                token = self.authentication(email, password)
                self.credential.update({email: token})
                count += 1
                print("%-20s %s" % ("User :", f"{data['first_name']} {data['last_name']}"))
                
                post_instance.post_bot(email)
        print(f"{count} %s registered successfully" % ("users" if count > 1 else "user"))

    def get_user(self):
        url = f"{self.get_host()}/api/user/"
        headers = self.get_header()
        response = requests.get(url=url, headers=headers)
        result = response.json()
        data = []
        data.extend(result['results'])
        while result['next']:
            url = result['next']
            response = requests.get(url=url, headers=headers)
            result = response.json()
            data.extend(result['results'])
        return data



class Post(User):

    def post_generate(self):
        title = ' '.join(names.get_first_name() for i in range(rand.randint(2, 5)))
        description = ' '.join(names.get_first_name() for i in range(rand.randint(5, 10)))
        if rand.random() > 0.6:
            description = "" 

        data = {
            "title": title,
            "description": description
        }
        return data

    def post_bot(self, email):
        number_of_post = rand.randint(0, self.config.max_posts_per_user)
        url = f"{self.get_host()}/api/post/"
        headers = self.get_header()
        token = self.credential.get(email)
        headers.update({"Authorization": f"token {token}"})
        count = 0
        for post in range(number_of_post):
            data = self.post_generate()
            try:
                response = requests.post(url=url, json=data, headers=headers)
            except Exception as e:
                print(e)
                print("%-20s %s\n" % ("Number of Post :", count))
                return
            if response.ok:
                count += 1
        print("%-20s %s\n" % ("Number of Post :", count))


    def check_likes(self, email, post_id):
        url = f"{self.get_host()}/api/post/like/check-like/?id={post_id}"
        headers = self.get_header()
        token = self.credential.get(email)
        headers.update({"Authorization": f"token {token}"})
        response = requests.get(url=url, headers=headers)
        data = response.json()
        return data['result']
    
    def like_post(self, email, post_id):
        url = f"{self.get_host()}/api/post/like/"
        headers = self.get_header()
        token = self.credential.get(email)
        headers.update({"Authorization": f"token {token}"})

        data = {"post_id": post_id}
        response = requests.post(url=url, json=data, headers=headers)
        if response.ok:
            return 1
        return 0

    def get_my_likes(self, email):
        url = f"{self.get_host()}/api/post/like/"
        headers = self.get_header()
        token = self.credential.get(email)
        if not token:
            return {'results': [], 'count': 0}
        headers.update({"Authorization": f"token {token}"})
        response = requests.get(url=url, headers=headers)
        data = response.json()
        return data

    def get_user_post(self, email, user_id):
        if not email in self.credential:
            return []
        url = f"{self.get_host()}/api/post/user/{user_id}/"
        headers = self.get_header()
        token = self.credential.get(email)
        headers.update({"Authorization": f"token {token}"})
        response = requests.get(url=url, headers=headers)
        result = response.json()
        data = []
        data.extend(result['results'])
        while result['next']:
            url = result['next']
            response = requests.get(url=url, headers=headers)
            result = response.json()
            data.extend(result['results'])
        return data
    
    def get_available_posts(self, all_user_post, email):
        available = []
        for user in all_user_post:
            if user == email:
                continue
            for post in all_user_post[user]:
                if post['likes'] == 0:
                    available.append(all_user_post[user])
                    break
        if not available:
            return []

        result = rand.choice(available)
        my_likes = self.get_my_likes(email)['results']
        data = []
        for post in result:
            post_id = post['id']
            for likes in my_likes:
                if likes['id'] == post_id:
                    break
            else:
                data.append(post)
        return data


    def get_available_users(self, users):
        max_likes_per_user = self.config.max_likes_per_user
        available = []
        for user in users:
            email = user['email']
            if not email in self.credential:
                continue
            like_count = self.get_my_likes(email)['count']
            if like_count < max_likes_per_user:
                available.append((like_count, user))
        # available.sort(reverse=True)
        available = sorted(available, key=lambda x: x[0], reverse=True)
        available_user = [user for like_count, user in available]
        return available_user

    def like(self):
        max_likes_per_user = self.config.max_likes_per_user
        users = self.get_user()
        available_users = self.get_available_users(users)
        # posts = self.get_post()
        count = 0
        all_user_post = {}
        for user in users:
            email = user['email']
            all_user_post[email] = self.get_user_post(email, user['id'])


        for user in available_users:
            email = user['email']
            like_count = self.get_my_likes(email)['count']
            while like_count < max_likes_per_user:
                available_posts = self.get_available_posts(all_user_post, email)
                if not available_posts:
                    break
                    # print(f"{count} %s was liked." % ("posts" if count > 1 else "post"))
                    # return
                random_post = rand.choice(available_posts)
                # available_posts.remove(random_post)
                post_id = random_post['id']
                if self.check_likes(email, post_id) == False:
                    success = self.like_post(email, post_id)
                    like_count += success
                    count += success

        print(f"{count} %s was liked." % ("posts" if count > 1 else "post"))


if __name__ == '__main__':
    config_file = "config.json"
    config = Config(config_file)
    bot = User(config)
    bot.register_user() # user register with post

    post = Post(config)
    post.like()

