def user_by_user(user_one, user_two):
    if user_one != user_two:
        return False
    else:
        return True


def check_bid_count(bid_one, bid_two):
    if float(bid_one) > float(bid_two):
        return True
    else:
        return False

def get_max_bid(bids):
    return max(bids, default=0)