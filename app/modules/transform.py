def transform_data(data_list, relations=None):
    """
    data_list: List objek dari database (misal: pagination.items)
    relations: Dictionary konfigurasi. 
                Format: {'nama_relasi': ['field1', 'field2']}
                Jika valuenya None atau [], maka akan mengambil seluruh data (to_dict).
    """
    if relations is None:
        relations = {}

    results = []

    for item in data_list:
        # 1. Ambil data utama (misal: Transaksi)
        item_dict = item.to_dict()

        # 2. Loop melalui relasi yang diminta (misal: 'user', 'haircut')
        for relation_name, fields in relations.items():
            
            # Cek apakah item punya relasi tersebut (misal: item.user)
            if hasattr(item, relation_name):
                related_obj = getattr(item, relation_name) # Ambil objeknya
                
                if related_obj:
                    # Jika user mendefinisikan field spesifik (misal: ['name', 'email'])
                    if fields:
                        rel_data = {}
                        for field in fields:
                            # Ambil nilai field dari related_obj
                            # getattr(obj, 'name', None) -> aman jika field tidak ada
                            rel_data[field] = getattr(related_obj, field, None)
                        item_dict[relation_name] = rel_data
                    
                    # Jika user tidak mendefinisikan field (ambil semua via to_dict)
                    else:
                        if hasattr(related_obj, 'to_dict'):
                            item_dict[relation_name] = related_obj.to_dict()
                        else:
                            # Fallback jika tidak ada to_dict, ambil string representasi
                            item_dict[relation_name] = str(related_obj)
                else:
                    # Jika relasi ada tapi datanya kosong (None)
                    item_dict[relation_name] = None
            
        results.append(item_dict)

    return results