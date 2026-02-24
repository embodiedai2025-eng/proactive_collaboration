
import pprint


def check_relation(relations):
    res = {}
    object_count = len(relations)
    rule_success = len(relations)

    rule_misplaced = []
    for object in relations.keys():
        if relations[object]['on']:
            for on_obj in relations[object]['on']:
                if 'loor' in on_obj:
                    rule_misplaced.append(object.lower())

    res["misplaced_objects"] = list(relations.keys())

    if rule_misplaced:
        res['rule_success'] = False
        res['rule_misplaced_object'] = rule_misplaced
        rule_success -= len(rule_misplaced)
    else:
        res['rule_success'] = True
        res['rule_misplaced_object'] = []

    success_flag = res['rule_success']
    res['all_misplaced_objects'] = res['rule_misplaced_object']
    all_misplaced_count = len(res['all_misplaced_objects'])
    all_success_count = object_count - all_misplaced_count
    
    return success_flag, rule_success/object_count, all_success_count/object_count, res

    
if __name__ == "__main__":
    relations= {
    "Bread_01": {
    "on": [
        "CounterTop_02"
    ],
    "between": [
        [
        "Sink_02",
        "Walls"
        ]
    ]
    },
    "Newspaper_01": {
    "on": [
        "SideTable_01"
    ],
    "between": [
        [
        "ArmChair_01",
        "HousePlant_01"
        ]
    ]
    },
    "HousePlant_01": {
    "on": [
        "SideTable_01"
    ],
    "between": []
    },
    "Pillow_02": {
    "on": [
        "Floor_01"
    ],
    "between": []
    },
    "AlarmClock_01": {
    "on": [
        "Bed_01"
    ],
    "between": []
        }
    }
  
    
    pprint.pprint(check_relation(relations))