def transform_data(data_list, relations=None):
    if relations is None:
        relations = {}

    results = []

    for item in data_list:
        item_dict = item.to_dict()

        for relation_name, fields in relations.items():
            if hasattr(item, relation_name):
                related_obj = getattr(item, relation_name)
                
                if related_obj is not None:
                    # KASUS 1: Jika user minta field tertentu (custom fields)
                    if fields:
                        # Jika related_obj adalah LIST (One-to-Many, misal: items)
                        if isinstance(related_obj, list):
                            rel_data_list = []
                            for obj in related_obj:
                                temp = {}
                                for field in fields:
                                    temp[field] = getattr(obj, field, None)
                                rel_data_list.append(temp)
                            item_dict[relation_name] = rel_data_list
                        
                        # Jika related_obj adalah SINGLE OBJECT (Many-to-One, misal: user)
                        else:
                            rel_data = {}
                            for field in fields:
                                rel_data[field] = getattr(related_obj, field, None)
                            item_dict[relation_name] = rel_data
                    
                    # KASUS 2: Jika user minta SEMUA field (list kosong [])
                    else:
                        # --- PERBAIKAN DI SINI ---
                        
                        # Cek apakah related_obj adalah LIST (seperti items)
                        if isinstance(related_obj, list):
                            # Loop dan jalankan to_dict() untuk setiap item di dalam list
                            item_dict[relation_name] = [
                                obj.to_dict() if hasattr(obj, 'to_dict') else str(obj) 
                                for obj in related_obj
                            ]
                        
                        # Cek apakah related_obj adalah Single Object (seperti user/product)
                        elif hasattr(related_obj, 'to_dict'):
                            item_dict[relation_name] = related_obj.to_dict()
                        
                        else:
                            # Fallback jika bukan list dan gak punya to_dict
                            item_dict[relation_name] = str(related_obj)
                else:
                    item_dict[relation_name] = None
            
        results.append(item_dict)

    return results