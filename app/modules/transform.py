def transform(data):
    data = [item.to_dict() for item in data]
    return data

def transform_with_user(data_list):
    results = []
    for item in data_list:
        item_dict = item.to_dict()
        if hasattr(item, 'user') and item.user:
            user_data = item.user.to_dict()
            user_data = {
                'id': item.user.id,
                'name': item.user.name,
                'email': item.user.email
            }
            
            item_dict['user'] = user_data
        else:
            item_dict['user'] = None
        results.append(item_dict)
    return results