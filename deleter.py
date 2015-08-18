
import requests
import json
import time

stagger_delay = 0.1
api_token = file("api.token").read().strip()

def main():
    # Who are you?
    iden_r = requests.get("https://slack.com/api/auth.test?token=%s&pretty=1" % api_token)
    iden = json.loads(iden_r.text)

    # Get list of users
    users_r = requests.get("https://slack.com/api/users.list?token=%s&pretty=1" % api_token)
    users = json.loads(users_r.text)["members"]

    # Create dict of users by ID
    users_d = {}
    for i in users:
        users_d[i["id"]] = i

    # Get list of ims
    ims_r = requests.get("https://slack.com/api/im.list?token=%s&pretty=1" % api_token)
    ims = json.loads(ims_r.text)["ims"]

    # Display a list of ims and corresponding users
    # Prompt user to ask which one to delete
    print("List of Direct Chats:")
    count = 1
    for i in ims:
        if i["user"] == "USLACKBOT":
            # Fuck you slackbot
            continue
        u = users_d[i["user"]]
        print("%d. @%s (%s)" % (count, u["name"], u["profile"]["real_name"]))
        count += 1

    choice = int(raw_input("\nPlease select the chat you wish to purge: "))

    chat = ims[choice]

    # Let's get all their messages
    hist_r = requests.get("https://slack.com/api/im.history?token=%s&channel=%s&count=1000&pretty=1" % (api_token, chat["id"]))
    hist = json.loads(hist_r.text)["messages"]

    # Let's inform the user of the statistics:
    ours = []
    for i in hist:
        if i["user"] == iden["user_id"]:
            ours.append(i)
    len_hist = len(hist)
    len_ours = len(ours)
    len_ratio = (float(len_ours)/len_hist)*100
    print("Got %d messages." % len_hist)
    print("%d (%d%%) of that is ours. Delete?" % (len_ours, len_ratio))
    delete_choice = raw_input("y/n: ")

    # Delete
    if delete_choice != "y":
        exit()

    count = 1
    for i in ours:
        time.sleep(stagger_delay)
        requests.get("https://slack.com/api/chat.delete?token=%s&ts=%s&channel=%s&pretty=1" % (api_token, i["ts"], chat["id"]))
        if count % 10 == 0:
            print("Deleted %d messages." % count)
        count += 1

    print("Deleted all your messages!")

if __name__ == "__main__":
    main()
