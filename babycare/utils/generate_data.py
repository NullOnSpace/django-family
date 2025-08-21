import json
import datetime
import random
import zoneinfo


def generate_feeding_data():
    feedings = list()
    # 最近20天内 每隔约3小时一条记录 喂养量在60到120毫升之间
    for i in range(20):
        date = datetime.datetime.now(tz=zoneinfo.ZoneInfo("Asia/Shanghai")) - datetime.timedelta(days=i)
        for j in range(8):  # 每天8次喂养
            record = dict()
            record['model'] = 'babycare.feeding'
            record['pk'] = i * 8 + j + 1
            record['fields'] = fields = dict()
            fields['baby_date'] = 1  # 假设第一个宝宝
            fields['date'] = (date + datetime.timedelta(hours=j * 3)).isoformat()
            fields['amount'] = round(random.uniform(60, 120), 2)  # 喂养量在60到120毫升之间
            fields['note'] = f"喂养记录 {i * 8 + j + 1}"
            feedings.append(record)
    
    with open('output/feedings.json', 'w') as f:
        json.dump(feedings, f, ensure_ascii=False, indent=4)

def generate_body_temperature_data():
    bts = list()
    # 最近20天内 每天3次测温
    for i in range(20):
        date = datetime.datetime.now(tz=zoneinfo.ZoneInfo("Asia/Shanghai")) - datetime.timedelta(days=i)
        for j in range(3):
            record = dict()
            record['model'] = 'babycare.bodytemperature'
            record['pk'] = i * 3 + j + 1
            record['fields'] = fields = dict()
            fields['baby_date'] = 1  # 假设第一个宝宝
            fields['date'] = (date + datetime.timedelta(hours=j * 8)).isoformat()
            fields['temperature'] = round(random.uniform(36.5, 36.9), 1)
            fields['measurement'] = random.choice(['temporal', 'tympanic', 'axillary'])
            fields['notes'] = f"测温 {i * 3 + j + 1}"
            bts.append(record)
    
    with open('output/_body_temperatures.json', 'w') as f:
        json.dump(bts, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    generate_body_temperature_data()
    print("Data generated successfully.")